"""Read-only appraisal routes mounted on the existing Cue viewer."""
import json, mimetypes, re, subprocess, threading, os, sqlite3, csv, io
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
BASE=Path(__file__).resolve().parent
CURRENT=BASE/'runs/current.json'
RUN_ID=os.environ.get('APPRAISAL_RUN_ID') or (json.loads(CURRENT.read_text())['run_id'] if CURRENT.exists() else 'pilot30')
assert RUN_ID in {'pilot30','pilot30_v2_4','mercaptionplus_v2_4'}
RUN=BASE/'runs'/RUN_ID
ASSETS=BASE/'viewer'
CUE=BASE.parent/'cue_annotation/viewer'
router=APIRouter(prefix='/appraisal')
_lock=threading.Lock()

def read(p):return json.loads(p.read_text())
@lru_cache(maxsize=1)
def context():
    samples=read(RUN/'samples.json')
    pointer=BASE.parent/'cue_student/artifacts/current_release.json'
    if RUN_ID=='mercaptionplus_v2_4' and pointer.exists():
        current=read(pointer)
        roles={m['sample_id']:m['role'] for m in read(Path(current['path'])/'members.json')}
        assert set(roles)=={s['sample_id'] for s in samples}
        for s in samples:
            s['annotation_snapshot_role']=s['data_role']
            s['data_role']=roles[s['sample_id']]
            s['data_release_id']=current['release_id']
    return samples,{s['sample_id']:s for s in samples}
def sample(sid):
    _,idx=context()
    if sid not in idx:raise HTTPException(404,'样本不在当前 appraisal 清单中')
    return idx[sid]
def record(sid):
    p=RUN/'annotations'/f'{sid}.json'
    if not p.exists():return None
    rec=read(p)
    current=sample(sid)
    if rec.get('data_role')!=current['data_role']:
        rec['annotation_snapshot_role']=rec.get('data_role')
        rec['data_role']=current['data_role']
    if 'data_release_id' in current:rec['data_release_id']=current['data_release_id']
    return rec

@router.get('')
@router.get('/')
def page():return FileResponse(ASSETS/'index.html',media_type='text/html')
@router.get('/assets/{name}')
def asset(name:str):
    if name not in {'app.js','style.css'}:raise HTTPException(404)
    return FileResponse(ASSETS/name)
def summary():
    path=RUN/'status.json'
    return read(path) if path.exists() else read(RUN/'summary.json')

@router.get('/api/full-progress')
def full_progress():
    result=summary()
    pid=result.get('pid')
    try:os.kill(int(pid),0);result['runner_alive']=True
    except (OSError,TypeError,ValueError):result['runner_alive']=False
    return result

@router.get('/api/bootstrap')
def bootstrap(q:str='',status:str='all',offset:int=0,limit:int=100):
    samples,index=context();items=[]
    if RUN_ID=='mercaptionplus_v2_4':
        limit=max(1,min(200,limit));offset=max(0,offset)
        clauses=[];args=[]
        if q:clauses.append('search_text LIKE ?');args.append('%'+q+'%')
        if status=='ok':clauses.append("state='succeeded'")
        elif status=='technical_failure':clauses.append("state='failed'")
        elif status=='pending':clauses.append("state IN ('pending','running')")
        elif status=='invalid':clauses.append("state='succeeded' AND invalid_dimensions>0")
        elif status!='all':raise HTTPException(400,'未知筛选状态')
        where=' WHERE '+' AND '.join(clauses) if clauses else ''
        db=sqlite3.connect('file:'+str(RUN/'tasks.sqlite3')+'?mode=ro',uri=True,timeout=10)
        try:
            count=db.execute('SELECT count(*) FROM tasks'+where,args).fetchone()[0]
            ids=[r[0] for r in db.execute('SELECT sid FROM tasks'+where+' ORDER BY rowid LIMIT ? OFFSET ?',args+[limit,offset])]
        finally:db.close()
        shown=[index[sid] for sid in ids]
    else:shown=samples;count=len(samples);offset=0;limit=len(samples)
    for sample in shown:
        rec=record(sample['sample_id']);failed=RUN/'failed'/f"{sample['sample_id']}.json"
        items.append(dict(id=sample['sample_id'],text=sample['text'],role=sample['data_role'],
            status='ok' if rec else 'technical_failure' if failed.exists() else 'pending',
            valid_count=sum(d['valid'] for d in rec['annotation']['dimensions']) if rec else 0,
            dimensions=rec['annotation']['dimensions'] if rec else []))
    protocol={k:v for k,v in read(RUN/'protocol.json').items() if k!='sample_ids'}
    return dict(run_id=RUN_ID,full_run=RUN_ID=='mercaptionplus_v2_4',samples=items,summary=summary(),protocol=protocol,
        ontology=read(RUN/'ontology.json'),total_matches=count,offset=offset,page_size=limit,has_more=offset+len(items)<count)

@router.get('/api/samples/{sid}')
def detail(sid:str):
    s=sample(sid);rec=record(sid);failed=RUN/'failed'/f'{sid}.json'
    meta_path=RUN/'inputs'/f'{sid}.joint.json'
    if meta_path.exists():meta=read(meta_path)
    else:
        vm=read(BASE.parent/'cue_annotation/runs/mercaptionplus/inputs'/f'{sid}.video_file.json')
        meta=dict(input_pending=True,audio=dict(duration_sec=s.get('audio_duration',0)),
            video=vm,prompt_version='appraisal_teacher_v2.4')
    raw=None
    if rec:
        p=RUN/'teacher_raw'/f"{sid}.attempt{rec['api']['attempt']}.json"
        raw=read(p)
    elif failed.exists():
        attempts=read(failed).get('errors',[])
        if attempts:
            p=RUN/'teacher_raw'/f"{sid}.attempt{attempts[-1]['attempt']}.json"
            if p.exists():raw=read(p)
    return dict(sample=s,record=rec,input_metadata=meta,raw_response=raw,
        failure=read(failed) if failed.exists() else None,
        media=dict(audio=f'/appraisal/media/{sid}/audio',video=f'/appraisal/media/{sid}/preview',
            teacher_video=f'/appraisal/media/{sid}/video'))
