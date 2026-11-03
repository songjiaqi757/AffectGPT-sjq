"""Read-only appraisal routes mounted on the existing Cue viewer."""
import json, mimetypes, re, subprocess, threading
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
BASE=Path(__file__).resolve().parent
RUN=BASE/'runs/pilot30'
ASSETS=BASE/'viewer'
CUE=BASE.parent/'cue_annotation/viewer'
router=APIRouter(prefix='/appraisal')
_lock=threading.Lock()

def read(p):return json.loads(p.read_text())
def context():
    samples=read(RUN/'samples.json')
    return samples,{s['sample_id']:s for s in samples}
def sample(sid):
    _,idx=context()
    if sid not in idx:raise HTTPException(404,'样本不在 appraisal 30 条清单中')
    return idx[sid]
def record(sid):
    p=RUN/'annotations'/f'{sid}.json'
    return read(p) if p.exists() else None

@router.get('')
@router.get('/')
def page():return FileResponse(ASSETS/'index.html',media_type='text/html')
@router.get('/assets/{name}')
def asset(name:str):
    if name not in {'app.js','style.css'}:raise HTTPException(404)
    return FileResponse(ASSETS/name)
@router.get('/api/bootstrap')
def bootstrap():
    samples,_=context();items=[]
    for s in samples:
        rec=record(s['sample_id']);failed=RUN/'failed'/f"{s['sample_id']}.json"
        items.append(dict(id=s['sample_id'],text=s['text'],role=s['data_role'],
            status='ok' if rec else 'technical_failure' if failed.exists() else 'pending',
            valid_count=sum(d['valid'] for d in rec['annotation']['dimensions']) if rec else 0,
            dimensions=rec['annotation']['dimensions'] if rec else []))
    return dict(samples=items,summary=read(RUN/'summary.json'),protocol=read(RUN/'protocol.json'),
        ontology=read(RUN/'ontology.json'))
@router.get('/api/samples/{sid}')
def detail(sid:str):
    s=sample(sid);rec=record(sid);failed=RUN/'failed'/f'{sid}.json'
    meta=read(RUN/'inputs'/f'{sid}.joint.json')
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
@router.get('/api/export/{name}')
def export(name:str):
    if name=='annotations.json':
        samples,_=context()
        return Response(json.dumps([record(s['sample_id']) for s in samples if record(s['sample_id'])],
            ensure_ascii=False,indent=2),media_type='application/json',
            headers={'Content-Disposition':'attachment; filename="appraisal_pilot30.annotations.json"'})
    if name not in {'labels.csv','summary.json','protocol.json'}:raise HTTPException(404)
    p=RUN/name
    if not p.is_file():raise HTTPException(404,'尚无结果')
    return FileResponse(p,filename='appraisal_pilot30.'+name)

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
    sample(sid)
    paths={'audio':RUN/'media/audio'/f'{sid}.wav','video':RUN/'media/video'/f'{sid}.mp4'}
    if kind=='preview':
        path=CUE/'cache/videos'/f'{sid}.mp4'
        with _lock:
            if not path.exists():
                path.parent.mkdir(parents=True,exist_ok=True)
                temp=path.with_name(path.stem+'.appraisal.tmp.mp4')
                subprocess.run(['/ai/sjq/miniconda3/envs/talkinghead/bin/ffmpeg','-hide_banner','-loglevel','error',
                    '-nostdin','-y','-i',str(paths['video']),'-map','0:v:0','-an','-c:v','libx264','-crf','18',
                    '-preset','fast','-pix_fmt','yuv420p','-vsync','0','-threads','2','-movflags','+faststart',str(temp)],
                    check=True,timeout=120)
                temp.replace(path)
    elif kind in paths:path=paths[kind]
    else:raise HTTPException(404)
    return stream(path,request)
