#!/usr/bin/env python3
"""Server-side 2-GPU evaluation queue. Original generation and metric code are reused."""
import argparse
import csv
import io
import json
import math
import multiprocessing as mp
import os
import queue
import re
import subprocess
import sys
import time
import traceback
import zipfile
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo


def now():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False))
    os.replace(temp, path)


def valid_raw(job):
    p = Path(job['raw_path'])
    if not p.is_file():
        return False
    try:
        with zipfile.ZipFile(p) as z:
            return 'name2reason.npy' in z.namelist() and z.testzip() is None
    except (OSError, zipfile.BadZipFile):
        return False


def valid_score(job):
    try:
        x = json.loads(Path(job['score_path']).read_text())
        return x['job_id'] == job['id'] and math.isfinite(x['main_score'])
    except (OSError, ValueError, KeyError, TypeError):
        return False


def configure_worker(plan, variant):
    os.chdir(plan['project'])
    sys.path.insert(0, plan['project'])
    os.environ['CUDA_VISIBLE_DEVICES'] = str(plan['runs'][variant]['gpu'])
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['OMP_NUM_THREADS'] = '2'
    os.environ['MKL_NUM_THREADS'] = '2'
    os.environ['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'
    for k in ('RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'SLURM_PROCID'):
        os.environ.pop(k, None)


def event(events, variant, stage, lane, **kwargs):
    events.put({'time': now(), 'variant': variant, 'stage': stage,
                'lane': lane, 'pid': os.getpid(), **kwargs})


def raw_worker(plan, variant, lane, jobs, events):
    configure_worker(plan, variant)
    run = plan['runs'][variant]
    while True:
        job = jobs.get()
        if job is None:
            return
        if valid_raw(job):
            event(events, variant, 'raw', lane, job_id=job['id'], status='generated', cached=True)
            continue
        target = Path(job['raw_path'])
        if target.exists():
            # Only an incomplete file in this new batch's own output tree is removed.
            assert str(target.resolve()).startswith(plan['batch'] + '/')
            target.unlink()
        log = Path(plan['batch']) / 'logs' / variant / 'raw' / (job['id'] + '.log')
        log.parent.mkdir(parents=True, exist_ok=True)
        command = [plan['python'], '-B', '-u', 'inference_hybird.py', '--zeroshot',
                   '--dataset=' + job['dataset'], '--cfg-path=' + run['config'], '--options',
                   'inference.gpu=0', 'inference.ckpt_root=' + run['run_dir'],
                   'inference.test_epoch=' + str(job['epoch']),
                   'inference.base_root=' + str(Path(plan['batch']) / variant / 'results')]
        succeeded = False
        for attempt in range(1, 3):
            event(events, variant, 'raw', lane, job_id=job['id'], status='running_raw',
                  attempt=attempt, log=str(log), samples=job['samples'])
            with log.open('a', buffering=1) as stream:
                stream.write('\nQUEUE_START ' + json.dumps({'time': now(), 'attempt': attempt,
                                                           'command': command}) + '\n')
                result = subprocess.run(command, cwd=plan['project'], env=os.environ.copy(),
                                        stdout=stream, stderr=subprocess.STDOUT)
                stream.write('\nQUEUE_END ' + json.dumps({'time': now(), 'returncode': result.returncode}) + '\n')
            if result.returncode == 0 and valid_raw(job):
                succeeded = True
                break
            if target.exists() and not valid_raw(job):
                target.unlink()
        event(events, variant, 'raw', lane, job_id=job['id'],
              status='generated' if succeeded else 'failed_raw', log=str(log))


def build_judge(plan):
    import evaluation
    # Use the repository loader verbatim, including all vLLM defaults.
    return evaluation.func_read_batch_calling_model('Qwen25')


def score_one(plan, job, evaluation, judge, datasets):
    llm, tokenizer, params = judge
    dataset = job['dataset']
    if dataset not in datasets:
        cls = evaluation.get_dataset2cls(dataset)
        truth = cls.get_test_name2gt()
        if evaluation.get_discrete_or_dimension_flag(dataset) == 'discrete':
            _, idx2emo = evaluation.get_emo2idx_idx2emo(cls)
            truth = {name: label if isinstance(label, str) else idx2emo[label]
                     for name, label in truth.items()}
        datasets[dataset] = truth
    truth = datasets[dataset]
    kind = evaluation.get_discrete_or_dimension_flag(dataset)
    path = job['raw_path']
    if kind == 'discrete':
        primary, _ = evaluation.calculate_discrete_zeroshot(path, truth, llm, tokenizer, params, True)
        metrics = {'HIT': float(primary)}
        metric_name = 'HIT'
    elif kind == 'dimension':
        primary, accuracy = evaluation.calculate_dimension_zeroshot(path, truth, llm, tokenizer, params, True)
        metrics = {'WAF': float(primary), 'ACC': float(accuracy)}
        metric_name = 'WAF'
    else:
        primary, precision, recall = evaluation.calculate_ov_zeroshot(path, truth, llm, tokenizer, params, True)
        metrics = {'F_s': float(primary), 'P_s': float(precision), 'R_s': float(recall)}
        metric_name = 'F_s'
    assert all(math.isfinite(v) for v in metrics.values()), metrics
    return {'job_id': job['id'], 'variant': job['variant'], 'gpu': job['gpu'],
            'epoch': job['epoch'], 'dataset': dataset, 'samples': job['samples'],
            'ground_truth_records': len(truth), 'checkpoint': job['checkpoint'],
            'raw_path': path, 'main_metric': metric_name, 'main_score': float(primary),
            'metrics': metrics, 'completed_at': now(),
            'protocol': 'Repository per-checkpoint functions; original Qwen prompts and wheel resources.'}


def score_worker(plan, variant, lane, jobs, events):
    # The live controller was started with three score lanes. Extra lanes exit
    # before importing evaluation or allocating a judge; lane 0 drains the queue.
    if lane != 0:
        return
    configure_worker(plan, variant)
    # This GPU starts scoring immediately after its own inference queue finishes.
    log = Path(plan['batch']) / 'logs' / variant / ('score_lane_' + str(lane) + '.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('a', buffering=1) as stream:
        os.dup2(stream.fileno(), 1)
        os.dup2(stream.fileno(), 2)
        try:
            import evaluation
            event(events, variant, 'score', lane, status='loading_judge', log=str(log))
            judge = build_judge(plan)
            datasets = {}
            while True:
                job = jobs.get()
                if job is None:
                    return
                if valid_score(job):
                    event(events, variant, 'score', lane, job_id=job['id'], status='done', cached=True)
                    continue
                succeeded = False
                for attempt in range(1, 3):
                    event(events, variant, 'score', lane, job_id=job['id'], status='running_score',
                          attempt=attempt, log=str(log), samples=job['samples'])
                    try:
                        print('SCORE_START', json.dumps(job, ensure_ascii=False), flush=True)
                        result = score_one(plan, job, evaluation, judge, datasets)
                        atomic_json(job['score_path'], result)
                        print('SCORE_DONE', json.dumps(result, ensure_ascii=False), flush=True)
                        succeeded = True
                        break
                    except Exception as error:
                        traceback.print_exc()
                        event(events, variant, 'score', lane, job_id=job['id'],
                              status='score_retry', error=repr(error), attempt=attempt, log=str(log))
                event(events, variant, 'score', lane, job_id=job['id'],
                      status='done' if succeeded else 'failed_score', log=str(log))
        except Exception as error:
            traceback.print_exc()
            event(events, variant, 'score', lane, status='worker_failed', error=repr(error), log=str(log))
            raise


def summarize(plan):
    rows = []
    for job in plan['jobs']:
        if valid_score(job):
            rows.append(json.loads(Path(job['score_path']).read_text()))
    columns = ['variant', 'gpu', 'epoch', 'dataset', 'samples', 'main_metric',
               'main_score', 'HIT', 'WAF', 'ACC', 'F_s', 'P_s', 'R_s', 'completed_at']
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in sorted(rows, key=lambda x: (x['variant'], x['epoch'], x['dataset'])):
        flat = {k: row.get(k, '') for k in columns}
        flat.update(row['metrics'])
        writer.writerow(flat)
    final = Path(plan['batch']) / 'metrics_all.csv'
    temp = final.with_suffix('.csv.tmp')
    temp.write_text(output.getvalue())
    os.replace(temp, final)
    means = []
    for variant in plan['runs']:
        for epoch in plan['epochs']:
            chosen = [r for r in rows if r['variant'] == variant and r['epoch'] == epoch]
            means.append({'variant': variant, 'epoch': epoch, 'datasets_completed': len(chosen),
                          'dataset_wise_mean': sum(r['main_score'] for r in chosen) / 9 if len(chosen) == 9 else None,
                          'scores': {r['dataset']: r['main_score'] for r in chosen}})
    atomic_json(Path(plan['batch']) / 'per_checkpoint_summary.json', means)
    return rows


def spawn_group(context, plan, variant, stage, candidates, events, concurrency):
    jobs = context.Queue()
    for job in sorted(candidates, key=lambda x: (-x['samples'], -x['epoch'], x['dataset'])):
        jobs.put(job)
    for _ in range(concurrency):
        jobs.put(None)
    function = raw_worker if stage == 'raw' else score_worker
    processes = []
    for lane in range(concurrency):
        process = context.Process(target=function, args=(plan, variant, lane, jobs, events),
                                  name=variant + '_' + stage + '_' + str(lane))
        process.start()
        processes.append(process)
    return {'stage': stage, 'processes': processes, 'queue': jobs, 'pass': 0}


def controller(plan):
    import fcntl
    lock = (Path(plan['batch']) / 'controller.lock').open('a')
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    context = mp.get_context('spawn')
    events = context.Queue()
    state = {'created_at': now(), 'updated_at': now(), 'controller_pid': os.getpid(),
             'status': 'running', 'batch': plan['batch'], 'gpu_stages': {}, 'jobs': {}}
    groups = {}
    for variant in plan['runs']:
        candidates = [j for j in plan['jobs'] if j['variant'] == variant and not valid_raw(j)]
        for j in [j for j in plan['jobs'] if j['variant'] == variant]:
            state['jobs'][j['id']] = {'status': 'done' if valid_score(j) else 'generated' if valid_raw(j) else 'pending_raw'}
        groups[variant] = spawn_group(context, plan, variant, 'raw', candidates, events, 3)
        state['gpu_stages'][variant] = 'raw'
    last_refresh = 0
    while groups:
        try:
            item = events.get(timeout=2)
            with (Path(plan['batch']) / 'events.jsonl').open('a') as stream:
                stream.write(json.dumps(item, ensure_ascii=False) + '\n')
            if 'job_id' in item:
                state['jobs'][item['job_id']] = item
            print(json.dumps(item, ensure_ascii=False), flush=True)
        except queue.Empty:
            pass
        for variant in list(groups):
            group = groups[variant]
            if any(p.is_alive() for p in group['processes']):
                continue
            for process in group['processes']:
                process.join()
            stage = group['stage']
            candidates = [j for j in plan['jobs'] if j['variant'] == variant]
            if stage == 'raw':
                missing = [j for j in candidates if not valid_raw(j)]
                if missing and group['pass'] == 0:
                    # One serial recovery pass also covers a process terminated before its final event.
                    groups[variant] = spawn_group(context, plan, variant, 'raw', missing, events, 1)
                    groups[variant]['pass'] = 1
                    continue
                scoring = [j for j in candidates if valid_raw(j) and not valid_score(j)]
                if not scoring:
                    state['gpu_stages'][variant] = 'completed' if all(valid_score(j) for j in candidates) else 'needs_attention'
                    del groups[variant]
                    continue
                groups[variant] = spawn_group(context, plan, variant, 'score', scoring, events, 1)
                state['gpu_stages'][variant] = 'score'
            else:
                missing = [j for j in candidates if valid_raw(j) and not valid_score(j)]
                if missing and group['pass'] == 0:
                    groups[variant] = spawn_group(context, plan, variant, 'score', missing, events, 1)
                    groups[variant]['pass'] = 1
                    continue
                state['gpu_stages'][variant] = 'completed' if all(valid_score(j) for j in candidates) else 'needs_attention'
                del groups[variant]
                summarize(plan)
        if time.time() - last_refresh > 10:
            state['updated_at'] = now()
            state['worker_pids'] = {v: [p.pid for p in g['processes'] if p.is_alive()] for v, g in groups.items()}
            state['counts'] = dict(__import__('collections').Counter(v['status'] for v in state['jobs'].values()))
            atomic_json(Path(plan['batch']) / 'state.json', state)
            last_refresh = time.time()
    # Reconcile authoritative artifacts after draining workers; final events can lag process exit.
    for job in plan['jobs']:
        state['jobs'][job['id']]['status'] = 'done' if valid_score(job) else 'failed_score' if valid_raw(job) else 'failed_raw'
    state['counts'] = dict(__import__('collections').Counter(x['status'] for x in state['jobs'].values()))
    rows = summarize(plan)
    missing = [j['id'] for j in plan['jobs'] if not valid_score(j)]
    state.update(status='completed' if not missing else 'needs_attention', updated_at=now(),
                 completed_evaluations=len(rows), expected_evaluations=len(plan['jobs']), missing_jobs=missing)
    atomic_json(Path(plan['batch']) / 'state.json', state)
    atomic_json(Path(plan['batch']) / ('COMPLETED.json' if not missing else 'ATTENTION.json'), state)
    print(json.dumps({'event': 'PIPELINE_FINISHED', 'time': now(), 'completed': len(rows), 'missing': missing}), flush=True)


def smoke(plan, variant):
    configure_worker(plan, variant)
    import evaluation
    from toolkit.utils.qwen import reason_to_openset_qwen
    judge = build_judge(plan)
    llm, tokenizer, params = judge
    labels = reason_to_openset_qwen(llm=llm, tokenizer=tokenizer, sampling_params=params,
                                  batch_reasons=['The character sounds angry and frustrated.'])
    print('SMOKE_LABELS', labels, flush=True)
    assert len(labels) == 1
    print('SMOKE_OK', now(), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--mode', choices=['run', 'status', 'smoke'], default='run')
    parser.add_argument('--variant', choices=['face', 'frame'], default='face')
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text())
    if args.mode == 'status':
        print((Path(plan['batch']) / 'state.json').read_text())
    elif args.mode == 'smoke':
        smoke(plan, args.variant)
    else:
        controller(plan)


if __name__ == '__main__':
    main()
