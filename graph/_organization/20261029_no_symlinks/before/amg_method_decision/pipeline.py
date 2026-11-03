"""Server-only finite method decision: input QC and frozen Cue extraction."""
import os,sys,json,time,copy,traceback,subprocess,argparse,signal,collections
from pathlib import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq');sys.path.insert(0,str(ROOT))
from amg_d_graph_compare.common import read,sha,canonical,atomic_json,locked,environment,now
PYTHON='/ai/sjq/miniconda3/envs/vllm/bin/python'
PACKAGE='amg_method_decision'
def dump(p,x):atomic_json(Path(p),x)
def runpath():return Path(read(ROOT/PACKAGE/'current_run.json')['run'])
def key(row):return canonical(row['sample_id'])[:32]
def records(run):
 return [dict(x,partition=part) for part in ['development','confirmation'] for x in read(run/'data'/f'{part}_records.json')]
def qc(run):
 import numpy as np,cv2
 from concurrent.futures import ThreadPoolExecutor
 cv2.setNumThreads(1)
 rr=records(run)
 def inspect(r):
  a=np.load(r['face_path'],mmap_mode='r',allow_pickle=False)
  if a.ndim!=4 or not a.shape[0] or a.shape[-1]!=3 or not np.isfinite(a[0]).all():raise ValueError('invalid face array '+str(a.shape))
  cap=cv2.VideoCapture(r['video_path']);count=cap.get(cv2.CAP_PROP_FRAME_COUNT);fps=cap.get(cv2.CAP_PROP_FPS)
  hh=[]
  try:
   for t in [.2,.5,.8]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,int(max(0,count-1)*t));ok,img=cap.read()
    if not ok:raise ValueError('video frame decode failed')
    g=cv2.resize(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY),(32,32)).astype(np.float32);d=cv2.dct(g)[:8,:8].reshape(-1);bits=d>np.median(d[1:]);bits[0]=False
    hh.append(int(''.join('1' if b else '0' for b in bits),2))
  finally:cap.release()
  return dict(sample_id=r['sample_id'],name=r['name'],partition=r['partition'],family=r['family'],face_shape=list(a.shape),face_dtype=str(a.dtype),video_frames=count,video_fps=fps,frame_phash=hh)
 good=[];bad=[]
 with ThreadPoolExecutor(max_workers=8) as ex:
  def safe(r):
   try:return inspect(r),None
   except Exception as e:return None,dict(sample_id=r['sample_id'],name=r['name'],partition=r['partition'],reason=repr(e))
  for a,b in ex.map(safe,rr):
   if a:good.append(a)
   if b:bad.append(b)
 pairs=[];remove={x['sample_id'] for x in bad}
 # Conservative selected-media check only; this cannot establish source/video/speaker independence.
 for i,a in enumerate(good):
  for b in good[i+1:]:
   dd=[(x^y).bit_count() for x,y in zip(a['frame_phash'],b['frame_phash'])]
   if max(dd)<=4 and sum(dd)<=9:
    pairs.append(dict(left=a['sample_id'],right=b['sample_id'],phash_hamming=dd,source_identity='unverified',action='quarantine_later_record'))
    remove.add(b['sample_id'])
 for part in ['development','confirmation']:
  orig=run/'data'/f'{part}_records.json';labs=run/'data'/f'{part}_labels.json'
  if not orig.with_suffix('.pre_qc.json').exists():orig.with_suffix('.pre_qc.json').write_bytes(orig.read_bytes());labs.with_suffix('.pre_qc.json').write_bytes(labs.read_bytes())
  chosen=[r for r in read(orig) if r['sample_id'] not in remove];names={r['name'] for r in chosen}
  dump(orig,chosen);dump(labs,{n:v for n,v in read(labs).items() if n in names})
 report=dict(passed=True,input_checked=len(rr),bad=bad,near_selected_pairs=pairs,quarantined=sorted(remove),fingerprints=good,scope='Selected media decode/face validation and three-frame perceptual similarity. Not a known-training-video near-duplicate search; source/speaker grouping unverified.',remaining={p:dict(collections.Counter(r['family'] for r in read(run/'data'/f'{p}_records.json'))) for p in ['development','confirmation']},time_beijing=now())
 dump(run/'audit/selected_media_QC.json',report)
 print('QC',len(rr),'quarantined',len(remove),report['remaining'],flush=True)
