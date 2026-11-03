"""Joint Text/Audio/Video Appraisal Teacher pilot; all artifacts remain on server."""
import argparse, base64, copy, csv, fcntl, hashlib, json, os, re, sys, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent
sys.path.insert(0,str(PROJECT/'cue_annotation'))
import annotate_api as cue
ROOT=BASE/'runs/pilot30'
CUE_ROOT=PROJECT/'cue_annotation/runs/pilot30'
RELEASE=PROJECT/'cue_student/artifacts/release_strict_all_modalities_20261020_163131'
DIMS={
'APP_GOAL_RELEVANCE':['AGR_RELEVANT','AGR_IRRELEVANT'],
'APP_GOAL_CONGRUENCE':['AGC_CONGRUENT','AGC_INCONGRUENT','AGC_MIXED'],
'APP_EXPECTEDNESS':['AEX_EXPECTED','AEX_UNEXPECTED'],
'APP_AGENCY':['AAG_SELF','AAG_OTHER','AAG_CIRCUMSTANCE','AAG_SHARED'],
'APP_CERTAINTY':['ACT_CERTAIN','ACT_UNCERTAIN'],
'APP_COPING_POTENTIAL':['ACP_HIGH','ACP_LOW','ACP_MIXED']}
REASONS={'focus_person_ambiguous','focus_person_not_identifiable','goal_not_identifiable','event_goal_relation_unclear','prior_expectation_not_identifiable','causal_attribution_ambiguous','certainty_not_expressed','coping_evidence_absent','conflicting_evidence','insufficient_evidence','dimension_not_applicable'}
PROMPT_VERSION='appraisal_teacher_v2.3'
ONTOLOGY_VERSION='appraisal_ontology_v2.3'
sha=cue.sha
dump=cue.dump

def load(path):return json.loads(Path(path).read_text())
def frozen(path,value):
    if path.exists():assert load(path)==value,'Frozen artifact differs: '+str(path)
    else:dump(path,value)

def setup():
    for d in ['annotations','teacher_raw','inputs','failed','prompts','media/audio','media/video']:
        (ROOT/d).mkdir(parents=True,exist_ok=True)
    doc=(PROJECT/'图构建.md').read_text()
    match=re.search(r'\x60\x60\x60 text\n(# Appraisal Teacher v2\.3.*?)\n\x60\x60\x60',doc,re.S)
    assert match,'Document prompt block not found'
    prompt=match.group(1)+'\n'
    dest=ROOT/'prompts/appraisal_teacher_v2.3.txt'
    if dest.exists():assert dest.read_text()==prompt,'Frozen prompt changed'
    else:dest.write_text(prompt)
    old=load(CUE_ROOT/'samples.json')
    members={s['sample_id']:s for s in load(RELEASE/'members.json')}
    samples=[]
    for s in old:
        sid=s['sample_id'];m=members[sid]
        # Only raw fields and provenance; never include Cue annotations or target descriptions.
        samples.append(dict(sample_id=sid,text={k:s['text'].get(k,'') for k in ['chinese','english']},
            audio_path=s['audio_path'],video_path=s['video_path'],source_group_id=m['group_id'],
            source_video_id=s.get('video_source_id'),source_status=m['source_status'],data_role=m['role']))
    assert len(samples)==30 and len({s['sample_id'] for s in samples})==30
    protocol=dict(prompt_version=PROMPT_VERSION,ontology_version=ONTOLOGY_VERSION,prompt_sha256=sha(prompt.encode()),
        source_document_sha256=sha((PROJECT/'图构建.md').read_bytes()),model_requested=cue.MODEL,endpoint=cue.ENDPOINT,
        generation=load(CUE_ROOT/'protocol.json')['generation'],workers=3,maximum_attempts=3,
        actual_input_mode='joint_text_audio_video_single_request',sample_ids=[s['sample_id'] for s in samples],
        cue_input_protocol_sha256=sha((CUE_ROOT/'protocol.json').read_bytes()),
        release_id=load(RELEASE/'manifest.json')['release_id'],
        group_limitations=load(RELEASE/'manifest.json')['group_limitations'],
        human_gold_audit_completed=False,full_dataset_started=False,labels_postprocessing='none')
    frozen(ROOT/'protocol.json',protocol)
    frozen(ROOT/'ontology.json',dict(version=ONTOLOGY_VERSION,dimensions=DIMS,unknown_reason_codes=sorted(REASONS)))
    frozen(ROOT/'samples.json',samples)
    cue.RUN=ROOT
    return samples,protocol,prompt

