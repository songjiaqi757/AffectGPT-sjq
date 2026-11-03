"""Server-only original seven checkpoint inference, D compact/gate, full graph10."""
import argparse,copy,csv,datetime,fcntl,json,os,signal,subprocess,sys,time,traceback
from collections import Counter
from zoneinfo import ZoneInfo
from graph_paths import Path,hash_matches
from amg_runtime.common import read,sha,canonical,atomic_json as dump,require
from amg_bcd.policy import POLICY,make_prompt,format_evidence,gate
ROOT=Path('/ai/sjq/AffectGPT-sjq/graph')
PKG=ROOT/'amg_base7_graph10'
PYTHON='/ai/sjq/miniconda3/envs/vllm/bin/python'
OLD=ROOT/'amg_inference/runs/graph_225_20261022_174537'
ASSETS=ROOT/'amg_d_graph_compare/assets/graph10_20261025_110938'
def now():return datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def key(sid):return canonical(sid)
def lock(path,blocking=False):
 f=Path(path).open('a+')
 try:fcntl.flock(f,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));return f
 except BlockingIOError:f.close();return None
def env():
 return dict(os.environ,CUDA_VISIBLE_DEVICES='0',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1',PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True')
def plan(run):
 p=read(run/'plan.json');require(p['plan_id']==canonical({k:v for k,v in p.items() if k!='plan_id'}),'Plan changed')
 for f,h in p['protected_files'].items():require(sha(f)==h,'Protected input changed: '+f)
 return p
def engine_for(ap):
 from amg_runtime.engine import GraphQueryEngine
 inputs=read(Path(ap['runtime_path'])/'inputs_p0.json');policy=read(Path(ap['runtime_path'])/'cue_policy.json');g=Path(ap['new_graph_path']);cfg=read(ap['query_config_path'])
 inputs['graph'].update(release_id=ap['graph_release_id'],graph_file=str(g/'graph/graph.json'),path_file=str(g/'graph/paths_cue_appraisal_emotion.csv'))
 with (g/'graph/paths_cue_appraisal_emotion.csv').open() as f:paths=list(csv.DictReader(f))
 return GraphQueryEngine(read(g/'graph/graph.json'),paths,inputs,policy,cfg,ap['runtime_release_id'])
def query(old,engine):
 from amg_finetune_nogc.common import bound_query
 require(old['cache_id']==canonical({k:v for k,v in old.items() if k!='cache_id'}),'Old cache corrupt')
 cue=copy.deepcopy(old['cue']);cue['graph_release_id']=engine.inputs['graph']['release_id'];cue['query_input_id']=canonical({k:v for k,v in cue.items() if k!='query_input_id'})
 return bound_query(engine.query(cue),engine)
