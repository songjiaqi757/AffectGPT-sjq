import json,re,pathlib,sqlite3,runpy,hashlib,collections
ROOT=pathlib.Path('/ai/sjq/AffectGPT-sjq')
def read(p):return json.loads(pathlib.Path(p).read_text())
def parse(p):
 content=read(p)['response']['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(x.get('text','') for x in content)
 return json.loads(re.sub(r'^\x60\x60\x60(?:json)?\s*|\s*\x60\x60\x60$','',content.strip()))
def teacher(sid):
 cues={}
 for m in ['text','audio','visual']:
  r=ROOT/'cue_annotation/runs/mercaptionplus';a=read(r/'annotations'/f'{sid}.{m}.json')
  cues.update(parse(r/'teacher_raw'/f"{sid}.{m}.attempt{a['api']['attempt']}.json")['labels'])
 r=ROOT/'appraisal_annotation/runs/mercaptionplus_v2_4';a=read(r/'annotations'/f'{sid}.json')
 return dict(cues=cues,appraisal=parse(r/'teacher_raw'/f"{sid}.attempt{a['api']['attempt']}.json"))
db=sqlite3.connect('file:'+str(ROOT/'human_annotation/annotations.sqlite3')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
rows=[dict(r) for r in db.execute("SELECT sid,status,payload,source_hash,updated_at FROM records WHERE status='submitted' ORDER BY sid")];db.close()
fn=runpy.run_path(str(ROOT/'human_annotation/positive_scoring.py'))
teachers={r['sid']:teacher(r['sid']) for r in rows}
result=fn['compare_records'](rows,teachers.__getitem__)
dims=collections.defaultdict(lambda:collections.Counter(tp=0,fp=0,fn=0,human_positive=0,teacher_positive=0))
for row in rows:
 h=fn['sets'](json.loads(row['payload']))['appraisal'];t=fn['sets'](teachers[row['sid']],teacher=True)['appraisal']
 for label in h|t:
  d=dims[label.split('=')[0]];d['tp']+=label in h&t;d['fp']+=label in t-h;d['fn']+=label in h-t;d['human_positive']+=label in h;d['teacher_positive']+=label in t
result['appraisal_dimensions']={k:fn['rates'](v) for k,v in dims.items()}
result.update(mode='teacher_visible_assisted_review',annotation_policy='positive_confirmation_v1',selection_note='50 currently submitted reserve samples; incomplete500,single annotator,not random full-population estimate; absent confirmation counted as set FP,not a negative annotation',record_snapshot=[{k:r[k] for k in ['sid','status','source_hash','updated_at']}|{'payload_sha256':hashlib.sha256(r['payload'].encode()).hexdigest()} for r in rows])
(ROOT/'analysis_reports/reanalysis_20261027_human.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='record_snapshot'},ensure_ascii=False,indent=2))

