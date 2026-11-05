
"""One official evaluator per GPU, disjoint jobs, after the global inference barrier."""
import argparse,math,os,sys,time,traceback,subprocess,signal,zipfile
from .common import *

def wait_inference(run,node):
 deadline=time.monotonic()+4*3600
 while True:
  assert not (run/'STOP.json').exists(),'Run stopped'
  if (run/'inference_barrier.json').exists() and read(run/'inference_barrier.json').get('passed'):
   if read(run/'workers'/(node+'_controller.json'))['state']=='complete':return
  assert time.monotonic()<deadline,'Inference barrier wait timeout'
  time.sleep(10)

def worker(run,node):
 owner=lock(run/(node+'_official_evaluator.lock'));assert owner is not None,'Evaluator already running on '+node
 state=dict(node=node,pid=os.getpid(),evaluators_per_gpu=1,plan_id=plan(run)['plan_id'])
 def update(**kw):state.update(kw,at=now());write(run/('evaluation_'+node+'_status.json'),state)
 try:
  update(state='waiting_for_all_inference')
  wait_inference(run,node)
  from .execute import verify,used_memory
  p=verify(run);deadline=time.monotonic()+180
  while used_memory()>512:
   assert time.monotonic()<deadline,'GPU not released after inference'
   time.sleep(3)
  assert all(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json'))
  os.chdir(PROJECT/'AffectGPT');sys.path.insert(0,str(PROJECT/'AffectGPT'))
  import evaluation
  from amg_inference.full_score import truth
  files=[f for i,f in enumerate(sorted((run/'jobs').glob('*.json'))) if i%2==p['nodes'].index(node)]
  refs={d:truth(d,p,evaluation) for d in p['datasets']};judge=None
  update(state='loading_judge',assigned_groups=len(files),completed_groups=0)
  for f in files:
   j=read(f);dest=run/'scores'/f.name
   if dest.exists():
    assert read(dest)['plan_id']==p['plan_id']
    continue
   raw=Path(j['official_npz']);assert raw.is_file()
   update(state='scoring',job=j['id'],completed_groups=sum((run/'scores'/x.name).exists() for x in files))
   for suffix in ['-openset.npz','-openset-sentiment.npz']:
    cached=raw.with_name(raw.stem+suffix)
    if cached.exists():
     try:
      with zipfile.ZipFile(cached) as z:good=z.testzip() is None
     except (OSError,zipfile.BadZipFile):good=False
     if not good:cached.unlink()
   if judge is None:judge=evaluation.func_read_batch_calling_model('Qwen25')
   d=j['dataset'];assert len(refs[d])==j['samples']
   if d=='MER2023':
    v,_=evaluation.calculate_discrete_zeroshot(str(raw),refs[d],*judge,True);metric='HIT';metrics=dict(HIT=float(v))
   elif d=='SIMS':
    v,acc=evaluation.calculate_dimension_zeroshot(str(raw),refs[d],*judge,True);metric='WAF';metrics=dict(WAF=float(v),ACC=float(acc))
   else:
    v,precision,recall=evaluation.calculate_ov_zeroshot(str(raw),refs[d],*judge,True);metric='F_s';metrics=dict(F_s=float(v),P_s=float(precision),R_s=float(recall))
   assert all(math.isfinite(x) for x in metrics.values())
   write(dest,dict(job_id=j['id'],epoch=j['epoch'],dataset=d,samples=j['samples'],main_metric=metric,main_score=float(v),metrics=metrics,checkpoint=p['checkpoints'][str(j['epoch'])],raw_sha256=sha(raw),plan_id=p['plan_id'],official_evaluation_source=str(PROJECT/'AffectGPT/evaluation.py'),evaluation_node=node,evaluators_per_gpu=1,completed_at=now()))
   j['score_state']='complete';write(f,j)
  assert all((run/'scores'/x.name).exists() for x in files)
  update(state='complete',completed_groups=len(files))
 except BaseException as exc:
  update(state='failed',error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()

def coordinate(run):
 owner=lock(run/'dual_evaluation_coordinator.lock');assert owner is not None,'Score coordinator already running'
 from .execute import verify,summarize
 p=verify(run);child=None
 try:
  assert read(run/'inference_barrier.json')['passed']
  args=[PYTHON,'-u','-B','-m','amg_oof_eval_20261105.dual_score','worker','--run',str(run),'--node','A800']
  with (run/'logs/score_A800.log').open('ab',buffering=0) as stream:
   child=subprocess.Popen(args,cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=time.monotonic()+3600
  while True:
   states={n:read(run/('evaluation_'+n+'_status.json')) if (run/('evaluation_'+n+'_status.json')).exists() else dict(state='pending_start') for n in p['nodes']}
   assert not any(s['state']=='failed' for s in states.values()),'Evaluator failed: '+repr(states)
   if child.poll() is not None:assert child.returncode==0,'A800 evaluator failed'
   completed=summarize(run,p)
   write(run/'evaluation_status.json',dict(state='scoring',completed=completed,evaluators_per_gpu=1,node_states={n:s['state'] for n,s in states.items()},pid=os.getpid(),at=now()))
   if all(s['state']=='complete' for s in states.values()):break
   assert time.monotonic()<deadline,'Evaluation timeout'
   time.sleep(10)
  assert summarize(run,p)==21
  write(run/'evaluation_status.json',dict(state='complete',completed=21,evaluators_per_gpu=1,nodes=p['nodes'],at=now()))
 except BaseException:
  if child is not None and child.poll() is None:
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
  raise
 finally:owner.close()

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['worker','coordinate']);a.add_argument('--run',required=True);a.add_argument('--node',choices=['A800','A100'])
 x=a.parse_args()
 {'worker':lambda:worker(Path(x.run),x.node),'coordinate':lambda:coordinate(Path(x.run))}[x.mode]()
