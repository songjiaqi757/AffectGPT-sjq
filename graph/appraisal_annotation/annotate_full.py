"""Durable full Appraisal v2.4: one joint Text/Audio/Video request per eligible sample."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,base64,concurrent.futures,copy,csv,fcntl,json,math,os,random,re,shutil,signal,sqlite3,subprocess,sys,threading,time
from collections import Counter
from graph_paths import Path
import requests
import annotate as pilot
sys.path.insert(0,str(pilot.PROJECT/'cue_annotation'))
import annotate_api as media
import importlib.util
_scheduler_spec=importlib.util.spec_from_file_location('cue_full_scheduler',pilot.PROJECT/'cue_annotation/annotate_full.py')
scheduler=importlib.util.module_from_spec(_scheduler_spec)
sys.modules['cue_full_scheduler']=scheduler
_scheduler_spec.loader.exec_module(scheduler)
from media_upload import temporary_url
BASE=pilot.BASE
ROOT=BASE/'runs/mercaptionplus_v2_4'
SOURCE=pilot.PROJECT/'cue_annotation/runs/mercaptionplus'
REFERENCE=BASE/'runs/pilot30_v2_4'
scheduler.MODALITIES=('joint',)
HALT=scheduler.HALT
load=pilot.load
dump=scheduler.dump

class JointQueue(scheduler.Queue):
    def __init__(self,root):
        super().__init__(root)
        cols={r[1] for r in self.db.execute('PRAGMA table_info(tasks)')}
        with self.lock,self.db:
            for name,typ in [('valid_dimensions','INTEGER DEFAULT 0'),('invalid_dimensions','INTEGER DEFAULT 0'),('search_text',"TEXT DEFAULT ''")]:
                if name not in cols:self.db.execute(f'ALTER TABLE tasks ADD COLUMN {name} {typ}')
    def initialize(self,samples):
        super().initialize(samples)
        with self.lock,self.db:
            self.db.executemany("UPDATE tasks SET search_text=? WHERE sid=? AND search_text=''",
                ((s['sample_id']+' '+s['text']['chinese']+' '+s['text']['english'],s['sample_id']) for s in samples))
    def success(self,sid,annotation):
        valid=sum(d['valid'] for d in annotation['dimensions'])
        search=' '.join([annotation['event_context']]+[' '.join(str(d.get(k) or '') for k in ['dimension_id','state','evidence','unknown_reason']) for d in annotation['dimensions']])
        with self.lock,self.db:
            self.db.execute("UPDATE tasks SET state='succeeded',last_error=NULL,valid_dimensions=?,invalid_dimensions=?,search_text=search_text||' '||?,updated=? WHERE sid=? AND modality='joint'",
                (valid,6-valid,search,time.time(),sid))
    def snapshot(self):
        with self.lock:
            raw=dict(self.db.execute('SELECT state,count(*) FROM tasks GROUP BY state').fetchall())
            v,i=self.db.execute('SELECT coalesce(sum(valid_dimensions),0),coalesce(sum(invalid_dimensions),0) FROM tasks WHERE state="succeeded"').fetchone()
            usage=self.db.execute('SELECT coalesce(sum(prompt_tokens),0),coalesce(sum(completion_tokens),0),coalesce(sum(total_tokens),0),count(*) FROM attempts').fetchone()
            retryable=self.db.execute("SELECT count(*) FROM tasks WHERE state='failed' AND retryable=1 AND attempts<6").fetchone()[0]
        return dict(counts=dict(ok=raw.get('succeeded',0),pending=raw.get('pending',0),running=raw.get('running',0),failed=raw.get('failed',0)),
            queue_counts=raw,successful_samples=raw.get('succeeded',0),completed_samples=raw.get('succeeded',0),
            valid_dimension_count=v,invalid_dimension_count=i,dimension_rows=raw.get('succeeded',0)*6,
            retryable_failed_tasks=retryable,http_attempts=usage[3],
            usage_including_failed_generations=dict(prompt_tokens=usage[0],completion_tokens=usage[1],total_tokens=usage[2]))

def prepare(root=ROOT):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    for d in ['annotations','teacher_raw','inputs','failed','prompts','media/audio','media/video','upload_cache']:(root/d).mkdir(parents=True,exist_ok=True)
    frozen=load(REFERENCE/'protocol.json')
    doc=REFERENCE/'source_document.md'
    assert _graph_hash_matches(doc.read_bytes(), frozen['source_document_sha256'], media.sha(doc.read_bytes())),'Frozen annotation document differs from validated v2.4' # Current graph/split document may evolve independently.
    prompt=(REFERENCE/'prompts/appraisal_teacher_v2.4.txt').read_text()
    assert _graph_hash_matches(prompt.encode(), frozen['prompt_sha256'], media.sha(prompt.encode()))
    members=load(pilot.RELEASE/'members.json')
    assert len(members)==31255 and len({m['sample_id'] for m in members})==31255
    samples=[dict(sample_id=m['sample_id'],text={k:m['text'].get(k,'') for k in ['chinese','english']},
        audio_path=m['audio_path'],video_path=m['video_path'],source_group_id=m['group_id'],source_video_id=m.get('video_source_id'),
        source_status=m['source_status'],data_role=m['role'],audio_duration=m['audio_duration'],visual_duration=m['visual_duration']) for m in members]
    if (root/'samples.json').exists():assert load(root/'samples.json')==samples
    else:dump(root/'samples.json',samples)
    config=dict(workers=32,rpm=360,tpm=1600000,maximum_attempts_per_round=3,maximum_attempts_total=6,
        automatic_retry_rounds=1,read_timeout_seconds=240,source_target_labels_excluded=True,
        full_dataset_explicitly_authorized=True,live_reconfiguration=True,temporary_upload_workers=4)
    if (root/'runtime_config.json').exists():config=load(root/'runtime_config.json')
    else:dump(root/'runtime_config.json',config)
    protocol=copy.deepcopy(frozen)
    protocol.update(sample_ids=[s['sample_id'] for s in samples],workers=32,maximum_attempts=6,
        full_dataset_started=True,pilot_annotations_reused=False,eligible_samples=len(samples),excluded_samples=72,
        source_population=31327,role_counts=dict(Counter(s['data_role'] for s in samples)),
        cue_input_protocol_sha256=media.sha((SOURCE/'protocol.json').read_bytes()),
        media_transport='base64_with_provider_private_temporary_oss_for_large_inputs',
        actual_input_mode='joint_text_audio_video_single_request')
    pilot.frozen(root/'protocol.json',protocol)
    pilot.frozen(root/'ontology.json',load(REFERENCE/'ontology.json'))
    for src,dest in [(doc,root/'source_document.md'),(REFERENCE/'prompts/appraisal_teacher_v2.4.txt',root/'prompts/appraisal_teacher_v2.4.txt')]:
        if dest.exists():assert dest.read_bytes()==src.read_bytes()
        else:shutil.copy2(_graph_resolve_path(src), _graph_resolve_path(dest))
    db=JointQueue(root);db.initialize(samples);db.db.close()
    media.RUN=root
    return samples,protocol,config,prompt

def restore_inputs(s,root=ROOT):
    root=Path(root);sid=s['sample_id'];media.RUN=root
    for suffix in ['audio.json','video_file.json']:
        source=SOURCE/'inputs'/f'{sid}.{suffix}'
        target=root/'inputs'/f'{sid}.{suffix}'
        if not target.exists():
            meta=load(source)
            if suffix=='video_file.json':meta['submitted_video_path']=str(root/'media/video'/f'{sid}.mp4')
            dump(target,meta)
    audio,_,_=media.prepare_audio(s)
    video_meta=media.prepare_video(s,allow_large=True)
    video=Path(video_meta['submitted_video_path'])
    am=load(root/'inputs'/f'{sid}.audio.json')
    assert _graph_hash_matches(audio.read_bytes(), am['submitted_wav_sha256'], media.sha(audio.read_bytes()))
    return audio,video,am,video_meta

def build(s,protocol,prompt,key=None,root=ROOT,uploader=temporary_url):
    root=Path(root);audio,video,am,vm=restore_inputs(s,root)
    audio_url=video_url=None
    # Keep the same complete files; change only transport if Base64 exceeds provider budget.
    encoded_audio=4*((audio.stat().st_size+2)//3);encoded_video=4*((video.stat().st_size+2)//3)
    if encoded_video>=9_500_000 or encoded_audio+encoded_video>=18_000_000:
        assert key,'Private upload credential required'
        video_url=uploader(video,key,root/'upload_cache')
    if encoded_audio>=9_500_000:
        assert key,'Private upload credential required'
        audio_url=uploader(audio,key,root/'upload_cache')
    runtime=dict(sample_id=s['sample_id'],available_modalities=['text','audio','video'],
        text={k:s['text'].get(k,'') for k in ['chinese','english']},
        audio=dict(mode='complete_continuous_wav',sample_rate=16000,channels=1,duration_sec=am['duration_sec']),
        video=dict(mode='complete_silent_video_file',duration_sec=vm['submitted_video']['duration'],client_frame_sampling=False,
            client_temporal_truncation=False,client_spatial_resize=False,server_processing='provider_default'))
    content=[dict(type='text',text=prompt+'\nRuntime input:\n'+json.dumps(runtime,ensure_ascii=False)),
        dict(type='input_audio',input_audio=dict(data=audio_url or 'data:audio/wav;base64,'+base64.b64encode(audio.read_bytes()).decode(),format='wav')),
        dict(type='video_url',video_url=dict(url=video_url or 'data:video/mp4;base64,'+base64.b64encode(video.read_bytes()).decode()))]
    data=json.dumps(dict(model=media.MODEL,messages=[dict(role='user',content=content)],**protocol['generation']),ensure_ascii=False,separators=(',',':')).encode()
    meta=dict(sample_id=s['sample_id'],source_group_id=s['source_group_id'],source_video_id=s['source_video_id'],data_role=s['data_role'],
        source_status=s['source_status'],source_audio_path=s['audio_path'],source_video_path=s['video_path'],
        actual_input_mode='joint_text_audio_video_single_request',request_content_types=['text','input_audio','video_url'],
        available_modalities=['text','audio','video'],available_modality_mask=dict(text=True,audio=True,video=True),
        actual_text_fields=runtime['text'],audio=runtime['audio'],video=vm,submitted_audio_path=str(audio),
        submitted_audio_sha256=media.sha(audio.read_bytes()),submitted_video_path=str(video),submitted_video_sha256=media.sha(video.read_bytes()),
        same_audio_as_cue=True,same_video_as_cue=True,media_preprocessing_version='cue_qwen_omni_api_exact_full_inputs',
        media_transport=dict(audio='provider_private_temporary_oss' if audio_url else 'base64',video='provider_private_temporary_oss' if video_url else 'base64'),
        prompt_version=pilot.PROMPT_VERSION,prompt_sha256=protocol['prompt_sha256'],annotation_schema_version=pilot.SCHEMA_VERSION,
        ontology_version=pilot.ONTOLOGY_VERSION,forbidden_inputs_included=False,provider_internal_coverage_verified=False,
        request_sha256=media.sha(data),request_bytes=len(data))
    dump(root/'inputs'/f"{s['sample_id']}.joint.json",meta)
    return data,meta,bool(audio_url or video_url)

class Runner(scheduler.Runner):
    def __init__(self,root,samples,protocol,cfg,prompt,key,transport=None):
        self.root=Path(root);media.RUN=self.root;self.samples=samples;self.index={s['sample_id']:s for s in samples}
        self.protocol=protocol;self.cfg=cfg;self.prompt=prompt;self.key=key;self.queue=JointQueue(root)
        self.limiter=scheduler.RateLimiter(cfg['rpm'],cfg['tpm']);self.limiter.workers=cfg['workers']
        self.transport=transport or requests.post;self.sleep=HALT.wait;self.print_lock=threading.Lock()
        self.round=0;self.consecutive_failures=0;self.failure_lock=threading.Lock()
    def fail(self,sid,m,kind,message,retryable,errors):
        message=message.replace(self.key,'[REDACTED]')
        dump(self.root/'failed'/f'{sid}.json',dict(sample_id=sid,status='technical_failure',kind=kind,error=message,
            retryable=retryable,errors=errors,semantic_unknown=False,updated_unix=time.time()))
        self.queue.mark(sid,'joint','failed',message,retryable)
        with self.failure_lock:
            self.consecutive_failures+=1
            if self.consecutive_failures>=36:scheduler.stop('36 consecutive task failures; inspect network/API before resuming')
        self.log(dict(sample_id=sid,status='failed',kind=kind,retryable=retryable))
    def task(self,job,maximum_requests=3):
        sid=job['sid'];s=self.index[sid];dest=self.root/'annotations'/f'{sid}.json'
        if dest.exists():
            rec=load(dest);pilot.validate(json.dumps(rec['annotation']));self.queue.success(sid,rec['annotation']);return
        if job['attempts']>=6:self.fail(sid,'joint','attempt_budget','Maximum six requests reached',False,[]);return
        try:
            if shutil.disk_usage(self.root).free<5*1024**3:scheduler.stop('Disk free space below 5 GiB');raise InterruptedError()
            data,meta,private=build(s,self.protocol,self.prompt,self.key,self.root)
        except InterruptedError:self.queue.mark(sid,'joint','pending');return
        except requests.RequestException as exc:self.fail(sid,'joint','upload_network_error',str(exc),True,[]);return
        except Exception as exc:self.fail(sid,'joint','input_failed',type(exc).__name__+': '+str(exc),False,[]);return
        errors=[];retryable=True;kind='network_error';last_error=''
        for local in range(min(maximum_requests,6-job['attempts'])):
            if HALT.is_set():self.queue.mark(sid,'joint','pending');return
            estimate=math.ceil(len(self.prompt)/3+1240*max(s['audio_duration'],s['visual_duration'])+3072)
            try:reservation=self.limiter.reserve(estimate)
            except InterruptedError:self.queue.mark(sid,'joint','pending');return
            n=self.queue.next_attempt(sid,'joint');started=time.time();status=None;usage={};kind='network_error'
            record=dict(sample_id=sid,attempt=n,request_sha256=meta['request_sha256'],model_requested=media.MODEL,
                endpoint=media.ENDPOINT,started_unix=started,input_metadata=meta,json_parse_status='not_attempted')
            try:
                proxy=os.environ.get('QWEN_HTTPS_PROXY');headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'}
                if private:headers['X-DashScope-OssResourceResolve']='enable'
                response=self.transport(media.ENDPOINT,data=data,headers=headers,timeout=(20,self.cfg['read_timeout_seconds']),
                    allow_redirects=False,proxies={'http':proxy,'https':proxy} if proxy else None)
                status=response.status_code;text=response.text.replace(self.key,'[REDACTED]')
                try:body=json.loads(text)
                except ValueError:body={'unparsed_response':text[:20000]}
                usage=body.get('usage') or {};self.limiter.reconcile(reservation,usage.get('total_tokens'))
                record.update(http_status=status,seconds=time.time()-started,request_id=response.headers.get('x-request-id') or response.headers.get('request-id'),response=body)
                if status!=200:
                    kind,retryable=scheduler.classify_http(status,body)
                    if kind=='fatal':scheduler.stop('API authentication/permission/balance error; inspect account')
                    if kind=='rate_limit':self.limiter.penalize(scheduler.retry_seconds(response.headers.get('Retry-After')))
                    raise RuntimeError('HTTP '+str(status)+': '+json.dumps(body,ensure_ascii=False)[:1500])
                kind='invalid_output';record['json_parse_status']='validating'
                assert body.get('model')==media.MODEL,'Returned model differs'
                choice=body['choices'][0];assert choice['finish_reason']=='stop','Generation incomplete'
                annotation=pilot.validate(choice['message']['content'])
                record['json_parse_status']='valid'
                dump(self.root/'teacher_raw'/f'{sid}.attempt{n}.json',record)
                rec=dict(status='ok',sample_id=sid,source_group_id=s['source_group_id'],source_video_id=s['source_video_id'],
                    data_role=s['data_role'],annotation=annotation,meta=meta,
                    versions=dict(prompt_version=pilot.PROMPT_VERSION,prompt_sha256=self.protocol['prompt_sha256'],
                        annotation_schema_version=pilot.SCHEMA_VERSION,ontology_version=pilot.ONTOLOGY_VERSION),
                    api=dict(model_requested=media.MODEL,model_returned=body.get('model'),response_id=body.get('id'),
                        usage=usage,attempt=n,retry_count=n-1,seconds=record['seconds'],json_parse_status='valid'))
                dump(dest,rec);self.queue.attempt(sid,'joint',n,status,usage,'success');self.queue.success(sid,annotation)
                (self.root/'failed'/f'{sid}.json').unlink(missing_ok=True)
                with self.failure_lock:self.consecutive_failures=0
                self.log(dict(sample_id=sid,status='ok',attempt=n,seconds=round(record['seconds'],2)));return
            except Exception as exc:
                last_error=(type(exc).__name__+': '+str(exc)).replace(self.key,'[REDACTED]')
                if record['json_parse_status']=='validating':record['json_parse_status']='invalid'
                record.update(error=last_error,seconds=time.time()-started)
                dump(self.root/'teacher_raw'/f'{sid}.attempt{n}.json',record)
                self.queue.attempt(sid,'joint',n,status,usage,kind)
                errors.append(dict(attempt=n,kind=kind,error=last_error))
                if HALT.is_set():self.queue.mark(sid,'joint','pending',last_error,True);return
                if not retryable:break
                if local<2:self.sleep(min(60,2**(local+1)+random.uniform(0,1)))
        self.fail(sid,'joint',kind,last_error,retryable,errors)
    def status(self,phase='running'):
        r=self.queue.snapshot();total=len(self.samples)
        r.update(phase=phase,complete=r['successful_samples']==total,test_complete=phase in ('complete','complete_with_failures'),
            tested_samples=r['successful_samples']+r['counts']['failed'],total_samples=total,total_tasks=total,expected_dimensions=6*total,
            run_id=self.root.name,run_label=f"Appraisal v2.4 全量 · {self.cfg['workers']}请求并发",updated_unix=time.time(),
            pid=os.getpid(),round=self.round,halt_reason=scheduler.HALT_REASON,limits=self.limiter.snapshot(),
            prompt_version=pilot.PROMPT_VERSION,annotation_schema_version=pilot.SCHEMA_VERSION,ontology_version=pilot.ONTOLOGY_VERSION,
            actual_input_mode='joint_text_audio_video_single_request',human_gold_audit_completed=False,full_dataset_started=True)
        dump(self.root/'status.json',r);dump(self.root/'summary.json',r);return r
    def run(self):
        for ri in (1,2):
            self.round=ri
            if ri==2:
                if HALT.is_set():break
                n=self.queue.recover_retries()
                if not n:break
                self.log(dict(phase='retry_failed_tasks',count=n));self.sleep(30)
            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
                futures={}
                while True:
                    self.refresh_runtime()
                    with self.queue.lock:pending=self.queue.db.execute("SELECT count(*) FROM tasks WHERE state='pending'").fetchone()[0]
                    if not HALT.is_set() and pending:
                        for slot in range(self.cfg['workers']):
                            if slot not in futures or futures[slot].done():
                                if slot in futures:futures[slot].result()
                                futures[slot]=pool.submit(self.worker,slot)
                    if not any(not f.done() for f in futures.values()) and (HALT.is_set() or not pending):break
                    self.status();time.sleep(1 if HALT.is_set() else 5)
                for f in futures.values():f.result()
        phase='stopped' if HALT.is_set() else 'complete' if self.queue.snapshot()['successful_samples']==len(self.samples) else 'complete_with_failures'
        result=self.status(phase)
        if not HALT.is_set():export(self.root,self.samples,self.queue)
        return result

def export(root,samples,queue):
    root=Path(root);temp=root/'labels.csv.tmp'
    with queue.lock:task_states={r['sid']:r['state'] for r in queue.db.execute('SELECT sid,state FROM tasks')}
    fields=['sample_id','source_group_id','source_video_id','data_role','dimension_id','state','valid','evidence','evidence_modalities','unknown_reason',
        'request_status','prompt_version','annotation_schema_version','ontology_version','teacher_model']
    with temp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for s in samples:
            sid=s['sample_id'];p=root/'annotations'/f'{sid}.json'
            if p.exists():
                r=load(p);ds=pilot.validate(json.dumps(r['annotation']))['dimensions'];status='ok'
            else:
                ds=[dict(dimension_id=d,state='',valid='',evidence='',evidence_modalities=[],unknown_reason='') for d in pilot.DIMS]
                status='technical_failure' if task_states.get(sid)=='failed' or (root/'failed'/f'{sid}.json').exists() else 'pending'
            for d in ds:w.writerow(dict(sample_id=sid,source_group_id=s['source_group_id'],source_video_id=s['source_video_id'],data_role=s['data_role'],
                **{**d,'evidence_modalities':'|'.join(d['evidence_modalities'])},request_status=status,prompt_version=pilot.PROMPT_VERSION,
                annotation_schema_version=pilot.SCHEMA_VERSION,ontology_version=pilot.ONTOLOGY_VERSION,teacher_model=media.MODEL))
    temp.replace(root/'labels.csv')
    with queue.lock:failures=[dict(r) for r in queue.db.execute("SELECT sid AS sample_id,state,attempts,retryable,last_error FROM tasks WHERE state!='succeeded'")]
    tmp=root/'failures.csv.tmp'
    with tmp.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['sample_id','state','attempts','retryable','last_error']);w.writeheader();w.writerows(failures)
    tmp.replace(root/'failures.csv')
    dump(root/'export_status.json',dict(updated_unix=time.time(),rows=len(samples)*6,successful_samples=queue.snapshot()['successful_samples']))

def launch():
    print('READY_FOR_API_KEY',flush=True);key=os.environ.get('QWEN_API_KEY') or sys.stdin.readline().strip();assert key
    log=(ROOT/'execution.log').open('a')
    proc=subprocess.Popen([sys.executable,'-u',str(Path(__file__).resolve()),'--run'],stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,
        start_new_session=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    proc.stdin.write((key+'\n').encode());proc.stdin.close();log.close()
    dump(ROOT/'launch.json',dict(pid=proc.pid,started_unix=time.time(),credential_delivery='anonymous_stdin_pipe_in_memory',detached=True))
    print('DETACHED_RUNNER_STARTED',proc.pid,flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--launch',action='store_true')
    ap.add_argument('--run',action='store_true');ap.add_argument('--status',action='store_true');ap.add_argument('--export',action='store_true');args=ap.parse_args()
    if args.status:print((ROOT/'status.json').read_text());return
    if args.launch:launch();return
    ROOT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        samples,protocol,cfg,prompt=prepare()
        if args.prepare:
            q=JointQueue(ROOT);r=q.snapshot();r.update(total_samples=len(samples),total_tasks=len(samples),expected_dimensions=len(samples)*6,
                phase='prepared',complete=False,test_complete=False,full_dataset_started=True,updated_unix=time.time(),run_id=ROOT.name)
            dump(ROOT/'status.json',r);dump(ROOT/'summary.json',r);print('PREPARED',len(samples));return
        if args.export:q=JointQueue(ROOT);export(ROOT,samples,q);return
        for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,lambda n,f:scheduler.stop('Stop signal received; checkpoint preserved'))
        print('READY_FOR_API_KEY',flush=True);key=os.environ.get('QWEN_API_KEY') or sys.stdin.readline().strip();assert key,'Missing API credential'
        runner=Runner(ROOT,samples,protocol,cfg,prompt,key)
        dump(ROOT/'runner.pid.json',dict(pid=os.getpid(),started_unix=time.time()))
        result=runner.run();print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