def validate(raw):
    obj=json.loads(raw,object_pairs_hook=cue.unique)
    assert set(obj)=={'focus_person','event_context','dimensions'},'Root fields'
    f=obj['focus_person']
    assert set(f)=={'status','description'} and f['status'] in {'identified','ambiguous','not_identifiable'}
    assert isinstance(f['description'],str) and isinstance(obj['event_context'],str)
    ds=obj['dimensions']
    assert isinstance(ds,list) and len(ds)==6
    assert {d['dimension_id'] for d in ds}==set(DIMS),'Missing/duplicate dimensions'
    for d in ds:
        assert set(d)=={'dimension_id','state','valid','evidence','evidence_modalities','unknown_reason'}, 'Dimension fields differ: '+d['dimension_id']
        assert type(d['valid']) is bool and isinstance(d['evidence'],str) and isinstance(d['evidence_modalities'],list)
        mods=d['evidence_modalities'];assert len(mods)==len(set(mods)) and set(mods)<= {'text','audio','video'}
        if d['valid']:
            assert d['state'] in DIMS[d['dimension_id']] and d['evidence'].strip() and mods and d['unknown_reason'] is None
        else:
            assert d['state'] is None and d['evidence']=='' and mods==[] and d['unknown_reason'] in REASONS, 'Invalid dimension requires JSON null, empty evidence/modalities, documented reason: '+d['dimension_id']
    return obj

def prepare(s):
    sid=s['sample_id']
    # Reuse the exact historic complete inputs by server-side hardlinks.
    a=CUE_ROOT/'media/audio'/f'{sid}.wav';v=CUE_ROOT/'media/video'/f'{sid}.mp4'
    ap=ROOT/'media/audio'/a.name;vp=ROOT/'media/video'/v.name
    for source,target in [(a,ap),(v,vp)]:
        assert source.is_file(),'Missing original Cue pilot input: '+str(source)
        if not target.exists():os.link(source,target)
        assert sha(source.read_bytes())==sha(target.read_bytes())
    vm=load(CUE_ROOT/'inputs'/f'{sid}.video_file.json')
    assert sha(vp.read_bytes())==vm['submitted_video_sha256']
    # Required by reused Cue preparation helpers; archive the same preprocessing facts.
    vm=copy.deepcopy(vm);vm['submitted_video_path']=str(vp)
    frozen(ROOT/'inputs'/f'{sid}.video_file.json',vm)
    import soundfile as sf
    info=sf.info(str(ap));assert info.samplerate==16000 and info.channels==1
    actual=cue.video_info(vp)
    assert actual['audio_streams']==0
    assert actual['video_packets']==vm['source_video']['video_packets']
    assert all(actual[k]==vm['submitted_video'][k] for k in ['width','height','fps'])
    return ap,vp,vm,info

def build(s,protocol,prompt):
    ap,vp,vm,ai=prepare(s)
    runtime=dict(sample_id=s['sample_id'],available_modalities=['text','audio','video'],
        text={k:s['text'].get(k,'') for k in ['chinese','english']},
        audio=dict(mode='complete_continuous_wav',sample_rate=16000,channels=1,duration_sec=ai.duration),
        video=dict(mode='complete_silent_video_file',duration_sec=vm['submitted_video']['duration'],
            client_frame_sampling=False,client_temporal_truncation=False,client_spatial_resize=False,server_processing='provider_default'))
    content=[dict(type='text',text=prompt+'\nRuntime input:\n'+json.dumps(runtime,ensure_ascii=False)),
        dict(type='input_audio',input_audio=dict(data='data:audio/wav;base64,'+base64.b64encode(ap.read_bytes()).decode(),format='wav')),
        dict(type='video_url',video_url=dict(url='data:video/mp4;base64,'+base64.b64encode(vp.read_bytes()).decode()))]
    payload=dict(model=cue.MODEL,messages=[dict(role='user',content=content)],**protocol['generation'])
    data=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode()
    meta=dict(sample_id=s['sample_id'],actual_input_mode='joint_text_audio_video_single_request',
        request_content_types=[c['type'] for c in content],available_modalities=['text','audio','video'],
        available_modality_mask={'text':True,'audio':True,'video':True},actual_text_fields=runtime['text'],
        submitted_audio_path=str(ap),submitted_audio_sha256=sha(ap.read_bytes()),audio=runtime['audio'],
        submitted_video_path=str(vp),submitted_video_sha256=sha(vp.read_bytes()),video=vm,
        media_preprocessing_version='cue_qwen_omni_api_exact_pilot30_inputs',
        same_audio_as_cue=True,same_video_as_cue=True,request_sha256=sha(data),request_bytes=len(data),
        source_group_id=s['source_group_id'],source_video_id=s['source_video_id'],data_role=s['data_role'],
        source_status=s['source_status'],source_audio_path=s['audio_path'],source_video_path=s['video_path'],
        prompt_version=PROMPT_VERSION,prompt_sha256=protocol['prompt_sha256'],ontology_version=ONTOLOGY_VERSION,
        forbidden_inputs_included=False,provider_internal_coverage_verified=False)
    frozen(ROOT/'inputs'/f"{s['sample_id']}.joint.json",meta)
    return data,meta