def prepare(run):
 status=run/'prepare_status.json'
 def update(**kw):dump(status,dict(time_beijing=now(),**kw))
 try:
  update(state='preparing')
  from transformers import AutoTokenizer
  op=read(OLD/'plan.json');ap=read(ASSETS/'plan.json');engine=engine_for(ap)
  audit=read(Path(ap['new_graph_path'])/'manifest/complete_audit.json');require(audit['passed'] and audit['release_id']==ap['graph_release_id'],'Graph audit failed')
  nodes=Counter(n['node_type'] for n in engine.graph['nodes']);require(nodes['EmotionConcept']==10 and nodes['CueType']==42,'Wrong ontology')
  tokenizer=AutoTokenizer.from_pretrained(str(ROOT/'AffectGPT/models/Qwen2.5-7B-Instruct'),local_files_only=True)
  p=dict(schema='original_base7_graph10_D_inference_v1',created_at_beijing=now(),training_run=str(run),variant='D',policy=POLICY,policy_module='amg_bcd.policy',generation=op['generation'],limits=dict(prompt_token_budget=1536,graph_token_budget=512,subtitle_token_budget=256),prompt_question=op['prompt_question'],datasets=copy.deepcopy(op['datasets']),checkpoints={},seed=42,concurrency_per_node=3,logical_jobs=63,dataset_samples_total=12799,sample_predictions_total=89593,graph_release_id=ap['graph_release_id'],query_config_id=engine.config_id,query_config_path=str(Path(ap['query_config_path'])),new_graph_path=str(Path(ap['new_graph_path'])),node_counts=dict(nodes),nodes={'A800':dict(port=34989,gpu_uuid='GPU-be2112e9-43e2-43e7-da85-ff9198a7c875'),'A100':dict(port=31764,gpu_uuid='GPU-c011e801-690b-0cb9-63d8-184e68e2d39c')},semantics='Inference-only on seven original checkpoints. Original D compact512 plus confidence gate; graph-only grouped OOF is a training protocol and does not alter these checkpoints. Official targets query frozen full-source graph10; no target graph fitting, no training dropout, no polarity loss or head added. No retraining.',protected_files={})
  (run/'original_config.json').write_bytes((ROOT/'amg_finetune/runs/graph_continue_20261022_123029/original_config.json').read_bytes())
  base=ROOT/'AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230'
  for f in sorted(base.glob('checkpoint_*.pth')):
   epoch=int(f.name.split('_')[1]);p['checkpoints'][str(epoch)]=dict(path=str(f),sha256=sha(f),epoch=epoch)
  require(set(p['checkpoints'])=={'30','35','40','45','50','55','60'},'Wrong seven checkpoints')
  for d,spec in p['datasets'].items():
   require(hash_matches(spec['path'],spec['sha256'],sha(spec['path'])),'Membership changed')
   rows=read(spec['path']);require(len(rows)==spec['samples'],'Split count changed')
   for r in rows:
    for field in ['audio_path','face_path','video_path']:r[field]=str(Path(r[field]))
   dest=run/'inputs'/(d+'.json');dump(dest,rows);spec.update(path=str(dest),sha256=sha(dest))
  for f in [PKG/'run.py',ROOT/'amg_bcd/policy.py',ROOT/'amg_inference/model.py',ROOT/'amg_runtime/engine.py',Path(ap['new_graph_path'])/'graph/graph.json',Path(ap['new_graph_path'])/'graph/paths_cue_appraisal_emotion.csv',Path(ap['query_config_path']),run/'original_config.json']+[Path(s['path']) for s in p['datasets'].values()]:p['protected_files'][str(f)]=sha(f)
  p['plan_id']=canonical(p);dump(run/'plan.json',p)
  inventory={};levels=Counter();maxgraph=0;done=0;examples={}
  for d,spec in p['datasets'].items():
   for row in read(spec['path']):
    old=read(OLD/'cache'/(key(row['sample_id'])+'.json'))
    # Compare the historical input hash before physical-path migration.
    expected=dict(sample_id=row['sample_id'],text=row['text'],audio_path=row['audio_path'],video_path=row['video_path'])
    oldinput=old.get('input_id')
    # Existing media paths are outside graph relocation; resolve consistently.
    if oldinput!=canonical(expected):
     original=next(r for r in read(op['datasets'][d]['path']) if r['sample_id']==row['sample_id'])
     require(oldinput==canonical({k:original[k] for k in ['sample_id','text','audio_path','video_path']}),'Cue input mismatch')
    ev=query(old,engine);text,info=format_evidence(ev,tokenizer,512,variant='D');require(info['graph_tokens']<=512,'Graph budget')
    levels[info['evidence_level']]+=1;maxgraph=max(maxgraph,info['graph_tokens'])
    if info['evidence_level'] not in examples:examples[info['evidence_level']]=dict(sample_id=row['sample_id'],graph_text=text,info=info)
    item=dict(sample_id=row['sample_id'],input_id=canonical(expected),source_cache_id=old['cache_id'],evidence=ev,format_info=info,graph_text_sha256=canonical(text),plan_id=p['plan_id'])
    item['cache_id']=canonical(item);dest=run/'cache'/(key(row['sample_id'])+'.json');dump(dest,item);inventory[row['sample_id']]=dict(cache_id=item['cache_id'],sha256=sha(dest));done+=1
    if done%100==0:update(state='querying_graph',completed=done,total=12799,dataset=d,evidence_levels=dict(levels))
  require(done==12799,'Cache coverage mismatch');dump(run/'cache_inventory.json',inventory);dump(run/'prompt_examples.json',examples)
  probe=read(OLD/'source_probe.json');sourceold=read(ROOT/'amg_finetune/runs/graph_continue_20261022_123029/cache'/(probe['record']['sample_id']+'.json'));sourceev=query(sourceold,engine)
  sr=probe['record']
  for field in ['audio_path','face_path','video_path']:
   if field in sr:sr[field]=str(Path(sr[field]))
  dump(run/'source_probe.json',dict(record=sr,evidence=sourceev))
  for epoch in p['checkpoints']:
   for d,spec in p['datasets'].items():
    jid=f'epoch_{int(epoch):03d}_{d}';shards=[]
    for lo in range(0,spec['samples'],32):
     sid=jid+f'_{lo:05d}';shards.append(sid)
     dump(run/'shards'/(sid+'.json'),dict(shard_id=sid,job_id=jid,epoch=int(epoch),dataset=d,start=lo,stop=min(lo+32,spec['samples']),samples=min(32,spec['samples']-lo),state='pending',attempts=0))
    dump(run/'jobs'/(jid+'.json'),dict(job_id=jid,epoch=int(epoch),dataset=d,samples=spec['samples'],shards=shards,state='pending'))
  dump(run/'cache_manifest.json',dict(complete=True,samples=done,plan_id=p['plan_id'],inventory_sha256=sha(run/'cache_inventory.json'),evidence_levels=dict(levels),max_graph_tokens=maxgraph,query_config_id=engine.config_id,graph_release_id=ap['graph_release_id'],no_target_labels_read=True))
  (run/'README.md').write_text('Original checkpoints 30/35/40/45/50/55/60; 9 official test sets; 63 jobs and 89593 predictions. Two separate GPUs, 3 workers each. D=compact512+confidence gate+Graph-OOF inference contract: targets query full frozen source graph10; OOF belongs to training only. Original weights remain unchanged. No training/dropout/polarity head. Cached original student Cue outputs verified and queried anew. One deterministic sample seed across epochs. Output per-sample JSON, per-job JSONL and name2reason.npz. All files stay on servers. Resume by running node with same run and node name; valid completed predictions are reused.\n')
  update(state='complete',completed=done,total=12799,evidence_levels=dict(levels),plan_id=p['plan_id'])
 except BaseException as e:update(state='failed',error=repr(e),traceback=traceback.format_exc());raise
