"""Server-only Chromium checks; screenshots and downloads stay on server."""
import json,os,sys
from graph_paths import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parent
REPORT=BASE/'reports/v2_4'
REPORT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('APPRAISAL_VIEWER_URL','http://127.0.0.1:8765')
with sync_playwright() as p:
    executable=next((BASE/'browser-cache').glob('chromium-*/chrome-linux64/chrome'))
    browser=p.chromium.launch(executable_path=str(executable),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/appraisal',wait_until='networkidle')
    page.locator('#workspace').wait_for(state='visible')
    assert page.locator('.dimension').count()==6
    assert page.locator('#focus').count()==0
    assert page.locator('#promptVersion').inner_text()=='appraisal_teacher_v2.4'
    first=page.locator('#sampleId').inner_text()
    page.wait_for_function("document.getElementById('video').readyState>=1 && document.getElementById('audio').readyState>=1",timeout=60000)
    media=page.evaluate("""() => ({videoDuration:video.duration,audioDuration:audio.duration,videoWidth:video.videoWidth,videoHeight:video.videoHeight})""")
    assert media['videoDuration']>0 and media['audioDuration']>0 and media['videoWidth']>0
    page.locator('#sync').click()
    page.wait_for_function("!document.getElementById('video').paused && !document.getElementById('audio').paused")
    page.wait_for_timeout(1200)
    assert abs(page.locator('#audio').evaluate('(e)=>e.currentTime')-page.locator('#video').evaluate('(e)=>e.currentTime'))<.6
    page.locator('#sync').click()
    assert page.locator('#audio').evaluate('(e)=>e.paused') and page.locator('#video').evaluate('(e)=>e.paused')
    page.locator('#dimensionFilter').select_option('invalid')
    assert page.locator('.dimension.valid').count()==0 and page.locator('.dimension.invalid').count()>0
    page.locator('#dimensionFilter').select_option('all')
    page.locator('#search').fill(first)
    assert page.locator('#samples button').count()==1
    page.locator('#search').fill('')
    assert page.locator('#samples button').count()==30
    page.locator('#next').click()
    page.wait_for_function("(first)=>document.getElementById('sampleId').textContent!==first",arg=first)
    page.locator('h1').click()
    page.keyboard.press('k')
    page.wait_for_function("(first)=>document.getElementById('sampleId').textContent===first",arg=first)
    page.locator('#dimensionFilter').select_option('valid')
    assert page.locator('.dimension.invalid').count()==0
    page.locator('#dimensionFilter').select_option('all')
    page.locator('.provenance summary').click()
    assert 'joint_text_audio_video_single_request' in page.locator('#raw').inner_text()
    page.locator('.provenance summary').click()
    with page.expect_download() as dl:
        page.locator('#csv').click()
    dl.value.save_as(str(REPORT/'browser_labels.csv'))
    assert (REPORT/'browser_labels.csv').stat().st_size>0
    page.screenshot(path=str(REPORT/'desktop.png'),full_page=True)
    page.locator('.annotation').screenshot(path=str(REPORT/'dimensions.png'))
    desktop_overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
    assert not desktop_overflow
    import requests
    items=requests.get(URL+'/appraisal/api/bootstrap').json()['samples']
    failed=[x for x in items if x['status']=='technical_failure']
    page.locator('#statusFilter').select_option('technical_failure')
    assert page.locator('#samples button').count()==len(failed)
    if failed:
        page.locator('#samples button').first.click()
        page.locator('#sampleId').filter(has_text=failed[0]['id']).wait_for(state='visible')
        assert page.locator('#dimensions .empty').count()==1
        assert '技术失败' in page.locator('#dimensions').inner_text()
        page.locator('.provenance summary').click()
        assert 'technical_failure' in page.locator('#raw').inner_text()
        page.locator('.provenance summary').click()
        page.screenshot(path=str(REPORT/'technical_failure.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.goto(URL+'/appraisal',wait_until='networkidle')
    page.locator('#workspace').wait_for(state='visible')
    assert page.locator('.dimension').count()==6
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    page.screenshot(path=str(REPORT/'mobile.png'),full_page=True)
    assert not errors,errors
    result=dict(passed=True,browser='Chromium',desktop_viewport=[1440,1100],mobile_viewport=[390,844],
        url=URL,prompt_version='appraisal_teacher_v2.4',focus_person_removed=True,technical_failure_ui=True,media_metadata=media,synchronized_playback=True,sample_search=True,keyboard_navigation=True,
        dimension_filters=True,csv_download=True,raw_response_expander=True,horizontal_overflow=False,javascript_errors=errors,
        screenshots=[p.name for p in REPORT.glob('*.png')])
    (REPORT/'browser_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False))
    browser.close()
