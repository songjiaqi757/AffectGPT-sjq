"""Audit and selectively requeue technical failures after an input transport repair."""
import argparse, fcntl, json, time
from pathlib import Path
import annotate_full as full

def remedy(modality,error):
    if 'data_inspection_failed' in error:return None
    if modality=='visual' and 'Base64 budget' in error:
        return dict(transport='provider_private_temporary_oss',force_h264=False,reason='Complete file exceeds Base64 size limit')
    if modality in ('visual','audio') and 'provided URL does not appear to be valid' in error:
        return dict(transport='provider_private_temporary_oss',force_h264=modality=='visual',reason='File decoding/transport compatibility')
    return None

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-dir',type=Path,default=full.ROOT)
    p.add_argument('--apply',action='store_true');p.add_argument('--limit',type=int)
    p.add_argument('--retry-upload-errors',action='store_true',help='Also recover network failures before a model request')
    args=p.parse_args();root=args.run_dir
    with (root/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        q=full.Queue(root)
        states="('running')" if args.retry_upload_errors else "('pending','running')"
        assert not q.db.execute('SELECT 1 FROM tasks WHERE state IN '+states).fetchone(),'Finish or stop the current queue first'
        manifest=root/'repair_manifest.json'
        if manifest.exists():plan=json.loads(manifest.read_text())
        else:
            tasks=[]
            for row in q.db.execute("SELECT * FROM tasks WHERE state='failed'"):
                entry=dict(row);entry['remedy']=remedy(row['modality'],row['last_error']);tasks.append(entry)
            plan=dict(created_unix=time.time(),strategy='Only technical failures; preserve complete duration/resolution/FPS/frames. Never requeue content moderation or pad short media.',
                official_reference='https://platform.qianwenai.com/docs/api-reference/more/upload-file-get-temporary-url',tasks=tasks)
            full.dump(manifest,plan)
        eligible=[]
        for task in plan['tasks']:
            current=q.db.execute('SELECT * FROM tasks WHERE sid=? AND modality=?',(task['sid'],task['modality'])).fetchone()
            error=current['last_error'] or ''
            upload_network=args.retry_upload_errors and current['attempts']==task['attempts'] and error.startswith(('ProxyError:','ConnectionError:','ConnectTimeout:','ReadTimeout:','Timeout:'))
            if task['remedy'] and current['state']=='failed' and current['attempts']<6 and (current['last_error']==task['last_error'] or upload_network):
                eligible.append(task)
        selected=eligible[:args.limit] if args.limit else eligible
        if args.apply:
            path=root/'transport_overrides.json';overrides=json.loads(path.read_text()) if path.exists() else {}
            for task in selected:overrides[task['sid']+'.'+task['modality']]=task['remedy']
            full.dump(path,overrides)
            with q.db:
                for task in selected:
                    q.db.execute("UPDATE tasks SET state='pending',retryable=1,updated=? WHERE sid=? AND modality=?",(time.time(),task['sid'],task['modality']))
            history=root/'repair_actions.jsonl'
            with history.open('a') as f:
                f.write(json.dumps(dict(time_unix=time.time(),queued=[t['sid']+'.'+t['modality'] for t in selected]))+'\n')
        print(json.dumps(dict(applied=args.apply,eligible=len(eligible),selected=len(selected),original_failures=len(plan['tasks']),
            excluded_moderation=sum('data_inspection_failed' in t['last_error'] for t in plan['tasks']),
            excluded_short_video=sum('video file is too short' in t['last_error'] for t in plan['tasks']))))

if __name__=='__main__':main()
