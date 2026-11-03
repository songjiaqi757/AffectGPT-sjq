"""Durable full MER-Caption+ API annotation; credentials remain in process memory."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse, collections, concurrent.futures, copy, csv, datetime, email.utils, fcntl, hashlib, json, math, os, random, shutil, signal, sqlite3, sys, threading, time
from graph_paths import Path
import requests
import annotate_api as core
from media_upload import temporary_url

ROOT=core.C/'runs/mercaptionplus'
MODALITIES=('text','audio','visual')
HALT=threading.Event()
HALT_REASON=''

def stop(reason):
    global HALT_REASON
    HALT_REASON=reason;HALT.set()

def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);core.dump(path,obj)

def classify_http(status,body):
    text=json.dumps(body,ensure_ascii=False).lower()
    billing=any(w in text for w in ('insufficient_quota','insufficientquota','arrearage','insufficient balance','balance insufficient','overdue','quotaexhausted','欠费','余额不足'))
    if status in (401,402,403) or billing:return 'fatal',False
    if status==429:return 'rate_limit',True
    if status in (408,409,425) or status>=500:return 'transient',True
    return 'request_rejected',False

def retry_seconds(value,default=60):
    if value:
        try:return max(1,float(value))
        except ValueError:
            try:return max(1,email.utils.parsedate_to_datetime(value).timestamp()-time.time())
            except (ValueError,TypeError):pass
    return default

class RateLimiter:
    def __init__(self,rpm=240,tpm=1600000,clock=time.monotonic):
        self.max_rpm=rpm;self.rpm=rpm;self.tpm=tpm;self.clock=clock
        self.lock=threading.Lock();self.events=collections.deque();self.next_start=0.;self.cooldown=0.;self.rate_events=0;self.workers=12
    def reserve(self,tokens):
        if tokens>self.tpm:raise ValueError('Estimated single request exceeds token rate budget')
        while not HALT.is_set():
            with self.lock:
                now=self.clock()
                while self.events and self.events[0][0]<=now-60:self.events.popleft()
                wait=max(0,self.next_start-now,self.cooldown-now)
                if len(self.events)>=self.rpm or sum(e[1] for e in self.events)+tokens>self.tpm:
                    wait=max(wait,self.events[0][0]+60-now+.02) if self.events else wait
                if wait<=0:
                    event=[now,tokens];self.events.append(event);self.next_start=now+60/self.rpm;return event
            HALT.wait(min(wait,1.))
        raise InterruptedError(HALT_REASON)
    def reconcile(self,event,actual):
        if actual:
            with self.lock:event[1]=max(event[1],actual)
    def penalize(self,delay):
        with self.lock:
            self.rpm=max(12,self.rpm//2);self.cooldown=max(self.cooldown,self.clock()+delay);self.rate_events+=1
    def configure(self,workers,rpm,tpm):
        assert 1<=workers<=64 and 12<=rpm<=1000 and 10000<=tpm<=1600000
        with self.lock:
            if rpm!=self.max_rpm:
                self.rpm=min(rpm,max(12,round(self.rpm*rpm/self.max_rpm)))
                self.max_rpm=rpm
            self.tpm=tpm;self.workers=workers
    def snapshot(self):
        with self.lock:return dict(request_concurrency=self.workers,rpm_limit=self.rpm,rpm_ceiling=self.max_rpm,tpm_limit=self.tpm,rate_limit_events=self.rate_events)

class Queue:
    def __init__(self,root):
        self.root=Path(root);self.lock=threading.RLock()
        self.db=sqlite3.connect(self.root/'tasks.sqlite3',check_same_thread=False,timeout=60)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=DELETE');self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS tasks(
          sid TEXT, modality TEXT, state TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
          retryable INTEGER NOT NULL DEFAULT 1, last_error TEXT, updated REAL,
          PRIMARY KEY(sid,modality));
          CREATE INDEX IF NOT EXISTS task_state ON tasks(state);
          CREATE TABLE IF NOT EXISTS attempts(sid TEXT,modality TEXT,number INTEGER,http_status INTEGER,
          prompt_tokens INTEGER,completion_tokens INTEGER,total_tokens INTEGER,error_kind TEXT,created REAL,
          PRIMARY KEY(sid,modality,number));''')
    def initialize(self,samples):
        with self.lock,self.db:
            self.db.executemany('INSERT OR IGNORE INTO tasks(sid,modality,updated) VALUES(?,?,?)',((s['sample_id'],m,time.time()) for s in samples for m in MODALITIES))
            self.db.execute("UPDATE tasks SET state='pending' WHERE state='running'")
    def claim(self):
        with self.lock,self.db:
            row=self.db.execute("SELECT * FROM tasks WHERE state='pending' ORDER BY rowid LIMIT 1").fetchone()
            if row is None:return None
            self.db.execute("UPDATE tasks SET state='running',updated=? WHERE sid=? AND modality=?",(time.time(),row['sid'],row['modality']))
            return dict(row)
    def mark(self,sid,m,state,error=None,retryable=True):
        with self.lock,self.db:self.db.execute('UPDATE tasks SET state=?,last_error=?,retryable=?,updated=? WHERE sid=? AND modality=?',(state,error,int(retryable),time.time(),sid,m))
    def next_attempt(self,sid,m):
        with self.lock,self.db:
            n=self.db.execute('SELECT attempts FROM tasks WHERE sid=? AND modality=?',(sid,m)).fetchone()[0]+1
            self.db.execute('UPDATE tasks SET attempts=?,updated=? WHERE sid=? AND modality=?',(n,time.time(),sid,m));return n
    def attempt(self,sid,m,n,status,usage,kind):
        usage=usage or {}
        with self.lock,self.db:self.db.execute('INSERT OR REPLACE INTO attempts VALUES(?,?,?,?,?,?,?,?,?)',(sid,m,n,status,usage.get('prompt_tokens',0),usage.get('completion_tokens',0),usage.get('total_tokens',0),kind,time.time()))
    def recover_retries(self,include_permanent=False):
        with self.lock,self.db:
            clause="" if include_permanent else " AND retryable=1"
            n=self.db.execute("UPDATE tasks SET state='pending' WHERE state='failed' AND attempts<6"+clause).rowcount
            return n
    def snapshot(self):
        with self.lock:
            counts=dict(self.db.execute('SELECT state,count(*) FROM tasks GROUP BY state').fetchall())
            modalities={m:dict(self.db.execute('SELECT state,count(*) FROM tasks WHERE modality=? GROUP BY state',(m,)).fetchall()) for m in MODALITIES}
            full=self.db.execute("SELECT count(*) FROM (SELECT sid FROM tasks GROUP BY sid HAVING sum(state='succeeded')=3)").fetchone()[0]
            failed_samples=self.db.execute("SELECT count(DISTINCT sid) FROM tasks WHERE state='failed'").fetchone()[0]
            usage=self.db.execute('SELECT coalesce(sum(prompt_tokens),0),coalesce(sum(completion_tokens),0),coalesce(sum(total_tokens),0),count(*) FROM attempts').fetchone()
            retryable=self.db.execute("SELECT count(*) FROM tasks WHERE state='failed' AND retryable=1").fetchone()[0]
        return dict(counts=counts,modality_counts=modalities,completed_samples=full,failed_samples=failed_samples,retryable_failed_tasks=retryable,
                    usage_including_failed_generations=dict(prompt_tokens=usage[0],completion_tokens=usage[1],total_tokens=usage[2]),http_attempts=usage[3])

def estimate(meta,prompt):
    media=1200*meta.get('duration_sec',0) if meta['modality']=='visual' else 40*meta.get('duration_sec',0) if meta['modality']=='audio' else 0
    return math.ceil(len(prompt)/3+media+3072)

def prepare(root=ROOT,dataset=None):
    root=Path(root);dataset=Path(dataset or core.C.parent/'dataset/mer2025-dataset')
    root.mkdir(parents=True,exist_ok=True)
    if (root/'samples.json').exists():
        samples=json.loads((root/'samples.json').read_text());assert len(samples)==31327
    else:
        with (dataset/'track2_train_mercaptionplus.csv').open() as f:
            names=[r['name'] for r in csv.DictReader(f)] # Membership only; no emotion or caption targets enter prompts.
        assert len(names)==len(set(names))==31327
        wanted=set(names)
        with (dataset/'subtitle_chieng.csv').open() as f:
            texts={r['name']:{k:r[k] or '' for k in ('chinese','english')} for r in csv.DictReader(f) if r['name'] in wanted}
        assert set(texts)==wanted
        samples=[dict(sample_id=sid,text=texts[sid],audio_path=str(dataset/'audio'/f'{sid}.wav'),video_path=str(dataset/'video'/f'{sid}.mp4')) for sid in names]
        missing=[s['sample_id'] for s in samples if not Path(s['audio_path']).is_file() or not Path(s['video_path']).is_file()]
        assert not missing,f'Missing media: {missing[:10]}'
        dump(root/'samples.json',samples)
    for name in ('annotations','teacher_raw','inputs','failed','prompts','media/audio','media/video'):(root/name).mkdir(parents=True,exist_ok=True)
    protocol=json.loads((core.CONFIG/'protocol.json').read_text());protocol['sample_ids']=[s['sample_id'] for s in samples]
    protocol['full_dataset_started']=True;protocol['workers']=12
    if (root/'protocol.json').exists():
        existing=json.loads((root/'protocol.json').read_text())
        assert all(existing[k]==protocol[k] for k in ('generation','prompt_sha256','quality','sample_ids','model_requested','endpoint'))
    else:dump(root/'protocol.json',protocol)
    shutil.copy2(_graph_resolve_path(core.CONFIG / 'ontology.json'), _graph_resolve_path(root / 'ontology.json'))
    for m in MODALITIES:shutil.copy2(_graph_resolve_path(core.CONFIG / f'{m}.txt'), _graph_resolve_path(root / 'prompts' / f'{m}.txt'))
    cfg=dict(workers=12,rpm=240,tpm=1600000,maximum_attempts_per_round=3,maximum_attempts_total=6,automatic_retry_rounds=1,
             on_failure='unlabeled; y empty; mask 0; preserve other modalities',read_timeout_seconds=240,
             frozen_prompts_unchanged=True,source_target_labels_excluded=True,full_dataset_explicitly_authorized=True)
    if (root/'runtime_config.json').exists():cfg=json.loads((root/'runtime_config.json').read_text())
    else:dump(root/'runtime_config.json',cfg)
    db=Queue(root);db.initialize(samples)
    status=db.snapshot();status.update(phase='prepared',complete=False,total_samples=len(samples),total_tasks=len(samples)*3,run_id=root.name,updated_unix=time.time())
    dump(root/'status.json',status)
    return samples,protocol,cfg

def reviewed_record(obj,meta,protocol,response,number,seconds):
    rec=dict(status='ok',annotation=copy.deepcopy(obj),meta=meta,
             versions={'protocol_version':core.VERSION,'teacher':core.MODEL,'prompt_sha256':protocol['prompt_sha256'][obj['modality']]},
             api={'model_requested':core.MODEL,'model_returned':response.get('model'),'response_id':response.get('id'),'usage':response.get('usage'),'attempt':number,'seconds':seconds},origin=core.VERSION)
    return rec

class Runner:
    def __init__(self,root,samples,protocol,cfg,key,transport=None,sleeper=None):
        self.root=Path(root);core.RUN=self.root;self.samples=samples;self.index={s['sample_id']:s for s in samples};self.protocol=protocol;self.cfg=cfg;self.key=key
        self.ids=json.loads((core.CONFIG/'ontology.json').read_text())['cue_ids'];self.prompts={m:(core.CONFIG/f'{m}.txt').read_text() for m in MODALITIES}
        assert all(_graph_hash_matches(p.encode(), protocol['prompt_sha256'][m], core.sha(p.encode())) for m,p in self.prompts.items())
        self.queue=Queue(root);self.limiter=RateLimiter(cfg['rpm'],cfg['tpm']);self.limiter.workers=cfg['workers'];self.transport=transport or requests.post;self.sleep=sleeper or HALT.wait
        self.print_lock=threading.Lock();self.round=0;self.consecutive_failures=0;self.failure_lock=threading.Lock()
        overrides=self.root/'transport_overrides.json'
        self.transport_overrides=json.loads(overrides.read_text()) if overrides.exists() else {}
    def log(self,obj):
        with self.print_lock:print(json.dumps(obj,ensure_ascii=False),flush=True)
    def fail(self,sid,m,kind,message,retryable,errors):
        message=message.replace(self.key,'[REDACTED]')
        dump(self.root/'failed'/f'{sid}.{m}.json',dict(sample_id=sid,modality=m,kind=kind,error=message,retryable=retryable,errors=errors,labels_written=False,updated_unix=time.time()))
        self.queue.mark(sid,m,'failed',message,retryable)
        with self.failure_lock:
            self.consecutive_failures+=1
            if self.consecutive_failures>=36:stop('36 consecutive task failures; inspect network/API before resuming')
        self.log(dict(sample_id=sid,modality=m,status='failed',kind=kind,retryable=retryable))
    def task(self,job,maximum_requests=3):
        assert 1<=maximum_requests<=3
        sid,m=job['sid'],job['modality'];s=self.index[sid];dest=self.root/'annotations'/f'{sid}.{m}.json'
        if dest.exists():
            rec=json.loads(dest.read_text());core.validate(json.dumps(rec['annotation']),sid,m,self.ids[m]);self.queue.mark(sid,m,'succeeded');return
        if job['attempts']>=6:self.fail(sid,m,'attempt_budget','Maximum six requests reached',False,[]);return
        try:
            if shutil.disk_usage(self.root).free<5*1024**3:stop('Disk free space below 5 GiB');raise InterruptedError(HALT_REASON)
            override=self.transport_overrides.get(sid+'.'+m)
            media_url=None
            if override:
                assert override['transport']=='provider_private_temporary_oss'
                assert m in ('visual','audio')
                if m=='visual':
                    info=core.prepare_video(s,force_h264=override.get('force_h264',False),allow_large=True)
                    path=info['submitted_video_path']
                else:path=core.prepare_audio(s)[0]
                media_url=temporary_url(path,self.key,self.root/'upload_cache')
            try:
                data,meta=core.build(s,m,self.prompts[m],media_url=media_url) if media_url else core.build(s,m,self.prompts[m])
            except AssertionError as exc:
                if m=='visual' and 'Base64 budget' in str(exc):
                    core.prepare_video(s,force_h264=True);data,meta=core.build(s,m,self.prompts[m])
                else:raise
            dump(self.root/'inputs'/f'{sid}.{m}.json',meta)
        except InterruptedError:
            self.queue.mark(sid,m,'pending');return
        except requests.RequestException as exc:
            if HALT.is_set():self.queue.mark(sid,m,'pending');return
            self.fail(sid,m,'upload_network_error',type(exc).__name__+': '+str(exc),True,[]);return
        except Exception as exc:
            self.fail(sid,m,'input_failed',type(exc).__name__+': '+str(exc),False,[]);return
        errors=[];last_kind='transient';last_error='';retryable=True
        request_count=min(maximum_requests,6-job['attempts'])
        for local_attempt in range(request_count):
            if HALT.is_set():self.queue.mark(sid,m,'pending');return
            try:reservation=self.limiter.reserve(estimate(meta,self.prompts[m]))
            except InterruptedError:self.queue.mark(sid,m,'pending');return
            number=self.queue.next_attempt(sid,m);started=time.time();record=dict(sample_id=sid,modality=m,attempt=number,request_sha256=meta['request_sha256'],model_requested=core.MODEL,endpoint=core.ENDPOINT,started_unix=started,input_metadata=meta)
            status=None;usage={};last_kind='network_error';retryable=True
            try:
                proxy=os.environ.get('QWEN_HTTPS_PROXY');proxies={'http':proxy,'https':proxy} if proxy else None
                headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'}
                if media_url:headers['X-DashScope-OssResourceResolve']='enable'
                response=self.transport(core.ENDPOINT,data=data,headers=headers,timeout=(20,240),allow_redirects=False,proxies=proxies)
                status=response.status_code;text=response.text.replace(self.key,'[REDACTED]')
                try:body=json.loads(text)
                except ValueError:body={'unparsed_response':text[:10000]}
                usage=body.get('usage') or {};self.limiter.reconcile(reservation,usage.get('total_tokens'))
                record.update(http_status=status,seconds=time.time()-started,request_id=response.headers.get('x-request-id') or response.headers.get('request-id'),response=body)
                dump(self.root/'teacher_raw'/f'{sid}.{m}.attempt{number}.json',record)
                if status!=200:
                    last_kind,retryable=classify_http(status,body)
                    if last_kind=='fatal':stop('API authentication/permission/balance error; inspect account')
                    if last_kind=='rate_limit':self.limiter.penalize(retry_seconds(response.headers.get('Retry-After')))
                    if m=='visual' and status>=500 and 'STOP_ENGINE_ABORT' in text:
                        core.prepare_video(s,force_h264=True,allow_large=bool(media_url))
                        if media_url:
                            info=core.prepare_video(s,allow_large=True)
                            media_url=temporary_url(info['submitted_video_path'],self.key,self.root/'upload_cache')
                        data,meta=core.build(s,m,self.prompts[m],media_url=media_url) if media_url else core.build(s,m,self.prompts[m])
                        dump(self.root/'inputs'/f'{sid}.{m}.json',meta)
                    raise RuntimeError('HTTP '+str(status)+': '+json.dumps(body,ensure_ascii=False)[:1500])
                last_kind='invalid_output'
                assert body.get('model')==core.MODEL,'Returned model differs'
                choice=body['choices'][0];assert choice['finish_reason']=='stop','Generation incomplete: '+str(choice['finish_reason'])
                obj=core.validate(choice['message']['content'],sid,m,self.ids[m])
                dump(dest,reviewed_record(obj,meta,self.protocol,body,number,time.time()-started))
                self.queue.attempt(sid,m,number,status,usage,'success');self.queue.mark(sid,m,'succeeded')
                (self.root/'failed'/f'{sid}.{m}.json').unlink(missing_ok=True)
                with self.failure_lock:self.consecutive_failures=0
                self.log(dict(sample_id=sid,modality=m,status='ok',attempt=number,seconds=round(time.time()-started,2)));return
            except Exception as exc:
                last_error=(type(exc).__name__+': '+str(exc)).replace(self.key,'[REDACTED]');errors.append(dict(attempt=number,kind=last_kind,error=last_error))
                self.queue.attempt(sid,m,number,status,usage,last_kind)
                if 'response' not in record:
                    record.update(error=last_error,seconds=time.time()-started);dump(self.root/'teacher_raw'/f'{sid}.{m}.attempt{number}.json',record)
                if HALT.is_set():
                    self.queue.mark(sid,m,'pending',last_error,True);return
                if not retryable:break
                if local_attempt<request_count-1:self.sleep(min(60,2**(local_attempt+1)+random.uniform(0,1)))
        self.fail(sid,m,last_kind,last_error,retryable,errors)
    def worker(self,slot=0):
        while not HALT.is_set() and slot<self.cfg['workers']:
            job=self.queue.claim()
            if not job:return
            try:self.task(job)
            except Exception as exc:
                self.fail(job['sid'],job['modality'],'internal_error',(type(exc).__name__+': '+str(exc)).replace(self.key,'[REDACTED]'),True,[])
    def refresh_runtime(self):
        path=self.root/'runtime_config.json'
        if not path.exists():return
        try:
            config=json.loads(path.read_text())
            workers=int(config['workers']);rpm=int(config['rpm']);tpm=int(config['tpm'])
            assert 1<=workers<=64 and 12<=rpm<=1000 and 10000<=tpm<=1600000
            before={k:self.cfg[k] for k in ('workers','rpm','tpm')}
            after=dict(workers=workers,rpm=rpm,tpm=tpm)
            if before!=after:
                self.limiter.configure(**after);self.cfg.update(after)
                self.log({'phase':'runtime_limits_updated','before':before,'after':after})
        except (ValueError,KeyError,AssertionError,OSError) as exc:
            self.log({'phase':'runtime_config_invalid','error':type(exc).__name__})
    def status(self,phase='running'):
        result=self.queue.snapshot();result.update(phase=phase,complete=result['counts'].get('succeeded',0)==len(self.samples)*3,
            total_tasks=len(self.samples)*3,total_samples=len(self.samples),run_id=self.root.name,run_label=f"MER-Caption+全量 · {self.cfg['workers']}请求并发",
            updated_unix=time.time(),pid=os.getpid(),round=self.round,halt_reason=HALT_REASON,limits=self.limiter.snapshot())
        dump(self.root/'status.json',result);return result
    def run(self):
        for round_index in (1,2):
            self.round=round_index
            if round_index==2:
                if HALT.is_set():break
                n=self.queue.recover_retries()
                if not n:break
                self.log({'phase':'retry_failed_tasks','count':n})
                self.sleep(30)
            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
                futures={}
                while True:
                    self.refresh_runtime()
                    with self.queue.lock:
                        pending=self.queue.db.execute("SELECT count(*) FROM tasks WHERE state='pending'").fetchone()[0]
                    if not HALT.is_set() and pending:
                        for slot in range(self.cfg['workers']):
                            if slot not in futures or futures[slot].done():
                                if slot in futures:futures[slot].result()
                                futures[slot]=pool.submit(self.worker,slot)
                    active=any(not f.done() for f in futures.values())
                    if not active and (HALT.is_set() or not pending):break
                    self.status();time.sleep(5)
                for future in futures.values():future.result()
        phase='stopped' if HALT.is_set() else 'complete' if self.queue.snapshot()['counts'].get('succeeded',0)==len(self.samples)*3 else 'complete_with_failures'
        result=self.status(phase)
        if not HALT.is_set():export(self.root,self.samples,self.ids,self.queue)
        else:dump(self.root/'summary.json',self.queue.snapshot())
        self.status(phase);return result

def export(root,samples,ids,queue):
    """Streaming exports; absent tasks remain unlabeled/mask=0, never negative."""
    root=Path(root);temp=root/'labels.csv.tmp'
    with temp.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['sample_id','modality','cue_id','state','y','mask','evidence_note','protocol_version']);writer.writeheader()
        for s in samples:
            sid=s['sample_id']
            for m in MODALITIES:
                p=root/'annotations'/f'{sid}.{m}.json';labels=json.loads(p.read_text())['annotation']['labels'] if p.exists() else {}
                for cue in ids[m]:
                    label=labels.get(cue,{'state':'unlabeled','evidence_note':'Task not successfully annotated; inspect failures.csv and tasks.sqlite3'})
                    st=label['state'];writer.writerow(dict(sample_id=sid,modality=m,cue_id=cue,state=st,y=1 if st=='positive' else 0 if st=='negative' else '',mask=int(st in ('positive','negative')),evidence_note=label['evidence_note'],protocol_version=core.VERSION))
    temp.replace(root/'labels.csv')
    with queue.lock:
        failed=[dict(x) for x in queue.db.execute("SELECT sid AS sample_id,modality,state,attempts,retryable,last_error FROM tasks WHERE state!='succeeded'")]
    with (root/'failures.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['sample_id','modality','state','attempts','retryable','last_error']);writer.writeheader();writer.writerows(failed)
    dump(root/'summary.json',queue.snapshot())

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-dir',type=Path,default=ROOT)
    parser.add_argument('--prepare',action='store_true');parser.add_argument('--status',action='store_true');parser.add_argument('--retry-failed',action='store_true');parser.add_argument('--export',action='store_true');parser.add_argument('--include-permanent',action='store_true')
    args=parser.parse_args();root=args.run_dir.resolve();root.mkdir(parents=True,exist_ok=True)
    if args.status:
        print((root/'status.json').read_text());return
    with (root/'runner.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise SystemExit('A full annotation process already owns this run')
        if args.prepare:
            samples,protocol,cfg=prepare(root);print('PREPARED',len(samples),len(samples)*3);return
        samples=json.loads((root/'samples.json').read_text());protocol=json.loads((root/'protocol.json').read_text());cfg=json.loads((root/'runtime_config.json').read_text())
        queue=Queue(root)
        if args.export:export(root,samples,json.loads((core.CONFIG/'ontology.json').read_text())['cue_ids'],queue);return
        queue.initialize(samples)
        if args.include_permanent:assert args.retry_failed,'--include-permanent requires --retry-failed after input repair'
        if args.retry_failed:queue.recover_retries(args.include_permanent)
        print('READY_FOR_API_KEY',flush=True);key=os.environ.get('QWEN_API_KEY') or sys.stdin.readline().strip()
        assert key,'Missing API credential'
        for signum in (signal.SIGINT,signal.SIGTERM):signal.signal(signum,lambda *_:stop('User or system requested stop; resume safely using the same run'))
        (root/'runner.pid').write_text(str(os.getpid()))
        runner=Runner(root,samples,protocol,cfg,key);result=runner.run();print(json.dumps(result,ensure_ascii=False),flush=True)
        if not result['complete']:raise SystemExit(2)

if __name__=='__main__':main()
