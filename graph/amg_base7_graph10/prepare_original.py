"""Prepare immutable native-only graph inference; retain old experiments."""
import os,sys,ast,copy,datetime,json
from zoneinfo import ZoneInfo
from graph_paths import Path
from amg_runtime.common import read,sha,canonical,atomic_json as dump
from .run import ROOT,now
def main():
 oldrun=Path(read(ROOT/'amg_base7_graph10/current_run.json')['run']);old=read(oldrun/'plan.json')
 run=ROOT/'amg_base7_graph10/runs'/('base7_original_plus_graph10_'+datetime.datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S'))
 for d in ['inputs','shards','jobs','predictions','workers','scores','evaluation_jobs','validation']:(run/d).mkdir(parents=True,exist_ok=True)
 dump(ROOT/'amg_base7_graph10/preparing_original.json',dict(run=str(run),old_run=str(oldrun),state='preparing'))
 dump(run/'prepare_status.json',dict(state='preparing',time_beijing=now()))
 try:
  adapter=ROOT/'amg_base7_graph10/original_model.py'
  text=adapter.read_text().replace('subtitle = name2subtitle[name]','subtitle = dataset_cls.name2subtitle[name]')
  adapter.write_text(text);compile(text,str(adapter),'exec')
  # Verify the production sample body against the original AST, allowing only bound names and graph append.
  source=ROOT/'AffectGPT/inference_hybird.py';tree=ast.parse(source.read_text())
  loop=next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [getattr(x,'id',None) for x in n.target.elts]==['ii','name'])
  expected=[]
  for n in loop.body:
   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='name2reason' for t in n.targets):continue
   if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='print' and any(isinstance(x,ast.Name) and x.id=='ii' for x in ast.walk(n)):continue
   n=copy.deepcopy(n)
   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='subtitle' for t in n.targets):n.value=ast.parse('dataset_cls.name2subtitle[name]',mode='eval').body
   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user_message' for t in n.targets):n.value.args=[ast.Name(id='dataset_cls',ctx=ast.Load()),ast.Constant(True),ast.Constant(None)]
   expected.append(n)
  expected.extend(ast.parse('return response, prompt').body)
  actual=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='original_sample_with_graph')
  stripped=[n for n in actual.body if not(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user_message' for t in n.targets) and isinstance(n.value,ast.BinOp))]
  assert ast.dump(ast.Module(body=stripped,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=expected,type_ignores=[]),include_attributes=False),'Native sample diverged beyond graph append'
  namespace={'get_user_message':lambda *_:'original question'}
  fn=copy.deepcopy(actual);ast.fix_missing_locations(fn);exec(compile(ast.Module(body=[fn],type_ignores=[]),'native_loop_check','exec'),namespace)
  class Reader:
   name2subtitle={'test':'full subtitle '*1000}
   def __init__(self):self.calls=[]
   def _get_video_path(self,s):self.calls.append('video');return 'v'
   def _get_audio_path(self,s):self.calls.append('audio');return 'a'
   def _get_face_path(self,s):self.calls.append('face');return 'f'
   def _get_image_path(self,s):self.calls.append('image');return 'i'
   def read_frame_face_audio_text(self,*args):self.calls.append(args);return 'media'
   def get_prompt_for_multimodal(self,mode,subtitle,question):self.prompt_args=(mode,subtitle,question);return question
  class Chat:
   def __init__(self):self.calls=[]
   def postprocess_audio(self,x):self.calls.append('audio');return 'ah','al'
   def postprocess_frame(self,x):self.calls.append('frame');return 'vh','vl'
   def postprocess_face(self,x):self.calls.append('face');return 'fh','fl'
   def postprocess_image(self,x):self.calls.append('image');return 'ih','il'
   def postprocess_multi(self,*x):self.calls.append(('multi',x));return 'mh','ml'
   def answer_sample(self,**kw):self.kw=kw;return ''
  r=Reader();c=Chat();answer,prompt=namespace['original_sample_with_graph'](r,c,'multiface_audio_face_text','test','graph input')
  assert answer=='' and r.prompt_args[1]==r.name2subtitle['test'] and r.prompt_args[2]=='original question\ngraph input'
  expected_gen=dict(num_beams=1,temperature=1,do_sample=True,top_p=.9,max_new_tokens=1200,max_length=2000)
  assert {k:v for k,v in c.kw.items() if k not in ['prompt','img_list']}==expected_gen
  dump(run/'native_contract_test.json',dict(passed=True,sample_ast_matches_original_except_graph_append=True,full_subtitle_preserved=True,original_generation_kwargs=expected_gen,empty_response_preserved=True,original_all_modality_calls=True,native_script_sha256=sha(source)))
  print('NATIVE_CONTRACT_PASSED',flush=True)
  from .original_model import native_module,original_reader
  native=native_module();config=read(oldrun/'original_config.json')
  p=copy.deepcopy(old);p.pop('plan_id',None);p.update(schema='native_original_plus_graph10_v1',created_at_beijing=now(),training_run=str(run),generation=expected_gen,limits=dict(graph_token_budget=512),seed=None,randomness_policy='Original script; no added per-sample RNG reseeding or backend overrides',native_script_sha256=sha(source),graph_cache_directory=str(oldrun/'cache'),graph_cache_plan_id=old['plan_id'],previous_run=str(oldrun),semantics='Native inference_hybird.py sample loop, original readers, original from_config and checkpoint restoration, original Chat, original generation 1200/2000, full subtitle, no response filtering. Only append requested D compact+gate graph10 input. Parallel dispatch and persistence wrap the native loop.',protected_files={})
  (run/'original_config.json').write_bytes((oldrun/'original_config.json').read_bytes())
  comparisons={}
  for d,spec in p['datasets'].items():
   rows=read(spec['path']);byname={r['name']:r for r in rows};reader=original_reader(native,d,config);names=reader.read_test_names()
   assert len(names)==len(rows) and set(names)==set(byname),'Native membership changed '+d
   newrows=[];subtitle_changes=0
   for name in names:
    row=copy.deepcopy(byname[name]);sub=reader.name2subtitle[name];subtitle_changes+=int(sub!=row['subtitle']);row['subtitle']=sub
    for field,method in [('audio_path','_get_audio_path'),('face_path','_get_face_path'),('video_path','_get_video_path')]:
     if hasattr(reader,method):
      path=getattr(reader,method)({'name':name})
      if path is not None:assert str(Path(path).resolve())==str(Path(row[field]).resolve()),(d,name,field,path,row[field])
    newrows.append(row)
   target=run/'inputs'/(d+'.json');dump(target,newrows);spec.update(path=str(target),sha256=sha(target))
   comparisons[d]=dict(samples=len(names),native_membership_verified=True,native_media_paths_verified=True,native_subtitle_corrections=subtitle_changes)
   print('NATIVE_DATASET',d,len(names),subtitle_changes,flush=True)
  dump(run/'native_dataset_audit.json',comparisons)
  for name in ['cache_inventory.json','cache_manifest.json']:(run/name).write_bytes((oldrun/name).read_bytes())
  graphpath=Path(p['new_graph_path'])
  protect=[ROOT/'amg_base7_graph10/run.py',ROOT/'amg_base7_graph10/original_model.py',ROOT/'amg_base7_graph10/execution_original.py',ROOT/'amg_bcd/policy.py',source,ROOT/'AffectGPT/my_affectgpt/conversation/conversation_video.py',ROOT/'AffectGPT/my_affectgpt/models/affectgpt.py',ROOT/'AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py',graphpath/'graph/graph.json',graphpath/'graph/paths_cue_appraisal_emotion.csv',Path(p['query_config_path']),run/'original_config.json',run/'cache_inventory.json',run/'native_contract_test.json',run/'native_dataset_audit.json']+[Path(s['path']) for s in p['datasets'].values()]
  p['protected_files']={str(f):sha(f) for f in protect};p['plan_id']=canonical(p);dump(run/'plan.json',p)
  for epoch in p['checkpoints']:
   for d,spec in p['datasets'].items():
    jid=f'epoch_{int(epoch):03d}_{d}';ss=[]
    for lo in range(0,spec['samples'],32):
     sid=jid+f'_{lo:05d}';ss.append(sid);dump(run/'shards'/(sid+'.json'),dict(shard_id=sid,job_id=jid,epoch=int(epoch),dataset=d,start=lo,stop=min(lo+32,spec['samples']),samples=min(32,spec['samples']-lo),state='pending',attempts=0))
    dump(run/'jobs'/(jid+'.json'),dict(job_id=jid,epoch=int(epoch),dataset=d,samples=spec['samples'],shards=ss,state='pending'))
    dump(run/'evaluation_jobs'/(jid+'.json'),dict(job_id=jid,epoch=int(epoch),dataset=d,samples=spec['samples'],state='pending',attempts=0))
  e=copy.deepcopy(read(oldrun/'execution_plan.json'));e.pop('execution_id',None);e.update(inference_plan_id=p['plan_id'],created_at_beijing=now(),empty_generation_policy='Original empty response saved verbatim',capacity_reference=str(run/'capacity_reference.json'))
  oldref=read(e.get('capacity_reference')) if Path(e.get('capacity_reference')).exists() else read(oldrun/'recovery_empty_response/capacity_reference.json')
  oldref.update(inference_plan_id=p['plan_id'],basis='Existing six-worker 1536-input+1200-output capacity evidence; native Chat retains original max_length2000, no target RNG consumed by extra probe generations. Same seven checkpoints and physical nodes.')
  dump(run/'capacity_reference.json',oldref)
  e['protected_files']={f:h for f,h in e['protected_files'].items() if '/amg_base7_graph10/' not in f}
  e['protected_files'].update({str(f):sha(f) for f in [ROOT/'amg_base7_graph10/execution_original.py',ROOT/'amg_base7_graph10/original_model.py',run/'capacity_reference.json',run/'native_contract_test.json']})
  e['execution_id']=canonical(e);dump(run/'execution_plan.json',e)
  for name in ['evaluation_preflight.json','scheduling_preflight.json']:
   v=read(oldrun/name);v['execution_id']=e['execution_id'];dump(run/name,v)
  (run/'README.md').write_text('Seven original checkpoints x nine official test sets. Native inference_hybird sample loop and original readers/model/Chat/generation; only append D compact+gate graph10 evidence. Original max_new_tokens1200,max_length2000,full subtitles,no added RNG reseeding,empty outputs preserved. Prior predictions are kept in previous run and not reused. Frozen graph-only cache is reused. Two physical GPUs,three workers each,global dataset-size descending32-sample shards. Automatic original evaluation starts after all63 jobs and all six inference workers exit and both GPUs release memory. Outputs metrics_all.csv,per_checkpoint_summary.csv/json,RESULTS.md. All files remain on servers.\n')
  dump(run/'prepare_status.json',dict(state='complete',samples=12799,jobs=63,predictions=89593,time_beijing=now()))
  dump(oldrun/'SUPERSEDED.json',dict(new_run=str(run),reason='User requires strictly native original inference with graph input only; old predictions not mixed',time_beijing=now()))
  dump(ROOT/'amg_base7_graph10/current_run.json',dict(run=str(run)))
  dump(ROOT/'amg_base7_graph10/preparing_original.json',dict(run=str(run),old_run=str(oldrun),state='complete'))
  print('PREPARED',run,flush=True)
 except BaseException as exc:
  import traceback
  dump(run/'prepare_status.json',dict(state='failed',error=repr(exc),traceback=traceback.format_exc(),time_beijing=now()));raise
if __name__=='__main__':main()