def cue_worker(run,slot):
 node='A800' if slot<4 else 'A100';dest=run/'workers'/f'cue_{slot}.json';state=dict(slot=slot,node=node,pid=os.getpid(),state='loading',completed=0)
 def update(**kw):state.update(kw,time_beijing=now());dump(dest,state)
 try:
  update()
  from amg_runtime.student import StudentRunner
  from amg_runtime.engine import GraphQueryEngine
  engine=GraphQueryEngine.from_release(config_path=ROOT/'amg_finetune/runs/graph_continue_20261022_123029/query_engine_config.json')
  with locked(run/f'cue_loading_{node}.lock',blocking=True):
   student=StudentRunner(device='cuda:0',profile='engineering')
   for m in ['text','audio','visual']:student._load(m)
  rr=records(run)
  # Shared queue across both hosts. Reclaimed unfinished tasks retain the same frozen input.
  for r in rr:
   f=run/'cue_cache'/(key(r)+'.json')
   if f.exists():continue
   lock=locked(run/'cue_cache'/(key(r)+'.lock'))
   if lock is None:continue
   try:
    if f.exists():continue
    update(state='cue_inference',sample_id=r['sample_id'])
    safe={k:r[k] for k in ['sample_id','text','audio_path','video_path']}
    cue=student.predict_records([safe])[0];ev=engine.query(cue)
    if not all(cue['modality_present'].values()):raise RuntimeError('Unavailable modality: '+str(cue['diagnostics']))
    dump(f,dict(sample_id=r['sample_id'],cue=cue,evidence=ev,input_id=canonical(safe),hardware_node=node,slot=slot,created_at_beijing=now()))
    update(completed=state['completed']+1)
   finally:lock.close()
  update(state='complete')
 except BaseException as e:update(state='failed',error=repr(e),traceback=traceback.format_exc());raise
def cue_node(run,index):
 node=['A800','A100'][index];pp=[];status=run/f'cue_node_{node}.json'
 deadline=time.monotonic()+1800
 while not (run/'audit/selected_media_QC.json').exists():
  if time.monotonic()>deadline:raise RuntimeError('Input QC timed out')
  time.sleep(3)
 qc=read(run/'audit/selected_media_QC.json')
 if not qc['passed'] or len(records(run))<500:raise RuntimeError('Input QC failed or unexpectedly few inputs')
 try:
  for slot in range(index*4,index*4+4):
   f=(run/f'cue_{slot}.log').open('ab',buffering=0)
   z=subprocess.Popen([PYTHON,'-u','-B','-m',PACKAGE+'.pipeline','cue-worker','--run',str(run),'--slot',str(slot)],cwd=ROOT,env=environment(0),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close();pp.append(z)
  while any(z.poll() is None for z in pp):
   if any(z.poll() not in [None,0] for z in pp):raise RuntimeError('Cue worker failed')
   dump(status,dict(state='running',pids=[z.pid for z in pp],exitcodes=[z.poll() for z in pp],time_beijing=now()));time.sleep(5)
  if any(z.returncode for z in pp):raise RuntimeError('Cue worker failed')
  dump(status,dict(state='complete',time_beijing=now()))
 except BaseException as e:
  dump(status,dict(state='failed',error=repr(e),time_beijing=now()))
  for z in pp:
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
def main():
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--run',default=None);p.add_argument('--slot',type=int);p.add_argument('--index',type=int);a=p.parse_args();run=Path(a.run) if a.run else runpath()
 if a.mode=='qc':qc(run)
 elif a.mode=='cue-worker':cue_worker(run,a.slot)
 elif a.mode=='cue-node':cue_node(run,a.index)
 else:raise ValueError(a.mode)
if __name__=='__main__':main()