def finalize(run,p,jid):
 h=lock(run/'jobs'/(jid+'.lock'))
 if h is None:return
 try:
  jf=run/'jobs'/(jid+'.json');j=read(jf)
  if j['state']=='complete':return
  if not all(read(run/'shards'/(s+'.json'))['state']=='complete' for s in j['shards']):return
  folder=run/'predictions'/jid;names={};tmp=folder/'predictions.jsonl.tmp'
  with tmp.open('w') as f:
   for row in read(p['datasets'][j['dataset']]['path']):
    x=read(folder/(key(row['sample_id'])+'.json'));require(x['plan_id']==p['plan_id'] and x['checkpoint']['sha256']==p['checkpoints'][str(j['epoch'])]['sha256'],'Output mismatch')
    names[row['name']]=x['response'];f.write(json.dumps(x,ensure_ascii=False)+'\n')
  tmp.replace(folder/'predictions.jsonl')
  import numpy as np
  with (folder/'name2reason.npz.tmp').open('wb') as f:np.savez_compressed(f,name2reason=names)
  (folder/'name2reason.npz.tmp').replace(folder/'name2reason.npz')
  j.update(state='complete',finished_at_beijing=now(),prediction_path=str(folder/'predictions.jsonl'),official_npz=str(folder/'name2reason.npz'));dump(jf,j)
 finally:h.close()
def verify_cache(run,p,row,inventory):
 f=run/'cache'/(key(row['sample_id'])+'.json');require(sha(f)==inventory[row['sample_id']]['sha256'],'Cache changed')
 b=read(f);require(b['cache_id']==inventory[row['sample_id']]['cache_id'] and b['plan_id']==p['plan_id'] and b['sample_id']==row['sample_id'],'Cache binding mismatch');return b