def successful_samples():
    samples,index=context()
    if RUN_ID!='mercaptionplus_v2_4':return samples
    db=sqlite3.connect('file:'+str(RUN/'tasks.sqlite3')+'?mode=ro',uri=True,timeout=10)
    try:ids=[row[0] for row in db.execute("SELECT sid FROM tasks WHERE state='succeeded' ORDER BY rowid")]
    finally:db.close()
    return [index[sid] for sid in ids]

@router.get('/api/export/{name}')
def export(name:str):
    if name=='annotations.json':
        def records():
            yield '[';first=True
            for sample in successful_samples():
                rec=record(sample['sample_id'])
                if rec:
                    yield ('' if first else ',')+json.dumps(rec,ensure_ascii=False)
                    first=False
            yield ']'
        return StreamingResponse(records(),media_type='application/json',
            headers={'Content-Disposition':f'attachment; filename="appraisal_{RUN_ID}.annotations.json"'})
    if name=='labels.csv' and not (RUN/name).exists() and RUN_ID=='mercaptionplus_v2_4':
        def rows():
            buffer=io.StringIO();fields=['sample_id','dimension_id','state','valid','evidence','evidence_modalities','unknown_reason',
                'request_status','prompt_version','annotation_schema_version','ontology_version']
            writer=csv.DictWriter(buffer,fieldnames=fields);writer.writeheader();yield '\ufeff'+buffer.getvalue();buffer.seek(0);buffer.truncate(0)
            for sample in successful_samples():
                rec=record(sample['sample_id'])
                if not rec:continue
                for d in rec['annotation']['dimensions']:
                    writer.writerow(dict(sample_id=sample['sample_id'],**{**d,'evidence_modalities':'|'.join(d['evidence_modalities'])},
                        request_status='ok',prompt_version=rec['versions']['prompt_version'],
                        annotation_schema_version=rec['versions']['annotation_schema_version'],ontology_version=rec['versions']['ontology_version']))
                yield buffer.getvalue();buffer.seek(0);buffer.truncate(0)
        return StreamingResponse(rows(),media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition':f'attachment; filename="appraisal_{RUN_ID}.current_successes.csv"'})
    if name not in {'labels.csv','summary.json','protocol.json'}:raise HTTPException(404)
    p=RUN/name
    if not p.is_file():raise HTTPException(404,'尚无结果')
    return FileResponse(p,filename='appraisal_'+RUN_ID+'.'+name)

def stream(path,request):
    if not path.is_file():raise HTTPException(404,'媒体不存在')
    size=path.stat().st_size;start,end,status=0,size-1,200
    headers={'Accept-Ranges':'bytes'}
    val=request.headers.get('range')
    if val:
        m=re.fullmatch(r'bytes=(\d*)-(\d*)',val)
        if not m or not any(m.groups()):return Response(status_code=416,headers={'Content-Range':f'bytes */{size}'})
        a,b=m.groups()
        if a:start=int(a);end=min(int(b),end) if b else end
        else:start=max(0,size-int(b))
        if start>end or start>=size:return Response(status_code=416,headers={'Content-Range':f'bytes */{size}'})
        status=206;headers['Content-Range']=f'bytes {start}-{end}/{size}'
    headers['Content-Length']=str(end-start+1)
    mime=mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
    if request.method=='HEAD':return Response(status_code=status,headers=headers,media_type=mime)
    def chunks():
        with path.open('rb') as f:
            f.seek(start);left=end-start+1
            while left:
                b=f.read(min(left,262144))
                if not b:break
                left-=len(b);yield b
    return StreamingResponse(chunks(),status_code=status,headers=headers,media_type=mime)

@router.api_route('/media/{sid}/{kind}',methods=['GET','HEAD'])
def media(sid:str,kind:str,request:Request):
    source_sample=sample(sid)
    paths={'audio':RUN/'media/audio'/f'{sid}.wav','video':RUN/'media/video'/f'{sid}.mp4'}
    if kind=='preview':
        path=CUE/'cache/videos'/f'{sid}.mp4'
        source=paths['video'] if paths['video'].exists() else Path(source_sample['video_path'])
        with _lock:
            if not path.exists():
                path.parent.mkdir(parents=True,exist_ok=True)
                temp=path.with_name(path.stem+'.appraisal.tmp.mp4')
                subprocess.run(['/ai/sjq/miniconda3/envs/talkinghead/bin/ffmpeg','-hide_banner','-loglevel','error',
                    '-nostdin','-y','-i',str(source),'-map','0:v:0','-an','-c:v','libx264','-crf','18',
                    '-preset','fast','-pix_fmt','yuv420p','-vsync','0','-threads','2','-movflags','+faststart',str(temp)],
                    check=True,timeout=120)
                temp.replace(path)
    elif kind in paths:
        path=paths[kind]
        if kind=='audio' and not path.exists():path=Path(source_sample['audio_path'])
    else:raise HTTPException(404)
    return stream(path,request)