def summarize(samples,protocol):
    rows=[];counts=Counter();valid=Counter();unknown=Counter();usage=Counter();returned=Counter()
    for s in samples:
        sid=s['sample_id'];path=ROOT/'annotations'/f'{sid}.json'
        if not path.exists():
            counts['failed' if (ROOT/'failed'/f'{sid}.json').exists() else 'pending']+=1
            continue
        rec=load(path);a=validate(json.dumps(rec['annotation']));counts['ok']+=1
        returned[rec['api'].get('model_returned')]+=1
        for k,v in (rec['api'].get('usage') or {}).items():
            if isinstance(v,(int,float)):usage[k]+=v
        for d in a['dimensions']:
            valid[d['dimension_id']]+=int(d['valid'])
            if not d['valid']:unknown[d['unknown_reason']]+=1
            rows.append(dict(sample_id=sid,source_group_id=s['source_group_id'],source_video_id=s['source_video_id'],
                data_role=s['data_role'],**{**d,'evidence_modalities':'|'.join(d['evidence_modalities'])},
                prompt_version=PROMPT_VERSION,ontology_version=ONTOLOGY_VERSION,teacher_model=rec['api'].get('model_returned')))
    if rows:
        tmp=ROOT/'labels.csv.tmp'
        with tmp.open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        tmp.replace(ROOT/'labels.csv')
    total=len(samples);ok=counts['ok']
    summary=dict(total_samples=total,expected_dimensions=total*6,successful_samples=ok,counts=dict(counts),
        dimension_rows=len(rows),valid_dimension_count=sum(valid.values()),invalid_dimension_count=len(rows)-sum(valid.values()),
        per_dimension={d:dict(valid=valid[d],invalid=ok-valid[d],valid_coverage=valid[d]/ok if ok else None) for d in DIMS},
        unknown_reason_counts=dict(unknown),successful_usage=dict(usage),model_returned_counts=dict(returned),
        complete=ok==total,actual_input_mode=protocol['actual_input_mode'],model_requested=cue.MODEL,
        prompt_version=PROMPT_VERSION,ontology_version=ONTOLOGY_VERSION,human_gold_audit_completed=False,
        full_dataset_started=False,updated_unix=time.time())
    attempts=[load(p) for p in (ROOT/'teacher_raw').glob('*.json')]
    attempt_usage=Counter()
    for attempt in attempts:
        for k in ['prompt_tokens','completion_tokens','total_tokens']:
            attempt_usage[k]+=(attempt.get('response',{}).get('usage') or {}).get(k,0)
    summary.update(attempt_records=len(attempts),attempt_status_counts=dict(Counter(
        'success' if a.get('http_status')==200 and a.get('json_parse_status')=='valid' else
        'schema_failure' if a.get('http_status')==200 else 'network_or_api_failure' for a in attempts)),
        usage_including_failed_generations=dict(attempt_usage))
    dump(ROOT/'summary.json',summary)
    summary['tested_samples']=ok+counts['failed']
    summary['test_complete']=summary['tested_samples']==total
    phase='complete_pending_human_audit' if ok==total else 'completed_with_technical_failures' if summary['test_complete'] else 'awaiting_or_running'
    summary['phase']=phase
    dump(ROOT/'summary.json',summary)
    dump(ROOT/'status.json',summary)
    return summary