def worker(run,node,slot):
 p=plan(run);state=dict(node=node,slot=slot,pid=os.getpid(),completed_samples=0,started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());dump(run/'workers'/f'{node}_{slot}.json',state)
 try:
  update(state='loading')
  import torch
  import amg_inference.model as original
  original.make_prompt=make_prompt
  with lock(run/f'loading_{node}.lock',True):model=original.Predictor(p);model.load(p['checkpoints']['30'])
  update(state='probe_ready')
  deadline=time.monotonic()+2400
  while not (run/f'probe_go_{node}.json').exists():
   require(time.monotonic()<deadline,'Probe ready timeout');time.sleep(2)
  source=read(run/'source_probe.json');previous=model.chat.stopping_criteria
  try:_,info=model.predict(source['record'],source['evidence'],42+slot,stress=True)
  finally:model.chat.stopping_criteria=previous
  require(1530<=info['stress_prompt_tokens']<=1536 and info['stress_generated_tokens']==1200,'Full window probe failed')
  dump(run/'workers'/f'capacity_{node}_{slot}.json',dict(passed=True,info=info,peak_allocated=int(torch.cuda.max_memory_allocated()),plan_id=p['plan_id']))
  update(state='probe_passed')
  while not (run/f'probe_accepted_{node}.json').exists():time.sleep(2)
  inventory=read(run/'cache_inventory.json')
  for epoch in p['checkpoints']:
   spec=p['checkpoints'][epoch]
   with lock(run/f'loading_{node}.lock',True):model.load(spec)
   # One source example verifies generation after each checkpoint restoration.
   response,info=model.predict(source['record'],source['evidence'],42)
   dump(run/'workers'/f'smoke_{node}_{slot}_{epoch}.json',dict(passed=isinstance(response,str) and bool(response.strip()),checkpoint=spec,response=response,prompt_info=info))
   require(isinstance(response,str) and response.strip(),'Empty source smoke response')
   files=sorted((run/'shards').glob(f'epoch_{int(epoch):03d}_*.json'),key=lambda f:(-p['datasets'][read(f)['dataset']]['samples'],f.name))
   while True:
    pending=False;worked=False
    for f in files:
     s=read(f)
     if s['state']=='complete':continue
     if s['state']=='failed':raise RuntimeError('Shard failed: '+f.name)
     pending=True;h=lock(f.with_suffix('.lock'))
     if h is None:continue
     try:
      s=read(f)
      if s['state']=='complete':continue
      require(s['attempts']<3,'Shard exhausted retries');s.update(state='running',attempts=s['attempts']+1,node=node,slot=slot,pid=os.getpid());dump(f,s)
      update(state='inference',epoch=int(epoch),job_id=s['job_id'],shard=f.name)
      folder=run/'predictions'/s['job_id'];folder.mkdir(exist_ok=True)
      binding=canonical([p['plan_id'],spec['sha256'],p['datasets'][s['dataset']]['sha256']])
      for row in read(p['datasets'][s['dataset']]['path'])[s['start']:s['stop']]:
       dest=folder/(key(row['sample_id'])+'.json');b=verify_cache(run,p,row,inventory)
       if dest.exists():
        x=read(dest);require(x['binding']==binding and x['cache_id']==b['cache_id'],'Stale prediction')
       else:
        seed=(42+int(key(row['sample_id'])[:8],16))%2**32
        started=time.monotonic();response,info=model.predict(row,b['evidence'],seed);require(isinstance(response,str) and response.strip(),'Empty model response')
        dump(dest,dict(sample_id=row['sample_id'],name=row['name'],dataset=s['dataset'],epoch=int(epoch),response=response,checkpoint=spec,plan_id=p['plan_id'],binding=binding,cache_id=b['cache_id'],graph_release_id=p['graph_release_id'],query_config_id=p['query_config_id'],policy='D=compact+gate+Graph-OOF inference',seed=seed,prompt_info=info,node=node,slot=slot,elapsed_seconds=time.monotonic()-started,created_at_beijing=now()))
       state['completed_samples']+=1;update(last_sample_id=row['sample_id'])
      s.update(state='complete',finished_at_beijing=now());dump(f,s);finalize(run,p,s['job_id']);worked=True
     except BaseException as e:
      s.update(state='pending' if s.get('attempts',0)<3 else 'failed',error=repr(e));dump(f,s);raise
     finally:h.close()
    if not pending or all(read(f)['state']=='complete' for f in files):break
    if not worked:time.sleep(3)
  update(state='complete',finished_at_beijing=now())
 except BaseException as e:update(state='failed',error=repr(e),traceback=traceback.format_exc());raise
