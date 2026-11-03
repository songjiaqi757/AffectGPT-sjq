"""Read-only remote annotation viewer; reachable through authenticated SSH forwarding."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, json, mimetypes, os, re, subprocess, threading
from uuid import uuid4
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from PIL import Image

BASE = Path(__file__).resolve().parent
RUN_ID="pilot30"
RUN_LABEL="Qwen3.8-Omni-Flash · 完整音视频 · 固定版"

@lru_cache(maxsize=1)
def run_context(run=""):
    if run and run!=RUN_ID:raise HTTPException(404,"该结果版本已删除；请打开当前固定版本")
    root=BASE.parent/'runs'/RUN_ID
    samples=json.loads((root/'samples.json').read_text())
    ontology=json.loads((root/'ontology.json').read_text())['cue_ids']
    rows=defaultdict(list)
    if (root/'labels.csv').is_file():
        with (root/'labels.csv').open(encoding='utf-8',newline='') as f:
            for original in csv.DictReader(f):
                row=dict(original);row['mask']=int(row['mask']);row['y']=int(row['y']) if row['y'] else None;rows[row['sample_id']].append(row)
    annotations={s['sample_id']:{m:json.loads((root/'annotations'/f"{s['sample_id']}.{m}.json").read_text()) for m in ontology if (root/'annotations'/f"{s['sample_id']}.{m}.json").is_file()} for s in samples}
    reviewed=sum(bool(a.get('visual',{}).get('human_review')) for a in annotations.values())
    audit=f"保留 {reviewed} 条人工流泪纠正；其余线索待人工复核" if any(annotations.values()) else "试标标签已删除；暂无标注结果"
    return dict(root=root,samples=samples,index={s['sample_id']:s for s in samples},ontology=ontology,rows=rows,
                annotations=annotations,audit=audit,source_count=json.loads((root/'dataset_manifest.json').read_text())['n_source'])

# Only the fixed sample manifest can supply media paths.
DEFAULT_CONTEXT=run_context()
RUN=DEFAULT_CONTEXT["root"]
SAMPLES=DEFAULT_CONTEXT["samples"]
INDEX=DEFAULT_CONTEXT["index"]
ROWS=DEFAULT_CONTEXT["rows"]
CUE_NAMES = {
"TXT_AFFECT_WORD_POSITIVE":"正向情感词","TXT_AFFECT_WORD_NEGATIVE":"负向情感词",
"TXT_EVALUATION_POSITIVE":"正向评价","TXT_EVALUATION_NEGATIVE":"负向评价",
"TXT_NEGATION_PRESENT":"否定表达","TXT_CONTRAST_PRESENT":"转折表达",
"TXT_INTENSIFIER_PRESENT":"程度强化词","TXT_UNCERTAINTY_HEDGE":"不确定／缓和表达",
"TXT_RHETORICAL_QUESTION":"反问","TXT_EXCLAMATION_INTERJECTION":"感叹／叹词",
"TXT_DESIRE_NEED":"愿望／需求","TXT_EXPLICIT_CAUSAL_ATTRIBUTION_SELF":"明确自我原因归因",
"TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER":"明确他人原因归因",
"TXT_EXPLICIT_SUCCESS_OUTCOME":"明确成功结果","TXT_EXPLICIT_FAILURE_LOSS_OUTCOME":"明确失败／损失结果",
"AUD_SPEECH_RATE_REL_FAST":"相对语速快","AUD_SPEECH_RATE_REL_SLOW":"相对语速慢",
"AUD_PITCH_LEVEL_REL_HIGH":"相对音高高","AUD_PITCH_LEVEL_REL_LOW":"相对音高低",
"AUD_VOCAL_INTENSITY_REL_HIGH":"相对音量高","AUD_VOCAL_INTENSITY_REL_LOW":"相对音量低",
"AUD_PITCH_VARIABILITY_HIGH":"音高变化大","AUD_PITCH_VARIABILITY_LOW":"音高变化小",
"AUD_PAUSE_LONG":"长停顿","AUD_PAUSE_FREQUENT":"频繁停顿",
"AUD_INTONATION_RISING":"升调","AUD_INTONATION_FALLING":"降调","AUD_INTONATION_FLAT":"平调",
"AUD_VOICE_TENSE":"声音紧张","AUD_VOICE_TREMBLING":"声音颤抖",
"AUD_LAUGHTER_PRESENT":"笑声","AUD_CRYING_SOBBING_PRESENT":"哭泣／啜泣",
"VIS_BROWS_FURROWED":"皱眉","VIS_BROWS_RAISED":"扬眉","VIS_EYES_WIDENED":"睁大眼睛",
"VIS_EYES_SQUINTED":"眯眼","VIS_SMILE_PRESENT":"微笑","VIS_MOUTH_CORNERS_DOWN":"嘴角下垂",
"VIS_LIPS_PRESSED":"抿嘴","VIS_GRIMACE_PRESENT":"面部扭曲","VIS_TEARING_PRESENT":"流泪","VIS_HEAD_LOWERED":"低头"}
STATES={"positive":"存在","negative":"未观察到","uncertain":"不确定","unobservable":"不可观测","unlabeled":"未标注"}
app=FastAPI(title="MER-Caption+ 标注查看器",docs_url=None,redoc_url=None,openapi_url=None)

@app.middleware("http")
async def headers(request:Request,call_next):
    res=await call_next(request)
    res.headers.update({"X-Content-Type-Options":"nosniff","Referrer-Policy":"same-origin","Cache-Control":"no-store",
                        "Content-Security-Policy":"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; media-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"})
    return res

def sample_or_404(sid):
    if sid not in INDEX: raise HTTPException(404,"样本不存在")
    return INDEX[sid]

@app.get("/")
def home(): return FileResponse(BASE/"index.html",media_type="text/html")

@app.get("/assets/{name}")
def asset(name:str):
    if name not in {"app.js","style.css","tearing.js","tearing.css"}: raise HTTPException(404)
    return FileResponse(BASE/name)

@app.get("/api/health")
def health(): return {"ok":True,"samples":len(INDEX),"cue_rows":sum(map(len,ROWS.values()))}

@app.get('/api/bootstrap')
def bootstrap(run:str=""):
    ctx=run_context(run);rows=ctx['rows']
    samples=[dict(id=s['sample_id'],text=s['text'],duration=s['audio']['duration'],
                  counts=dict(Counter(x['state'] for x in rows[s['sample_id']])),
                  review_count=sum(x['mask']==0 for x in rows[s['sample_id']]),cue_count=len(rows[s['sample_id']])) for s in ctx['samples']]
    return dict(samples=samples,cue_names=CUE_NAMES,states=STATES,modality_names={'text':'文本','audio':'音频','visual':'视觉'},
                counts=dict(Counter(x['state'] for r in rows.values() for x in r)),source_count=ctx['source_count'],cue_rows=sum(map(len,rows.values())),
                run_id=RUN_ID,run_label=RUN_LABEL,human_audit=ctx['audit'],model='Qwen3.8-Omni-Flash',completed_samples=sum(len(a)==3 for a in ctx['annotations'].values()),exports=['labels.csv'] if (ctx['root']/'labels.csv').is_file() else [])

@app.get('/api/samples/{sid}')
def detail(sid:str,run:str=""):
    ctx=run_context(run)
    if sid not in ctx['index']:raise HTTPException(404,'样本不存在')
    s=ctx['index'][sid];annotations=ctx['annotations'][sid]
    labels=[]
    for row in ctx['rows'][sid]:
        r=dict(row);r['name']=CUE_NAMES.get(r['cue_id'],r['cue_id'])
        r['human_review']=annotations.get('visual',{}).get('human_review') if r['cue_id']=='VIS_TEARING_PRESENT' else None
        r['quality_review']=annotations.get('visual',{}).get('quality_review') if r['cue_id']=='VIS_TEARING_PRESENT' else None
        labels.append(r)
    responses={m:json.loads((ctx['root']/'teacher_raw'/f"{sid}.{m}.attempt{int(record['api']['attempt'])}.json").read_text()) for m,record in annotations.items()}
    return dict(id=sid,text=s['text'],duration=s['audio']['duration'],
                media={'audio':f'/media/{sid}/audio','teacher_audio':f'/media/{sid}/teacher-audio','video':f'/media/{sid}/browser-video','teacher_video':f'/media/{sid}/teacher-video'},
                frames=[dict(slot=f['slot'],time=f['time_sec'],index=f['frame_index'],url=f"/media/{sid}/frame/{f['slot']}") for f in s['visual']['frames']],
                human_review=annotations.get('visual',{}).get('human_review'),labels=labels,annotations=annotations,teacher_responses=responses,
                provenance={'run':str(ctx['root']),'audio':s['audio_path'],'video':s['video_path'],'model':'Qwen3.8-Omni-Flash',
                            'text_input':'原始中文 + 英文字幕（独立字段）','audio_input':'完整连续音频 · 16 kHz · 单声道 · 无截断',
                            'visual_input':'完整静音视频文件，保留完整时长、原分辨率和帧率；1条作H.264兼容转码。客户端不抽帧、不缩放；服务端采用平台默认处理。',
                            'human_audit':ctx['audit']})

@app.get('/api/export/{name}')
def export(name:str,run:str=""):
    if name!='labels.csv':raise HTTPException(404)
    path=run_context(run)['root']/name
    if not path.is_file():raise HTTPException(404,'暂无标注结果')
    return FileResponse(path,media_type='text/csv; charset=utf-8',filename='pilot30.labels.csv')

def stream_media(path:Path,request:Request):
    if not path.is_file(): raise HTTPException(404,"媒体文件不存在")
    size=path.stat().st_size
    start,end,status=0,size-1,200
    hdrs={"Accept-Ranges":"bytes"}
    value=request.headers.get("range")
    if value:
        match=re.fullmatch(r"bytes=(\d*)-(\d*)",value)
        if not match or not any(match.groups()): return Response(status_code=416,headers={"Content-Range":f"bytes */{size}"})
        first,last=match.groups()
        if first:
            start=int(first);end=min(int(last),size-1) if last else size-1
        else:
            start=max(0,size-int(last));end=size-1
        if start>end or start>=size: return Response(status_code=416,headers={"Content-Range":f"bytes */{size}"})
        status=206;hdrs["Content-Range"]=f"bytes {start}-{end}/{size}"
    hdrs["Content-Length"]=str(end-start+1)
    mime="audio/wav" if path.suffix.lower()==".wav" else (mimetypes.guess_type(str(path))[0] or "application/octet-stream")
    if request.method=="HEAD": return Response(status_code=status,headers=hdrs,media_type=mime)
    def chunks():
        with path.open("rb") as f:
            f.seek(start);left=end-start+1
            while left:
                block=f.read(min(left,256*1024))
                if not block: break
                left-=len(block);yield block
    return StreamingResponse(chunks(),status_code=status,headers=hdrs,media_type=mime)

@app.api_route("/media/{sid}/{kind}",methods=["GET","HEAD"])
def media(sid:str,kind:str,request:Request):
    s=sample_or_404(sid)
    paths={"audio":s["audio_path"],"video":s["video_path"],"teacher-audio":str(RUN/"media/audio"/(sid+".wav")),"browser-video":str(BASE/"cache/videos"/(sid+".mp4")),"teacher-video":str(RUN/"media/video"/(sid+".mp4"))}
    if kind not in paths: raise HTTPException(404)
    return stream_media(Path(paths[kind]),request)

@app.get("/media/{sid}/frame/{slot}")
def frame(sid:str,slot:int):
    s=sample_or_404(sid);frames={f["slot"]:f for f in s["visual"]["frames"]}
    if slot not in frames: raise HTTPException(404)
    cache=BASE/"cache"/sid;cache.mkdir(parents=True,exist_ok=True)
    target=cache/(str(slot)+".jpg")
    if not target.is_file():
        with Image.open(frames[slot]["path"]) as im:
            im.thumbnail((640,400));temp=target.with_suffix(".tmp."+uuid4().hex)
            im.convert("RGB").save(temp,format="JPEG",quality=85);temp.replace(target)
    return FileResponse(target,media_type="image/jpeg")


@app.get("/media/{sid}/frame/{slot}/full")
def full_frame(sid:str,slot:int):
    s=sample_or_404(sid)
    frames={f["slot"]:f for f in s["visual"]["frames"]}
    if slot not in frames: raise HTTPException(404)
    path=Path(frames[slot]["path"])
    if not path.is_file(): raise HTTPException(404)
    return FileResponse(path,media_type="image/png")

@app.get('/api/pilot-progress')
def pilot_progress(run:str=""):
    ctx=run_context(run);status=json.loads((ctx['root']/'status.json').read_text());done=sum(len(a) for a in ctx['annotations'].values())
    return dict(available=True,run_id=RUN_ID,run_label=RUN_LABEL,counts={'done':done},completed_samples=sum(len(a)==3 for a in ctx['annotations'].values()),phase=status.get('phase'),
                total_tasks=len(ctx['samples'])*3,total_samples=len(ctx['samples']),ready=status['complete'],displayed_run=RUN_ID)


@app.get('/api/full-progress')
def full_progress():
    path=BASE.parent/'runs/mercaptionplus/status.json'
    if not path.exists():return {'available':False}
    result=json.loads(path.read_text());result['available']=True;return result


@lru_cache(maxsize=1)
def tearing_context():
    root=BASE.parent/'runs/mercaptionplus'
    with (root/'tearing_review_candidates.csv').open(encoding='utf-8',newline='') as f:
        candidates=list(csv.DictReader(f))
    index={s['sample_id']:s for s in json.loads((root/'samples.json').read_text())}
    items=[]
    for row in candidates:
        sid=row['sample_id'];assert row['teacher_state']=='positive' and row['final_state'] in ('uncertain','positive')
        items.append(dict(id=sid,duration=float(row['duration_sec']),evidence=row['evidence_note'],text=index[sid]['text'],
            final_state=row['final_state']))
    return root,items,{row['id']:row for row in items}

def tearing_item(sid):
    root,_,index=tearing_context()
    if sid not in index:raise HTTPException(404,'不在流泪候选清单中')
    record=json.loads((root/'annotations'/f'{sid}.visual.json').read_text())
    if record['annotation']['labels']['VIS_TEARING_PRESENT']['state']!='positive':
        raise HTTPException(409,'该样本当前未标注为流泪')
    return record,index[sid]

@app.get('/tearing')
def tearing_page():return FileResponse(BASE/'tearing.html',media_type='text/html')

@app.get('/api/tearing')
def tearing_list():
    _,items,_=tearing_context()
    return dict(samples=items,count=len(items),model='Qwen3.8-Omni-Flash',cue='VIS_TEARING_PRESENT')

@app.get('/api/tearing/{sid}')
def tearing_detail(sid:str):
    record,item=tearing_item(sid);meta=record['meta']
    label=record['annotation']['labels']['VIS_TEARING_PRESENT']
    return dict(**item,teacher_label=label,
        final_label=label,mask=int(label['state'] in ('positive','negative')),y=1 if label['state']=='positive' else 0 if label['state']=='negative' else None,
        video_url=f'/tearing-media/{sid}',resolution=[meta['submitted_video']['width'],meta['submitted_video']['height']],
        fps=meta['submitted_video']['fps'],frames=meta['source_frame_count'],
        model=record['api']['model_returned'])

_preview_lock=threading.Lock()

@app.api_route('/tearing-media/{sid}',methods=['GET','HEAD'])
def tearing_media(sid:str,request:Request):
    record,_=tearing_item(sid);source=Path(record['meta']['source_path'])
    if not source.is_file():raise HTTPException(404,'原始视频不存在')
    # Read original dataset video; generate only the requested complete silent preview.
    target=BASE/'cache/videos'/f'{sid}.review.mp4'
    with _preview_lock:
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_name(target.stem+'.tmp.mp4')
            subprocess.run(['/ai/sjq/miniconda3/envs/talkinghead/bin/ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
                '-i',str(source),'-map','0:v:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',
                '-vsync','0','-threads','2','-movflags','+faststart',str(temp)],check=True,timeout=120)
            import av
            with av.open(str(temp)) as video:
                stream=video.streams.video[0];expected=record['meta']['source_video']
                assert not video.streams.audio
                assert (stream.width,stream.height)==(expected['width'],expected['height'])
                assert abs(float(stream.average_rate)-expected['fps'])<.001
                assert abs(float(stream.duration*stream.time_base)-expected['duration'])<.001
                assert sum(bool(p.size) for p in video.demux(stream))==expected['video_packets']
            temp.replace(target)
    return stream_media(target,request)
