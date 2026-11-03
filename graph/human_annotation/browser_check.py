"""Run entirely on the server; all writes target a separate QA service/database."""
from graph_paths import resolve_path as _graph_resolve_path
import csv,json,os,time
from graph_paths import Path
import httpx
from playwright.sync_api import sync_playwright,expect
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
URL='http://127.0.0.1:8767'
client=httpx.Client(base_url=URL,timeout=30)
boot=client.get('/api/bootstrap').json()
assert len(boot['samples'])==500
assert sum(s['role']=='gold_audit' for s in boot['samples'])==300
assert len(boot['cue_names'])==42 and len(boot['dimensions'])==6
sid=boot['samples'][0]['id'];detail=client.get('/api/samples/'+sid).json()
assert detail['human']['revision']==0,'Use a fresh isolated QA database'
assert client.get('/api/samples/outside_manifest').status_code==404
assert client.get('/media/outside_manifest/audio').status_code==404
assert client.put('/api/samples/'+sid,json={'revision':0},headers={'Origin':'https://example.invalid'}).status_code==403
assert client.put('/api/samples/'+sid,json={'revision':0,'status':'submitted','annotator':'QA'}).status_code==422
assert client.get('/media/'+sid+'/audio',headers={'Range':'bytes=0-127'}).status_code==206
result={'fixed_500':True,'roles_300_200':True,'out_of_scope_rejected':True,'cross_origin_rejected':True,'incomplete_submit_rejected':True,'audio_range':True}
env={**os.environ,'LD_LIBRARY_PATH':str(ROOT/'appraisal_annotation/tools/system-libs/usr/lib/x86_64-linux-gnu')+':'+os.environ.get('LD_LIBRARY_PATH',''),'FONTCONFIG_FILE':str(ROOT/'appraisal_annotation/tools/fonts.conf')}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=str(ROOT/'appraisal_annotation/browser-cache/chromium-1248/chrome-linux64/chrome'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'],env=env)
 page=browser.new_page(viewport={'width':1440,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL,wait_until='networkidle');expect(page.locator('#workspace')).to_be_visible()
 expect(page.locator('.node')).to_have_count(15)
 assert all(v=='' for v in page.locator('.human-cell select').evaluate_all('(els)=>els.map(e=>e.value)'))
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.wait_for_function('document.getElementById("video").readyState>=2')
 page.wait_for_function('document.getElementById("audio").readyState>=2')
 result['media_decode']=True
 page.locator('#annotator').fill('QA_ONLY')
 row=page.locator('.node').first
 row.locator('.human-cell select').select_option('uncertain')
 row.locator('textarea').fill('QA：证据边界模糊，仅用于独立测试库')
 expect(page.locator('#saveStatus')).to_contain_text('草稿已保存',timeout=15000)
 saved=client.get('/api/samples/'+sid).json()['human'];assert saved['status']=='draft'
 conflict=client.put('/api/samples/'+sid,json={**saved['payload'],'revision':0,'status':'draft'})
 assert conflict.status_code==409
 page.reload(wait_until='networkidle')
 expect(page.locator('.node').first.locator('select')).to_have_value('uncertain')
 expect(page.locator('.node').first.locator('textarea')).to_have_value('QA：证据边界模糊，仅用于独立测试库')
 result.update(autosave=True,reload_restores=True,revision_conflict=True)
 page.locator('#tab-audio').click();expect(page.locator('.node')).to_have_count(17)
 page.locator('#tab-visual').click();expect(page.locator('.node')).to_have_count(10)
 page.locator('#tab-appraisal').click();expect(page.locator('.node')).to_have_count(6)
 first=page.locator('.node').first
 first.locator('.human-cell select').first.select_option('invalid')
 first.locator('.reason').select_option('insufficient_evidence')
 expect(page.locator('#saveStatus')).to_contain_text('草稿已保存',timeout=15000)
 page.reload(wait_until='networkidle');page.locator('#tab-appraisal').click()
 expect(page.locator('.node').first.locator('.reason')).to_have_value('insufficient_evidence')
 first=page.locator('.node').first;first.locator('.human-cell select').first.select_option('AGR_RELEVANT')
 first.locator('textarea').fill('QA：直接文本证据')
 first.locator('input[type=checkbox]').first.check()
 expect(page.locator('#saveStatus')).to_contain_text('草稿已保存',timeout=15000)
 result['appraisal_valid_invalid_edit']=True
 for tab,count in [('text',15),('audio',17),('visual',10),('appraisal',6)]:
  page.locator('#tab-'+tab).click()
  for i in range(count):page.locator('.node').nth(i).locator('.copy').click()
 page.locator('#save').click();expect(page.locator('#saveStatus')).to_contain_text('草稿已保存',timeout=15000)
 expect(page.locator('#nodeProgress')).to_have_text('48 / 48 已标注')
 before=client.get('/api/samples/'+sid).json()['teacher']
 page.locator('#submit').click()
 expect(page.locator('#sampleId')).not_to_have_text(sid,timeout=20000)
 submitted=client.get('/api/samples/'+sid).json();assert submitted['human']['status']=='submitted'
 assert submitted['teacher']==before
 result.update(all_48_nodes=True,copy_per_node=True,submit_and_next=True,teacher_unchanged=True)
 page.locator('#role').select_option('diagnostic_reserved');expect(page.locator('#samples button')).to_have_count(200)
 page.locator('#role').select_option('gold_audit');expect(page.locator('#samples button')).to_have_count(300)
 page.locator('#status').select_option('submitted');expect(page.locator('#samples button')).to_have_count(1)
 page.locator('#search').fill(sid);expect(page.locator('#samples button')).to_have_count(1)
 page.locator('#samples button').click();expect(page.locator('#sampleId')).to_have_text(sid)
 result['search_role_status_filters']=True
 page.locator('#tab-text').click();page.evaluate('window.scrollTo(0,0)')
 page.screenshot(path=str(BASE/'reports/desktop.png'))
 for width in (1024,768,390):
  page.set_viewport_size({'width':width,'height':900})
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
 page.screenshot(path=str(BASE/'reports/mobile.png'),full_page=True)
 assert not errors,errors
 result.update(desktop_mobile=True,javascript_errors=errors)
 browser.close()
exported=client.post('/api/export').json()
assert exported['saved_samples']==1 and exported['submitted']==1
assert '/reports/qa_exports/' in exported['csv']
with open(_graph_resolve_path(exported['csv']), encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
assert len(rows)==48 and all(r['status']=='submitted' for r in rows)
result['server_only_export']=True
prod=httpx.get('http://127.0.0.1:8766/api/bootstrap',timeout=30).json()
assert all(s['revision']==0 for s in prod['samples'])
result['production_annotations_untouched']=True
(BASE/'reports/browser_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