def node(run,name):
 controller=lock(run/f'node_{name}.lock')
 require(controller is not None,'Node controller already active')
 p=plan(run);procs={}
 def update(**kw):dump(run/f'node_{name}.json',dict(node=name,pid=os.getpid(),time_beijing=now(),**kw))
 def launch(slot):
  with (run/f'{name}_{slot}.log').open('ab',buffering=0) as f:
   return subprocess.Popen([PYTHON,'-u','-B','-m','amg_base7_graph10.run','worker','--run',str(run),'--node',name,'--slot',str(slot)],cwd=ROOT,env=env(),stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
 try:
  snap=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.used','--format=csv,noheader,nounits'],text=True).strip().split(',')
  require(snap[0].strip()==p['nodes'][name]['gpu_uuid'],'Wrong physical GPU');require(int(snap[1])<512,'GPU not idle')
  require(read(run/'cache_manifest.json')['complete'],'Preparation not complete')
  for f in [run/f'probe_go_{name}.json',run/f'probe_accepted_{name}.json']:f.unlink(missing_ok=True)
  for slot in range(3):
   (run/'workers'/f'capacity_{name}_{slot}.json').unlink(missing_ok=True);(run/'workers'/f'{name}_{slot}.json').unlink(missing_ok=True);procs[slot]=launch(slot)
  deadline=time.monotonic()+2400
  while True:
   require(all(z.poll() is None for z in procs.values()),'Worker exited before probe')
   states=[read(run/'workers'/f'{name}_{s}.json') if (run/'workers'/f'{name}_{s}.json').exists() else {} for s in range(3)]
   update(state='capacity_probe',workers=states)
   if all(s.get('state')=='probe_ready' for s in states):
    dump(run/f'probe_go_{name}.json',dict(time_beijing=now(),workers=3));break
   require(time.monotonic()<deadline,'Model loading timeout');time.sleep(5)
  while not all((run/'workers'/f'capacity_{name}_{s}.json').exists() for s in range(3)):
   require(all(z.poll() is None for z in procs.values()),'Capacity worker failed');require(time.monotonic()<deadline,'Capacity probe timeout');time.sleep(5)
  dump(run/f'probe_accepted_{name}.json',dict(passed=True,workers=3,gpu_uuid=snap[0].strip(),plan_id=p['plan_id'],time_beijing=now()))
  retries=Counter()
  while procs:
   update(state='running',pids={s:z.pid for s,z in procs.items()})
   for slot,z in list(procs.items()):
    if z.poll() is None:continue
    if z.returncode==0:del procs[slot];continue
    retries[slot]+=1;require(retries[slot]<=2,'Worker repeated failure, see slot log')
    time.sleep(3);procs[slot]=launch(slot)
   time.sleep(10)
  require(all(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json')),'Incomplete exports')
  update(state='complete',jobs=63,samples=89593)
 except BaseException as e:
  update(state='failed',error=repr(e),traceback=traceback.format_exc())
  for z in procs.values():
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:controller.close()
def status(run):
 jobs=[read(f) for f in (run/'jobs').glob('*.json')];workers=[read(f) for f in (run/'workers').glob('A*.json')]
 shards=[read(f) for f in (run/'shards').glob('*.json')]
 out=dict(run=str(run),time_beijing=now(),jobs=dict(Counter(j['state'] for j in jobs)),completed_shard_predictions=sum(s['samples'] for s in shards if s['state']=='complete'),workers=workers)
 print(json.dumps(out,ensure_ascii=False,indent=2));dump(run/'status.json',out)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','worker','node','status']);a.add_argument('--run',required=True);a.add_argument('--node',choices=['A800','A100']);a.add_argument('--slot',type=int);x=a.parse_args();run=Path(x.run)
 if x.mode=='prepare':prepare(run)
 elif x.mode=='worker':worker(run,x.node,x.slot)
 elif x.mode=='node':node(run,x.node)
 else:status(run)
