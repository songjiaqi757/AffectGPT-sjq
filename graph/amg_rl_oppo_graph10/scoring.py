import argparse,subprocess,time,traceback,math,sys,os
from types import SimpleNamespace
from .common import *
def pending(run,role,only=None):
 jobs=[read(f) for f in (Path(run)/'jobs').glob(role+'*.json')]
 return sorted([j for j in jobs if (only is None or (j['dataset']=='OVMERDPlus')==only) and not (Path(run)/'scores'/(j['id']+'.json')).exists()],key=lambda j:(j['checkpoint'],-j['samples']))
def commit(run,p,j,metrics,main,metric,source,**extra):
 require(all(math.isfinite(float(v)) for v in metrics.values()),'Nonfinite official metric')
 value=dict(role=j['role'],checkpoint=j['checkpoint'],dataset=j['dataset'],samples=j['samples'],main_metric=metric,main_score=float(main),metrics={k:float(v) for k,v in metrics.items()},official_source=source,plan_id=p['plan_id'],completed_at_beijing=now(),**extra)
 dump(Path(run)/'scores'/(j['id']+'.json'),value)
 j.update(score_state='complete',scored_at_beijing=now());dump(Path(run)/'jobs'/(j['id']+'.json'),j)
def progress(run,role,**kw):dump(Path(run)/('evaluation_'+role+'.json'),dict(role=role,pid=os.getpid(),time_beijing=now(),**kw))
def rl_ov(run):
 p=plan(run)
 from .native_rl import setup
 n,cfg,changes=setup()
 import statistic as ev
 reader=n.get_name2cls('OVMERDPlus');gt=reader.get_test_name2gt();judge=None
 for j in pending(run,'rl',True):
  require(j['state']=='complete' and len(gt)==j['samples'],'Incomplete RL OV inference or labels')
  progress(run,'rl',phase='scoring_official_RL_OV',job=j['id'])
  if judge is None:judge=ev.func_read_batch_calling_model('Qwen25')
  f,precision,recall=ev.calculate_ov_zeroshot(j['official_npz'],gt,*judge,True)
  commit(run,p,j,dict(F_s=f,P_s=precision,R_s=recall),f,'F_s',str(RL/'statistic.py'),raw_sha256=sha(j['official_npz']))
def rl_other(run):
 p=plan(run);os.chdir(BASE);sys.path.insert(0,str(BASE))
 import evaluation as ev
 from amg_inference.full_score import truth
 ip=dict(datasets=p['models']['rl']['datasets']);refs={};judge=None
 for j in pending(run,'rl',False):
  require(j['state']=='complete','Incomplete RL inference')
  d=j['dataset'];progress(run,'rl',phase='scoring_official_MER_UniBench',job=j['id'])
  if d not in refs:refs[d]=truth(d,ip,ev)
  require(len(refs[d])==j['samples'],'Ground truth membership differs')
  if judge is None:judge=ev.func_read_batch_calling_model('Qwen25')
  if d in DISCRETE:
   v,m=ev.calculate_discrete_zeroshot(j['official_npz'],refs[d],*judge,True);metrics=dict(HIT=v,MSCORE=m);metric='HIT'
  else:
   v,acc=ev.calculate_dimension_zeroshot(j['official_npz'],refs[d],*judge,True);metrics=dict(WAF=v,ACC=acc);metric='WAF'
  commit(run,p,j,metrics,v,metric,str(BASE/'evaluation.py'),raw_sha256=sha(j['official_npz']))
def oppo(run):
 p=plan(run);os.chdir(OPPO);sys.path.insert(0,str(OPPO))
 from affect_r1.merbench import evaluation as ev
 args=SimpleNamespace(dataset_root=str(OPPO/'datasets'));ev.load_config(args);modules=ev.build_local_modules();judge=None
 for j in pending(run,'oppo'):
  require(j['state']=='complete','Incomplete OPPO inference')
  progress(run,'oppo',phase='scoring_official_OPPO',job=j['id'])
  dataset_name=j['dataset'].upper();dataset=modules['dataset_map'][dataset_name]()
  gt=dataset.get_test_name2gt();flag=ev.dataset_flag(dataset_name)
  if flag=='discrete':
   _,idx2emo=ev.get_emo_maps(dataset)
   gt={name:value if isinstance(value,str) else idx2emo[value] for name,value in gt.items()}
  reason,answer=ev.load_predictions(j['official_jsonl'])
  require(len(reason)==j['samples'] and set(reason)==set(gt),'OPPO prediction/ground truth membership differs')
  gt,reason,answer=ev.align_with_groundtruth(gt,reason,answer);openset=ev.answers_to_openset_map(answer)
  if flag=='ovlabel':
   metrics=ev.evaluate_ovlabel(gt,answer,modules);v=metrics['fscore'];metric='F_s'
  elif flag=='discrete':
   metrics=ev.evaluate_discrete(gt,reason,modules,None,use_answer_openset=True,answer_openset=openset);v=metrics['hitrate'];metric='HIT'
  else:
   if judge is None:judge=modules['load_llm']('Qwen25')
   metrics=ev.evaluate_dimension(gt,reason,modules,judge,use_answer_openset=True,answer_openset=openset,jsonl_path=j['official_jsonl']);v=metrics['fscore'];metric='WAF'
  commit(run,p,j,metrics,v,metric,str(OPPO/'affect_r1/merbench/evaluation.py'),raw_sha256=sha(j['official_jsonl']),answer_selection='full',use_answer_openset=True)
def score(run,role):
 p=plan(run);require(all(j['state']=='complete' for j in [read(f) for f in (Path(run)/'jobs').glob(role+'*.json')]),'Inference barrier closed')
 owner=lock(Path(run)/('score_'+role+'.lock'));require(owner is not None,'Scorer already running')
 try:
  if role=='rl':
   with (Path(run)/'logs'/'rl_official_ov_scoring.log').open('ab',buffering=0) as log:
    z=subprocess.run([PYTHON,'-u','-B','-m','amg_rl_oppo_graph10.scoring','rl_ov','--run',str(run)],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
   require(z.returncode==0,'Official RL OV scorer failed')
   rl_other(run)
  else:oppo(run)
  progress(run,role,phase='complete')
 except BaseException as exc:progress(run,role,phase='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['rl_ov']);a.add_argument('--run',required=True);x=a.parse_args();rl_ov(x.run)