def one(s,protocol,prompt,key):
    import requests
    sid=s['sample_id'];dest=ROOT/'annotations'/f'{sid}.json'
    if dest.exists():validate(json.dumps(load(dest)['annotation']));return dict(sample_id=sid,status='cached')
    data,meta=build(s,protocol,prompt)
    previous=[int(p.stem.rsplit('attempt',1)[1]) for p in (ROOT/'teacher_raw').glob(f'{sid}.attempt*.json')]
    errors=[]
    for attempt in range(max(previous,default=0)+1,max(previous,default=0)+4):
        started=time.time();result=dict(sample_id=sid,attempt=attempt,request_sha256=meta['request_sha256'],
            model_requested=cue.MODEL,endpoint=cue.ENDPOINT,started_unix=started,json_parse_status='not_attempted')
        fatal=False
        try:
            proxy=os.getenv('QWEN_HTTPS_PROXY')
            r=requests.post(cue.ENDPOINT,data=data,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
                timeout=(20,180),allow_redirects=False,proxies={'http':proxy,'https':proxy} if proxy else None)
            text=r.text.replace(key,'[REDACTED]')
            result.update(http_status=r.status_code,seconds=time.time()-started,
                request_id=r.headers.get('x-request-id') or r.headers.get('request-id'))
            try:result['response']=json.loads(text)
            except ValueError:result['response_text']=text[:20000]
            if r.status_code!=200:
                fatal=r.status_code in [400,401,402,403,404,413,422]
                raise RuntimeError('HTTP '+str(r.status_code)+': '+text[:1500])
            response=result['response'];choice=response['choices'][0]
            assert choice['finish_reason']=='stop','Incomplete response: '+str(choice['finish_reason'])
            result['json_parse_status']='validating'
            annotation=validate(choice['message']['content'])
            result['json_parse_status']='valid'
            dump(ROOT/'teacher_raw'/f'{sid}.attempt{attempt}.json',result)
            rec=dict(status='ok',sample_id=sid,source_group_id=s['source_group_id'],source_video_id=s['source_video_id'],
                data_role=s['data_role'],annotation=annotation,meta=meta,versions=dict(prompt_version=PROMPT_VERSION,
                ontology_version=ONTOLOGY_VERSION,prompt_sha256=protocol['prompt_sha256']),
                api=dict(model_requested=cue.MODEL,model_returned=response.get('model'),response_id=response.get('id'),
                    usage=response.get('usage'),attempt=attempt,retry_count=attempt-1,seconds=result['seconds'],json_parse_status='valid'))
            dump(dest,rec);(ROOT/'failed'/f'{sid}.json').unlink(missing_ok=True)
            return dict(sample_id=sid,status='ok',seconds=result['seconds'])
        except Exception as exc:
            error=(type(exc).__name__+': '+str(exc)).replace(key,'[REDACTED]')
            result.update(error=error,seconds=time.time()-started)
            if result['json_parse_status']=='validating':result['json_parse_status']='invalid'
            dump(ROOT/'teacher_raw'/f'{sid}.attempt{attempt}.json',result)
            errors.append(dict(attempt=attempt,error=error,json_parse_status=result['json_parse_status']))
            if fatal:break
            time.sleep(2)
    failure=dict(sample_id=sid,status='technical_failure',errors=errors,semantic_unknown=False)
    dump(ROOT/'failed'/f'{sid}.json',failure);return failure

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');ap.add_argument('--summarize',action='store_true')
    ap.add_argument('--first',action='store_true');args=ap.parse_args()
    samples,protocol,prompt=setup()
    if args.preflight:
        checks=[]
        for s in samples:
            data,meta=build(s,protocol,prompt)
            checks.append(dict(sample_id=s['sample_id'],request_bytes=len(data),content_types=meta['request_content_types'],
                same_audio_as_cue=meta['same_audio_as_cue'],same_video_as_cue=meta['same_video_as_cue']))
        dump(ROOT/'preflight.json',dict(passed=True,samples=checks,api_called=False))
        print(json.dumps(summarize(samples,protocol),ensure_ascii=False));return
    if args.summarize:print(json.dumps(summarize(samples,protocol),ensure_ascii=False));return
    lock=(ROOT/'runner.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    print('READY_FOR_API_KEY',flush=True)
    key=os.getenv('QWEN_API_KEY') or sys.stdin.readline().strip();assert key,'Missing API credential'
    pending=[s for s in samples if not (ROOT/'annotations'/f"{s['sample_id']}.json").exists()]
    if pending:
        # Gate only a new run; resumed runs already have a successful joint request.
        if not any((ROOT/'annotations'/f"{s['sample_id']}.json").exists() for s in samples):
            first=one(pending[0],protocol,prompt,key);print(json.dumps(first,ensure_ascii=False),flush=True)
            summarize(samples,protocol)
            if first['status']!='ok':raise SystemExit('Joint-input capability gate failed; remaining samples not submitted')
            pending=pending[1:]
            if args.first:return
        elif args.first:pending=pending[:1]
        with ThreadPoolExecutor(max_workers=protocol['workers']) as pool:
            for f in as_completed([pool.submit(one,s,protocol,prompt,key) for s in pending]):
                print(json.dumps(f.result(),ensure_ascii=False),flush=True);summarize(samples,protocol)
    result=summarize(samples,protocol);print(json.dumps(result,ensure_ascii=False),flush=True)
    if not result['complete']:raise SystemExit(1)
if __name__=='__main__':main()
