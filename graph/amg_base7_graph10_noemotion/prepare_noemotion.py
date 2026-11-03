"""Prepare Cue+Appraisal inference from the completed 10-emotion baseline run.

Only the two emotion-bearing prompt blocks are removed. Cue and Appraisal text
is produced by the same formatter from the same cached graph evidence.
"""
import copy, datetime
from zoneinfo import ZoneInfo
from graph_paths import Path
from amg_runtime.common import read, sha, canonical, atomic_json as dump
from .run import ROOT, now

BASE = ROOT / 'amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105'
STAMP = datetime.datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')
RUN = ROOT / 'amg_base7_graph10_noemotion/runs' / ('base7_noemotion_' + STAMP)

DIRS = ['inputs', 'shards', 'jobs', 'predictions', 'workers', 'scores',
        'evaluation_jobs', 'validation']


def main():
    old = read(BASE / 'plan.json')
    for d in DIRS:
        (RUN / d).mkdir(parents=True, exist_ok=True)
    dump(ROOT / 'amg_base7_graph10_noemotion/preparing.json',
         dict(run=str(RUN), base_run=str(BASE), state='preparing'))
    dump(RUN / 'prepare_status.json', dict(state='preparing', time_beijing=now()))
    try:
        p = copy.deepcopy(old)
        p.pop('plan_id', None)
        p.update(
            schema='native_original_plus_graph10_noemotion_v1',
            created_at_beijing=now(),
            training_run=str(RUN),
            variant='CueAppraisal_noEmotion',
            previous_run=str(BASE),
            graph_cache_directory=str(Path(old['graph_cache_directory'])),
            graph_cache_plan_id=old['graph_cache_plan_id'],
            semantics=('Native inference_hybird.py sample loop, original readers/model/Chat/'
                       'generation. Reuse the frozen graph10 query cache; remove only the '
                       'Emotion hypotheses and Supporting links lines from the evidence text. '
                       'Cue and Appraisal lines are otherwise unchanged. No training, no '
                       'target graph fitting, no polarity head.'),
            protected_files={},
        )
        p['policy'] = copy.deepcopy(old['policy'])
        p['policy'].update(
            version='bcd_evidence_noemotion_v1',
            evidence_blocks=['cue', 'appraisal'],
            emotion_nodes=False,
            removed_prompt_blocks=['Emotion hypotheses:', 'Supporting links:'],
            change_scope='single-variable prompt ablation',
        )

        (RUN / 'original_config.json').write_bytes((BASE / 'original_config.json').read_bytes())

        for d, spec in p['datasets'].items():
            rows = read(spec['path'])
            dest = RUN / 'inputs' / (d + '.json')
            dump(dest, rows)
            spec.update(path=str(dest), sha256=sha(dest))

        for name in ['cache_inventory.json', 'cache_manifest.json',
                     'native_contract_test.json', 'native_dataset_audit.json']:
            (RUN / name).write_bytes((BASE / name).read_bytes())

        levels = read(BASE / 'cache_manifest.json')['evidence_levels']
        affected = {}
        for f in Path(old['graph_cache_directory']).glob('*.json'):
            item = read(f)
            info = item.get('format_info', {})
            if info.get('evidence_level') == 3:
                affected[item['sample_id']] = dict(
                    evidence_level=3,
                    emotion_candidates=info.get('emotion_candidates_displayed'),
                    displayed_paths=info.get('displayed_paths'),
                    baseline_graph_tokens=info.get('graph_tokens'),
                    baseline_graph_text_sha256=canonical(item.get('graph_text', '')),
                )
        dump(RUN / 'affected_level3_samples.json', affected)
        dump(RUN / 'prompt_policy.json', dict(
            schema='amg_noemotion_prompt_policy_v1',
            base_policy='bcd_evidence_v1',
            base_run=str(BASE),
            base_evidence_levels=levels,
            levels_unchanged=[0, 1, 2],
            level3_changed_to=2,
            removed_lines=['Emotion hypotheses:', 'Supporting links:'],
            expected_changed_samples=len(affected),
            expected_total_samples=sum(int(v) for v in levels.values()),
            note=('Only samples whose baseline evidence level was 3 change. '
                  'EmotionConcept candidates and all paths ending in an EmotionConcept are omitted.'),
        ))
        print('AFFECTED', len(affected), 'TOTAL', sum(int(v) for v in levels.values()), flush=True)

        graphpath = Path(p['new_graph_path'])
        protect = [
            ROOT / 'amg_base7_graph10_noemotion/run.py',
            ROOT / 'amg_base7_graph10_noemotion/execution_original.py',
            ROOT / 'amg_base7_graph10_noemotion/original_model.py',
            ROOT / 'amg_bcd/policy.py',
            ROOT / 'AffectGPT/inference_hybird.py',
            ROOT / 'AffectGPT/my_affectgpt/conversation/conversation_video.py',
            ROOT / 'AffectGPT/my_affectgpt/models/affectgpt.py',
            ROOT / 'AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py',
            graphpath / 'graph/graph.json',
            graphpath / 'graph/paths_cue_appraisal_emotion.csv',
            Path(p['query_config_path']),
            RUN / 'original_config.json',
            RUN / 'cache_inventory.json',
            RUN / 'cache_manifest.json',
            RUN / 'native_contract_test.json',
            RUN / 'native_dataset_audit.json',
            RUN / 'prompt_policy.json',
            RUN / 'affected_level3_samples.json',
        ] + [Path(s['path']) for s in p['datasets'].values()]
        p['protected_files'] = {str(f): sha(f) for f in protect}
        p['plan_id'] = canonical(p)
        dump(RUN / 'plan.json', p)

        for epoch in p['checkpoints']:
            for d, spec in p['datasets'].items():
                jid = f'epoch_{int(epoch):03d}_{d}'
                shards = []
                for lo in range(0, spec['samples'], 32):
                    sid = jid + f'_{lo:05d}'
                    shards.append(sid)
                    dump(RUN / 'shards' / (sid + '.json'), dict(
                        shard_id=sid, job_id=jid, epoch=int(epoch), dataset=d,
                        start=lo, stop=min(lo + 32, spec['samples']),
                        samples=min(32, spec['samples'] - lo), state='pending', attempts=0))
                dump(RUN / 'jobs' / (jid + '.json'), dict(
                    job_id=jid, epoch=int(epoch), dataset=d, samples=spec['samples'],
                    shards=shards, state='pending'))
                dump(RUN / 'evaluation_jobs' / (jid + '.json'), dict(
                    job_id=jid, epoch=int(epoch), dataset=d, samples=spec['samples'],
                    state='pending', attempts=0))

        ref = read(BASE / 'capacity_reference.json')
        ref.update(inference_plan_id=p['plan_id'],
                   basis=('Existing six-worker 1536-input+1200-output capacity evidence; '
                          'only the prompt text is shortened by the emotion-block removal.'))
        dump(RUN / 'capacity_reference.json', ref)

        e = copy.deepcopy(read(BASE / 'execution_plan.json'))
        e.pop('execution_id', None)
        e.update(inference_plan_id=p['plan_id'], created_at_beijing=now(),
                 updated_at_beijing=now(), capacity_reference=str(RUN / 'capacity_reference.json'),
                 empty_generation_policy='Original empty response saved verbatim')
        e['protected_files'] = {k: v for k, v in e['protected_files'].items()
                                if '/amg_base7_graph10/' not in k}
        e['protected_files'].update({str(f): sha(f) for f in [
            ROOT / 'amg_base7_graph10_noemotion/execution_original.py',
            ROOT / 'amg_base7_graph10_noemotion/original_model.py',
            RUN / 'capacity_reference.json', RUN / 'native_contract_test.json',
            RUN / 'prompt_policy.json', RUN / 'affected_level3_samples.json']})
        e['execution_id'] = canonical(e)
        dump(RUN / 'execution_plan.json', e)

        for name in ['evaluation_preflight.json', 'scheduling_preflight.json']:
            v = read(BASE / name)
            v['execution_id'] = e['execution_id']
            dump(RUN / name, v)

        (RUN / 'README.md').write_text(
            'Seven original checkpoints x nine official test sets. Native inference_hybird '
            'sample loop, original readers/model/Chat/generation. Reuse frozen graph10 query '
            'cache; remove only the Emotion hypotheses and Supporting links lines. Cue and '
            'Appraisal text remains byte-identical. Two physical GPUs, three workers each, '
            'global dataset-size descending 32-sample shards. Automatic original evaluation '
            'after all 63 jobs and six workers exit.\n')
        dump(RUN / 'prepare_status.json', dict(
            state='complete', samples=sum(int(v) for v in levels.values()), jobs=63,
            predictions=89593, changed_samples=len(affected), time_beijing=now(),
            plan_id=p['plan_id'], execution_id=e['execution_id']))
        dump(ROOT / 'amg_base7_graph10_noemotion/current_run.json', dict(run=str(RUN)))
        dump(ROOT / 'amg_base7_graph10_noemotion/preparing.json',
             dict(run=str(RUN), base_run=str(BASE), state='complete'))
        print('PREPARED', RUN, flush=True)
    except BaseException as exc:
        import traceback
        dump(RUN / 'prepare_status.json', dict(
            state='failed', error=repr(exc), traceback=traceback.format_exc(),
            time_beijing=now()))
        raise


if __name__ == '__main__':
    main()
