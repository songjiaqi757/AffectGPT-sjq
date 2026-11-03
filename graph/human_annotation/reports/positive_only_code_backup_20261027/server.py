"""Server-only teacher-visible human review for the fixed 300+200 reserve."""
import ast, csv, hashlib, json, os, re, sqlite3, sys, subprocess, threading
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
sys.path.insert(0,str(ROOT))
CUE=ROOT/'cue_annotation/runs/mercaptionplus'
APP=ROOT/'appraisal_annotation/runs/mercaptionplus_v2_4'
DB=Path(os.environ.get('HUMAN_ANNOTATION_DB',str(BASE/'annotations.sqlite3')))
MANIFEST=BASE/'manifest.json'
def read(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
_tree=ast.parse((ROOT/'cue_annotation/viewer/server.py').read_text())
CUE_NAMES=next(ast.literal_eval(n.value) for n in _tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CUE_NAMES' for t in n.targets))
CUE_IDS=read(CUE/'ontology.json')['cue_ids']
DIMENSIONS=read(APP/'ontology.json')['dimensions']
REASONS=read(APP/'ontology.json')['unknown_reason_codes']
DIM_NAMES=dict(APP_GOAL_RELEVANCE='目标相关性',APP_GOAL_CONGRUENCE='目标一致性',APP_EXPECTEDNESS='预期性',APP_AGENCY='因果归属',APP_CERTAINTY='确定性',APP_COPING_POTENTIAL='应对潜力')
STATE_NAMES=dict(positive='存在',negative='未观察到',uncertain='不确定',unobservable='不可观测',AGR_RELEVANT='相关',AGR_IRRELEVANT='不相关',AGC_CONGRUENT='促进目标',AGC_INCONGRUENT='阻碍目标',AGC_MIXED='混合影响',AEX_EXPECTED='符合预期',AEX_UNEXPECTED='违背预期',AAG_SELF='自身',AAG_OTHER='他人',AAG_CIRCUMSTANCE='环境／偶然',AAG_SHARED='共同原因',ACT_CERTAIN='确定',ACT_UNCERTAIN='不确定',ACP_HIGH='应对能力高',ACP_LOW='应对能力低',ACP_MIXED='能力与限制并存')
REASON_NAMES=dict(appraisal_holder_unclear='证据无法关联到同一明确评价',causal_attribution_ambiguous='因果归属不明',certainty_not_expressed='未表达对结果的确定程度',conflicting_evidence='证据存在无法化解的冲突',coping_evidence_absent='缺少应对能力或资源的证据',dimension_not_applicable='该维度不适用',event_goal_relation_unclear='事件与目标关系不清',evidence_indirect_only='只有间接证据',goal_not_identifiable='无法识别相关目标',insufficient_evidence='证据不足',prior_expectation_not_identifiable='缺少先前预期的证据',state_not_explicitly_supported='没有明确支持该状态的证据')
MOD_NAMES=dict(text='文本',audio='音频',visual='视觉',video='视频')
ROLE_NAMES=dict(gold_audit='人工审计',diagnostic_reserved='诊断保留')
ALL_CUES=[c for ids in CUE_IDS.values() for c in ids]
assert len(ALL_CUES)==42 and len(DIMENSIONS)==6 and set(ALL_CUES)<=set(CUE_NAMES)
if not MANIFEST.exists():
 release=read(ROOT/'cue_student/artifacts/current_release.json')
 members=read(Path(release['path'])/'members.json')
 selected=[s for s in members if s['role'] in ROLE_NAMES]
 assert len(selected)==500 and sum(s['role']=='gold_audit' for s in selected)==300
 MANIFEST.write_text(json.dumps(dict(schema_version='human_review_v1',created_at=now(),release_id=release['release_id'],release_path=release['path'],mode='teacher_visible_assisted_review',samples=selected),ensure_ascii=False,indent=2))
MAN=read(MANIFEST)
SAMPLES=MAN['samples']
INDEX={s['sample_id']:s for s in SAMPLES}
assert len(INDEX)==500
MANIFEST_HASH=digest(MANIFEST)
@contextmanager
def connect():
 db=sqlite3.connect(DB,timeout=20);db.row_factory=sqlite3.Row
 db.execute('PRAGMA mmap_size=0');db.execute('PRAGMA synchronous=FULL')
 try:
  with db:yield db
 finally:db.close()
def init_db():
 with connect() as db:
  db.execute('PRAGMA journal_mode=DELETE')
  db.execute('CREATE TABLE IF NOT EXISTS records (sid TEXT PRIMARY KEY,revision INTEGER NOT NULL,status TEXT NOT NULL,annotator TEXT NOT NULL,updated_at TEXT NOT NULL,payload TEXT NOT NULL,source_hash TEXT NOT NULL)')
  db.execute('CREATE TABLE IF NOT EXISTS history (sid TEXT NOT NULL,revision INTEGER NOT NULL,saved_at TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(sid,revision))')
init_db()
def check_sid(sid):
 if sid not in INDEX:raise HTTPException(404,'样本不在固定的 500 条人工标注清单中')
 return INDEX[sid]
def parse_raw(path):
 raw=read(path);content=raw['response']['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(x.get('text','') for x in content)
 content=re.sub(r'^```(?:json)?\s*|\s*```$','',content.strip())
 return json.loads(content),digest(path)
@lru_cache(maxsize=500)
def teacher(sid):
 check_sid(sid);cues={};current={};hashes={};paths={}
 for modality,ids in CUE_IDS.items():
  record=read(CUE/'annotations'/f'{sid}.{modality}.json')
  path=CUE/'teacher_raw'/f"{sid}.{modality}.attempt{record['api']['attempt']}.json"
  parsed,sha=parse_raw(path)
  assert parsed['sample_id']==sid and set(parsed['labels'])==set(ids)
  cues.update(parsed['labels']);current.update(record['annotation']['labels'])
  hashes[modality]=sha;paths[modality]=str(path.relative_to(ROOT))
 rec=read(APP/'annotations'/f'{sid}.json')
 path=APP/'teacher_raw'/f"{sid}.attempt{rec['api']['attempt']}.json"
 appraisal,hashes['appraisal']=parse_raw(path)
 assert {d['dimension_id'] for d in appraisal['dimensions']}==set(DIMENSIONS)
 paths['appraisal']=str(path.relative_to(ROOT))
 source_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
 return dict(cues=cues,appraisal=appraisal,current_cue_differences={k:v for k,v in current.items() if v!=cues[k]},raw_sha256=hashes,raw_paths=paths,source_hash=source_hash)
def stored(sid):
 with connect() as db:row=db.execute('SELECT * FROM records WHERE sid=?',(sid,)).fetchone()
 if not row:return dict(revision=0,status='pending',annotator='',updated_at=None,payload=None)
 result=dict(row);result['payload']=json.loads(result['payload']);return result
def fail(message):raise HTTPException(422,message)
def string(value,name,limit=6000):
 if not isinstance(value,str) or len(value)>limit:fail(name+' 必须为长度不超过 '+str(limit)+' 的字符串')
 return value.strip()
def validate(data):
 if not isinstance(data,dict):fail('标注必须是对象')
 if set(data)-{'revision','status','annotator','notes','event_context','cues','appraisal'}:fail('未知字段')
 if type(data.get('revision')) is not int or data['revision']<0:fail('revision 必须为非负整数')
 status=data.get('status','draft')
 if status not in ('draft','submitted'):fail('未知标注状态')
 final=status=='submitted';annotator=string(data.get('annotator',''),'标注人',100)
 if final and not annotator:fail('提交前请填写标注人')
 payload=dict(annotator=annotator,notes=string(data.get('notes',''),'备注'),event_context=string(data.get('event_context',''),'事件概述'),cues={},appraisal={})
 cues,dims=data.get('cues',{}),data.get('appraisal',{})
 if not isinstance(cues,dict) or not isinstance(dims,dict):fail('Cue / Appraisal 必须为对象')
 if set(cues)-set(ALL_CUES) or set(dims)-set(DIMENSIONS):fail('包含未定义的节点')
 for key in ALL_CUES:
  row=cues.get(key,{})
  if not isinstance(row,dict) or set(row)-{'state','evidence_note'}:fail(key+' 格式错误')
  state=row.get('state') or None
  if state is not None and state not in ('positive','negative','uncertain','unobservable'):fail(key+' 标签非法')
  note=string(row.get('evidence_note',''),key+' 证据')
  if final and (state is None or (state!='negative' and not note)):fail(CUE_NAMES[key]+'：请选择标签；存在／不确定／不可观测需要证据说明')
  payload['cues'][key]=dict(state=state,evidence_note=note)
 for key,states in DIMENSIONS.items():
  row=dims.get(key,{})
  if not isinstance(row,dict) or set(row)-{'state','valid','evidence','evidence_modalities','unknown_reason'}:fail(key+' 格式错误')
  state,valid=row.get('state'),row.get('valid');reason=row.get('unknown_reason') or None
  evidence=string(row.get('evidence',''),key+' 证据');modalities=row.get('evidence_modalities',[])
  if valid is not None and type(valid) is not bool:fail(key+' valid 必须为 true / false / null')
  if state is not None and state not in states:fail(key+' 标签非法')
  if reason is not None and reason not in REASONS:fail(key+' 弃标原因非法')
  if not isinstance(modalities,list) or any(m not in ('text','audio','video') for m in modalities) or len(modalities)!=len(set(modalities)):fail(key+' 证据模态非法')
  if valid is False:
   if state is not None or evidence or modalities:fail(key+' 无效维度必须 state=null、证据为空')
   if final and reason is None:fail(DIM_NAMES[key]+'：请选择无效原因')
  elif valid is True:
   if reason is not None:fail(key+' 有效维度不能包含弃标原因')
   if final and (state is None or not evidence or not modalities):fail(DIM_NAMES[key]+'：有效状态需要标签、直接证据和证据模态')
  elif state is not None or evidence or modalities or reason is not None:fail(key+' 请先选择是否有效')
  if final and valid is None:fail(DIM_NAMES[key]+'：尚未标注')
  payload['appraisal'][key]=dict(state=state,valid=valid,evidence=evidence,evidence_modalities=modalities,unknown_reason=reason)
 return status,payload
app=FastAPI(title='500 样本人工标注',docs_url=None,redoc_url=None,openapi_url=None)
@app.middleware('http')
async def headers(request:Request,call_next):
 if request.method in ('PUT','POST','DELETE','PATCH'):
  origin=request.headers.get('origin')
  if origin and origin!=str(request.base_url).rstrip('/'):return JSONResponse({'detail':'请从同源标注页面保存'},status_code=403)
 response=await call_next(request)
 response.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"})
 return response
@app.get('/')
@app.get('/human')
@app.get('/human/')
def home():return FileResponse(BASE/'static/index.html')
@app.get('/static/{name}')
def asset(name:str):
 if name not in ('app.js','style.css'):raise HTTPException(404)
 return FileResponse(BASE/'static'/name)
@app.get('/api/bootstrap')
def bootstrap():
 with connect() as db:rows={r['sid']:dict(r) for r in db.execute('SELECT sid,revision,status,annotator,updated_at FROM records')}
 samples=[dict(id=s['sample_id'],role=s['role'],text=s['text'],**rows.get(s['sample_id'],dict(revision=0,status='pending',annotator='',updated_at=None))) for s in SAMPLES]
 return dict(samples=samples,release_id=MAN['release_id'],manifest_sha256=MANIFEST_HASH,mode=MAN['mode'],cue_ids=CUE_IDS,cue_names=CUE_NAMES,dimensions=DIMENSIONS,dimension_names=DIM_NAMES,state_names=STATE_NAMES,reason_names=REASON_NAMES,modality_names=MOD_NAMES,role_names=ROLE_NAMES)
@app.get('/api/samples/{sid}')
def detail(sid:str):
 s=check_sid(sid)
 return dict(sample=s,teacher=teacher(sid),human=stored(sid),media=dict(audio=f'/media/{sid}/audio',video=f'/media/{sid}/preview'))
@app.put('/api/samples/{sid}')
def save(sid:str,data:dict):
 check_sid(sid);status,payload=validate(data);timestamp=now();source_hash=teacher(sid)['source_hash']
 with connect() as db:
  db.execute('BEGIN IMMEDIATE')
  previous=db.execute('SELECT revision FROM records WHERE sid=?',(sid,)).fetchone()
  revision=previous['revision'] if previous else 0
  if revision!=data['revision']:raise HTTPException(409,'该样本已在其他页面更新；请复制未保存内容后刷新，避免覆盖')
  revision+=1;serialized=json.dumps(payload,ensure_ascii=False)
  db.execute('INSERT OR REPLACE INTO records VALUES (?,?,?,?,?,?,?)',(sid,revision,status,payload['annotator'],timestamp,serialized,source_hash))
  history=dict(sample_id=sid,revision=revision,status=status,updated_at=timestamp,mode=MAN['mode'],release_id=MAN['release_id'],manifest_sha256=MANIFEST_HASH,source_hash=source_hash,payload=payload)
  db.execute('INSERT INTO history VALUES (?,?,?,?)',(sid,revision,timestamp,json.dumps(history,ensure_ascii=False)))
 return dict(revision=revision,status=status,updated_at=timestamp)
_media_lock=threading.Lock()
@app.api_route('/media/{sid}/{kind}',methods=['GET','HEAD'])
def media(sid:str,kind:str,request:Request):
 sample=check_sid(sid)
 if kind not in ('audio','preview'):raise HTTPException(404)
 from appraisal_annotation.viewer import media as established_media, stream
 if kind=='audio':return established_media(sid,kind,request)
 target=BASE/'cache/video_audio'/f'{sid}.mp4'
 with _media_lock:
  if not target.exists():
   # Reuse the existing complete H.264 silent preview, then mux the dataset WAV.
   # The original files and the Cue viewer's silent preview remain unchanged.
   established_media(sid,'preview',request)
   silent=ROOT/'cue_annotation/viewer/cache/videos'/f'{sid}.mp4'
   target.parent.mkdir(parents=True,exist_ok=True)
   temp=target.with_name(target.stem+'.'+uuid4().hex+'.tmp.mp4')
   try:
    subprocess.run(['/ai/sjq/miniconda3/envs/talkinghead/bin/ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
     '-i',str(silent),'-i',sample['audio_path'],'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k',
     '-threads','2','-movflags','+faststart',str(temp)],check=True,timeout=120)
    temp.replace(target)
   finally:
    temp.unlink(missing_ok=True)
 return stream(target,request)
@app.post('/api/export')
def export():
 folder=Path(os.environ.get('HUMAN_ANNOTATION_EXPORTS',str(BASE/'exports')));folder.mkdir(parents=True,exist_ok=True)
 stem=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid4().hex[:6]
 jp,cp=folder/(stem+'.jsonl'),folder/(stem+'.csv')
 with connect() as db:rows=[dict(row) for row in db.execute('SELECT * FROM records ORDER BY sid')]
 fields=['sample_id','role','mode','status','annotator','revision','updated_at','node_type','modality','node_id','node_zh','teacher_state','teacher_state_zh','human_state','human_state_zh','valid','evidence','evidence_modalities','unknown_reason','source_hash','manifest_sha256']
 with jp.open('w') as jf,cp.open('w',encoding='utf-8-sig',newline='') as cf:
  writer=csv.DictWriter(cf,fieldnames=fields);writer.writeheader()
  for row in rows:
   sid=row['sid'];human=json.loads(row['payload']);raw=teacher(sid)
   item=dict(sample_id=sid,role=INDEX[sid]['role'],mode=MAN['mode'],release_id=MAN['release_id'],manifest_sha256=MANIFEST_HASH,**{k:row[k] for k in ('status','annotator','revision','updated_at','source_hash')},annotation=human,teacher=raw)
   jf.write(json.dumps(item,ensure_ascii=False)+'\n')
   common={k:item[k] for k in ('sample_id','role','mode','status','annotator','revision','updated_at','source_hash','manifest_sha256')}
   for modality,keys in CUE_IDS.items():
    for key in keys:
     h=human['cues'][key];t=raw['cues'][key]
     writer.writerow(dict(common,node_type='cue',modality=modality,node_id=key,node_zh=CUE_NAMES[key],teacher_state=t['state'],teacher_state_zh=STATE_NAMES[t['state']],human_state=h['state'],human_state_zh=STATE_NAMES.get(h['state'],''),evidence=h['evidence_note']))
   original={d['dimension_id']:d for d in raw['appraisal']['dimensions']}
   for key in DIMENSIONS:
    h,t=human['appraisal'][key],original[key]
    writer.writerow(dict(common,node_type='appraisal',modality='joint',node_id=key,node_zh=DIM_NAMES[key],teacher_state=t['state'],teacher_state_zh=STATE_NAMES.get(t['state'],'无效'),human_state=h['state'],human_state_zh=STATE_NAMES.get(h['state'],'无效' if h['valid'] is False else ''),valid=h['valid'],evidence=h['evidence'],evidence_modalities='|'.join(h['evidence_modalities']),unknown_reason=h['unknown_reason']))
 return dict(saved_samples=len(rows),submitted=sum(r['status']=='submitted' for r in rows),jsonl=str(jp),csv=str(cp),jsonl_sha256=digest(jp),csv_sha256=digest(cp))
