"""Sparse-positive workflow checks; writes only to isolated port 8767."""
import csv,json,os,time
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright,expect
from human_annotation.positive_scoring import compare_records
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'human_annotation';URL='http://127.0.0.1:8767'
c=httpx.Client(base_url=URL,timeout=30)
boot=c.get('/api/bootstrap').json();assert boot['annotation_policy']=='positive_confirmation_v1'
sid=boot['samples'][0]['id'];sid2=boot['samples'][1]['id'];key=boot['cue_ids']['text'][0]
meta=dict(annotation_policy=boot['annotation_policy'],workspace_epoch=boot['workspace_epoch'])
assert c.put('/api/samples/'+sid,json=dict(revision=0,status='draft')).status_code==409
assert c.put('/api/samples/'+sid,json=dict(meta,revision=0,status='draft',annotator='1',cues={key:{'state':'negative'}})).status_code==422
body=dict(meta,revision=0,status='draft',annotator='1',cues={key:{'state':'positive'}})
r=c.put('/api/samples/'+sid,json=body);assert r.status_code==200,r.text
assert c.put('/api/samples/'+sid,json=body).status_code==409
assert c.put('/api/samples/'+sid,json=dict(body,revision=r.json()['revision'],workspace_epoch='old-reset')).status_code==409
env={**os.environ,'LD_LIBRARY_PATH':str(ROOT/'appraisal_annotation/tools/system-libs/usr/lib/x86_64-linux-gnu'),'FONTCONFIG_FILE':str(ROOT/'appraisal_annotation/tools/fonts.conf')}
errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=str(ROOT/'appraisal_annotation/browser-cache/chromium-1248/chrome-linux64/chrome'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'],env=env)
 page=b.new_page(viewport={'width':1440,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL+'/#'+sid,wait_until='networkidle');expect(page.locator('#workspace')).to_be_visible()
 expect(page.locator('#annotator')).to_have_value('1')
 assert page.locator('.human-cell select').count()==0
 expect(page.locator('.positive-pick input')).to_have_count(15)
 expect(page.locator('.positive-pick input').first).to_be_checked()
 page.locator('.positive-pick input').nth(1).check();page.locator('.positive-pick input').first.uncheck()
 expect(page.locator('#saveStatus')).to_contain_text('草稿已保存',timeout=15000)
 page.reload(wait_until='networkidle');expect(page.locator('.positive-pick input').nth(1)).to_be_checked();expect(page.locator('.positive-pick input').first).not_to_be_checked()
 page.locator('#tab-appraisal').click();expect(page.locator('.human-cell select')).to_have_count(6)
 first_dim=next(iter(boot['dimensions']));state=boot['dimensions'][first_dim][0]
 page.locator('.human-cell select').first.select_option(state)
 expect(page.locator('#saveStatus')).to_contain_text('草稿已保存',timeout=15000)
 assert page.locator('.reason').count()==0
 page.locator('#submit').click();expect(page.locator('#sampleId')).not_to_have_text(sid,timeout=15000)
 saved=c.get('/api/samples/'+sid).json()['human'];assert saved['status']=='submitted'
 human=saved['payload'];assert sum(x['state']=='positive' for x in human['cues'].values())==1
 assert sum(x['state'] is None for x in human['cues'].values())==41
 assert sum(x['valid'] is None for x in human['appraisal'].values())==5
 assert not human['appraisal'][first_dim]['evidence']
 assert all(x['state'] in (None,'positive') for x in human['cues'].values())
 for width in (1024,390):
  page.set_viewport_size({'width':width,'height':900});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 assert not errors,errors
 b.close()
r=c.put('/api/samples/'+sid2,json=dict(meta,revision=0,status='submitted',annotator='1',cues={},appraisal={}))
assert r.status_code==200,r.text
r=c.post('/api/export');assert r.status_code==200,r.text
export=r.json()
with open(export['csv'],encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
assert len(rows)==2 and all(r['human_state'] for r in rows)
metrics=json.loads(Path(export['positive_comparison']).read_text())
assert metrics['submitted_samples']==2 and metrics['overall']['human_positive']==2
# Deterministic metric fixture: one overlap, one extra model positive, one missed human positive.
rows=[dict(sid='test',status='submitted',payload=dict(cues={'TXT_A':{'state':'positive'},'TXT_B':{'state':'positive'}},appraisal={})),dict(sid='draft',status='draft',payload={})]
t=lambda _:dict(cues={'TXT_A':{'state':'positive'},'TXT_C':{'state':'positive'},'TXT_D':{'state':'uncertain'}},appraisal={'dimensions':[]})
known=compare_records(rows,t);assert known['overall']['tp']==known['overall']['fp']==known['overall']['fn']==1
assert known['overall']['precision']==known['overall']['recall']==known['overall']['f1']==.5
result=dict(sparse_cue_submit=True,optional_appraisal_dimensions=True,optional_evidence=True,empty_positive_sample_submit=True,autosave_and_reload=True,only_positive_controls=True,no_negative_for_blanks=True,old_page_and_reset_epoch_rejected=True,revision_conflict=True,positive_only_csv=True,submitted_only_positive_metrics=True,metric_fixture_verified=True,desktop_mobile=True,javascript_errors=errors)
(BASE/'reports/positive_review_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
