import json,re,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
BASE=Path(__file__).resolve().parent
REPORT=BASE/'reports/full_v2_4'
URL=os.getenv('APPRAISAL_VIEWER_URL','http://127.0.0.1:8765')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=str(next((BASE/'browser-cache').glob('chromium-*/chrome-linux64/chrome'))),
  headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1440,'height':1100})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL+'/appraisal',wait_until='networkidle')
 page.locator('#workspace').wait_for(state='visible')
 expect(page.locator('#completed')).to_contain_text('31255')
 expect(page.locator('#samples button')).to_have_count(100)
 assert page.locator('#focus').count()==0
 expect(page.locator('#promptVersion')).to_have_text('appraisal_teacher_v2.4')
 expect(page.locator('#pageInfo')).to_have_text('1–100')
 page.locator('#listNext').click()
 expect(page.locator('#pageInfo')).to_have_text('101–200')
 page.locator('#listPrev').click()
 expect(page.locator('#pageInfo')).to_have_text('1–100')
 page.locator('#search').fill('samplenew3_00000058')
 expect(page.locator('#samples button')).to_have_count(1,timeout=20000)
 expect(page.locator('#sampleId')).to_have_text('samplenew3_00000058')
 expect(page.locator('.dimension')).to_have_count(6)
 page.locator('#search').fill('')
 expect(page.locator('#samples button')).to_have_count(100,timeout=20000)
 page.locator('#statusFilter').select_option('ok')
 expect(page.locator('#samples button').first).to_be_visible()
 page.locator('.provenance summary').click()
 assert 'joint_text_audio_video_single_request' in page.locator('#raw').inner_text()
 assert '"focus_person":' not in page.locator('#raw').inner_text()
 page.locator('.provenance summary').click()
 with page.expect_download(timeout=30000) as download:page.locator('#csv').click()
 download.value.save_as(str(REPORT/'browser_current_successes.csv'))
 assert (REPORT/'browser_current_successes.csv').stat().st_size>0
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.screenshot(path=str(REPORT/'desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 page.goto(URL+'/appraisal',wait_until='networkidle')
 page.locator('#workspace').wait_for(state='visible')
 expect(page.locator('#completed')).to_contain_text('31255')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.screenshot(path=str(REPORT/'mobile.png'),full_page=True)
 assert not errors,errors
 result=dict(passed=True,total_samples=31255,page_size=100,next_previous_pages=True,server_search=True,
  success_filter=True,csv_download=True,focus_person_removed=True,desktop_and_mobile=True,javascript_errors=errors)
 (REPORT/'browser_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False))
 browser.close()
