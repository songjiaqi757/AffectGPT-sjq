"""Concurrency and persistence verification against the isolated QA server."""
from concurrent.futures import ThreadPoolExecutor
import httpx,json,sqlite3
from graph_paths import Path
BASE=Path(__file__).resolve().parent
url='http://127.0.0.1:8767'
boot=httpx.get(url+'/api/bootstrap').json();sid=boot['samples'][1]['id']
current=httpx.get(url+'/api/samples/'+sid).json()['human']
payload=current['payload'] or dict(annotator='QA_CONCURRENCY',cues={},appraisal={},notes='',event_context='')
body=dict(payload,revision=current['revision'],status='draft')
def write(i):
 return httpx.put(url+'/api/samples/'+sid,json=body,timeout=30).status_code
with ThreadPoolExecutor(max_workers=12) as pool:codes=list(pool.map(write,range(12)))
assert codes.count(200)==1 and codes.count(409)==11,codes
record=httpx.get(url+'/api/samples/'+sid).json()['human']
assert record['revision']==current['revision']+1
with sqlite3.connect(BASE/'annotations.sqlite3') as db:
 integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
 journal=db.execute('PRAGMA journal_mode').fetchone()[0]
 assert db.execute('SELECT count(*) FROM records').fetchone()[0]==0
assert integrity=='ok' and journal=='delete'
r=dict(parallel_writers=12,successful_writes=1,conflicts_prevented=11,production_integrity=integrity,journal_mode=journal,production_samples_untouched=True)
(BASE/'reports/storage_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r))
