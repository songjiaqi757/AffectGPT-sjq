"""Read-only playback checks, executed on the server without editing annotations."""
import json,os,subprocess
from graph_paths import Path
import httpx
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'human_annotation'
URL='http://127.0.0.1:8766'
client=httpx.Client(base_url=URL,timeout=150)
sid=client.get('/api/bootstrap').json()['samples'][0]['id']
d=client.get('/api/samples/'+sid).json()
r=client.get(d['media']['video'],headers={'Range':'bytes=0-127'})
assert r.status_code==206 and len(r.content)==128
preview=BASE/'cache/video_audio'/f'{sid}.mp4'
probe=json.loads(subprocess.check_output(['/ai/sjq/miniconda3/envs/talkinghead/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(preview)]))
assert {s['codec_type'] for s in probe['streams']}=={'video','audio'}
assert next(s for s in probe['streams'] if s['codec_type']=='audio')['codec_name']=='aac'
assert abs(float(probe['format']['duration'])-d['sample']['audio_duration'])<.15
result=dict(has_video_and_audio_tracks=True,range_playback=True,full_duration=True)
env={**os.environ,'LD_LIBRARY_PATH':str(ROOT/'appraisal_annotation/tools/system-libs/usr/lib/x86_64-linux-gnu'),'FONTCONFIG_FILE':str(ROOT/'appraisal_annotation/tools/fonts.conf')}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=str(ROOT/'appraisal_annotation/browser-cache/chromium-1248/chrome-linux64/chrome'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'],env=env)
 page=b.new_page(viewport={'width':1440,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def wait_js(predicate):
  for _ in range(100):
   if page.evaluate('()=>'+predicate):return
   page.wait_for_timeout(50)
  raise AssertionError('Playback condition timed out: '+predicate)
 page.goto(URL+'/#'+sid,wait_until='networkidle');expect(page.locator('#workspace')).to_be_visible()
 wait_js('document.getElementById("video").readyState>=2')
 assert page.locator('#video').evaluate('(v)=>!v.muted && !v.defaultMuted')
 page.locator('#sync').click()
 wait_js('document.getElementById("video").currentTime>0.15')
 state=page.locator('#video').evaluate('(v)=>({paused:v.paused,muted:v.muted,error:v.error?.message,audioBytes:v.webkitAudioDecodedByteCount})')
 assert not state['paused'] and not state['muted'] and not state.get('error'),state
 assert state.get('audioBytes',1)>0,state
 assert page.locator('#audio').evaluate('(a)=>a.paused')
 page.locator('#sync').click();assert page.locator('#video').evaluate('(v)=>v.paused')
 page.locator('#audio').evaluate('(a)=>a.play()')
 wait_js('!document.getElementById("audio").paused')
 assert page.locator('#video').evaluate('(v)=>v.paused')
 page.locator('#video').evaluate('(v)=>{v.currentTime=0;return v.play()}')
 wait_js('!document.getElementById("video").paused')
 assert page.locator('#audio').evaluate('(a)=>a.paused')
 page.locator('#video').evaluate('(v)=>{v.pause();v.currentTime=0.5;v.playbackRate=1.5}')
 assert page.locator('#video').evaluate('(v)=>v.currentTime===0.5 && v.playbackRate===1.5')
 assert not errors,errors
 result.update(default_unmuted=True,audio_decode=True,video_with_sound_plays=True,separate_audio_excludes_video=True,video_excludes_separate_audio=True,pause_seek_speed=True,javascript_errors=errors)
 b.close()
(BASE/'reports/media_playback_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
