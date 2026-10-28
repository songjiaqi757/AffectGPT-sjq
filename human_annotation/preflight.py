import json,time
from collections import Counter
from pathlib import Path
import server
start=time.time();errors=[];differences=0
for i,sid in enumerate(server.INDEX):
 try:
  t=server.teacher(sid)
  assert len(t['cues'])==42 and len(t['appraisal']['dimensions'])==6
  assert all(Path(server.INDEX[sid][m+'_path']).is_file() for m in ('audio','video'))
  differences+=len(t['current_cue_differences'])
 except Exception as e:errors.append(dict(sid=sid,error=str(e)))
 if (i+1)%100==0:print(i+1,flush=True)
r=dict(samples=len(server.INDEX),roles=dict(Counter(s['role'] for s in server.SAMPLES)),nodes_per_sample=48,original_vs_current_differences=differences,errors=errors,seconds=round(time.time()-start,2),manifest_sha256=server.MANIFEST_HASH)
(server.BASE/'reports/preflight.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps(r,ensure_ascii=False));assert not errors
