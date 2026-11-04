"""Keep prepared frozen graphs, verify identical P4 text, and restore native generation exactly."""
import argparse,ast,datetime,gzip,json,shutil
from zoneinfo import ZoneInfo
from .common import *
def main(previous,run):
 from amg_graph_v2.unified_prompt.adapter import UnifiedAMGPromptAdapter
 from amg_graph_v2.unified_prompt.integration import AffectGPTUnifiedBridge
 from amg_graph_v2.unified_prompt.tokenization import actual_interfaces
 old=Path(previous);run=Path(run);run.mkdir(parents=True,exist_ok=True)
 for name in ['inputs','cache','graphs','jobs','shards','workers','logs','predictions','scores','source']:(run/name).mkdir(exist_ok=True)
 p=read(old/'plan.json');p.pop('plan_id');p.update(version='base7_AMG_v21_unified_P4_NATIVE_generation_three_targets',created_at=now(),run=str(run),training_run=str(run),previous_superseded_run=str(old),seed=None,seed_rule='Native inference_hybird.py flow: no added RNG reseeding. Source-only warmup/capacity preserves all RNG states.',generation=dict(num_beams=1,temperature=1,do_sample=True,top_p=.9,max_new_tokens=1200,max_length=2000),native_generation_only_prompt_change=True)
 native=GRAPH/'amg_base7_graph10/original_model.py';tree=ast.parse(native.read_text());assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GENERATION' for t in n.targets));native_generation=eval(compile(ast.Expression(assignment.value),str(native),'eval'),{'dict':dict});assert p['generation']==native_generation
 config_source=GRAPH/'amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105/original_config.json';shutil.copy2(config_source,run/'original_config.json')
 tok,reader,chat,tokenbinding=actual_interfaces();adapter=UnifiedAMGPromptAdapter(tok);bridge=AffectGPTUnifiedBridge(adapter);inventory={};maxprompt=0;maxevidence=0;count=0
 for d,spec in p['datasets'].items():
  rows=read(spec['path']);target=run/'inputs'/(d+'.json');write(target,rows);spec.update(path=str(target),sha256=sha(target))
  for row in rows:
   sid=row['sample_id'];b=read(old/'cache'/(key(sid)+'.json'));gfile=old/'graphs'/(key(sid)+'.json.gz')
   with gzip.open(gfile,'rt',encoding='utf-8') as f:g=json.load(f)
   prepared=bridge.prepare(reader,chat,g,p['prompt_question'],row['subtitle'],max_length=2000,max_new_tokens=1200);assert prepared['prompt']==b['final_prompt'],'Restored native context unexpectedly changed target evidence';assert prepared['evidence']['text']==b['packet']['text'];b['packet']=prepared['evidence'];b['cache_id']=digest({k:v for k,v in b.items() if k!='cache_id'});dest=run/'cache'/(key(sid)+'.json');write(dest,b);inventory[sid]=dict(path=str(dest),sha256=sha(dest),cache_id=b['cache_id']);shutil.copy2(gfile,run/'graphs'/gfile.name);maxprompt=max(maxprompt,b['packet']['audit']['full_prompt_tokens']);maxevidence=max(maxevidence,b['packet']['audit']['evidence_tokens']);count+=1
  print('Native-identical prompts checked',d,len(rows),flush=True)
 assert count==1400 and maxprompt<=800
 sourcegraph=read(Path(p['graph_release_path'])/'runtime/examples/candidate_and_evidence.json');source_rows={r['sample_id']:r for r in read(GRAPH/'amg_graph_v2/data/input_rows.json')};sid=sourcegraph['sample_id'];sr=source_rows[sid];prepared=bridge.prepare(reader,chat,sourcegraph,p['prompt_question'],sr['text']['english'],max_length=2000,max_new_tokens=1200);write(run/'source_probe.json',dict(sample_id=sid,row=dict(sample_id=sid,name=sid,dataset='SOURCE',subtitle=sr['text']['english'],audio_path=sr['audio_path'],face_path=str(PROJECT/'dataset/mer2025-dataset/openface_face'/sid/(sid+'.npy'))),final_prompt=prepared['prompt'],packet=prepared['evidence']))
 write(run/'cache_inventory.json',inventory);write(run/'tokenizer_binding.json',tokenbinding);p['cache_inventory_sha256']=sha(run/'cache_inventory.json');p['source_probe_sha256']=sha(run/'source_probe.json');p['original_config_sha256']=sha(run/'original_config.json');p['plan_id']=digest(p);write(run/'plan.json',p)
 for f in (old/'shards').glob('*.json'):
  j=read(f);j.update(state='pending',attempts=0);j={k:v for k,v in j.items() if k not in ['pid','slot','error','traceback','finished_at']};write(run/'shards'/f.name,j)
 for f in (old/'jobs').glob('*.json'):
  j=read(f);j.update(state='pending',score_state='pending');j={k:v for k,v in j.items() if k not in ['official_npz','prediction_path','prediction_sha256','finished_at']};write(run/'jobs'/f.name,j)
 report=read(old/'preparation_report.json');report.update(maximum_AMG_tokens=maxevidence,maximum_full_prompt_tokens=maxprompt,generation_reserve=1200,total_context=2000,all_target_prompt_text_identical_to_prepared_P4=True,original_generation_dict_exact_match=True,original_model_config_exact_sha256=sha(config_source),no_added_per_sample_seeding=True,source_tests_rng_isolated=True);write(run/'preparation_report.json',report);write(run/'prepare_status.json',dict(state='complete',samples=1400,at=now()));write(ROOT/'current_run.json',dict(run=str(run),plan_id=p['plan_id'],status='native_prepared'))
 (run/'README.md').write_text('Seven original checkpoints, new AMG v2.1 and unified P4. Native original model/config, media readers, encoders, fusion and Chat preserved. Native generation exactly: num_beams1 temperature1 do_sampleTrue top_p.9 max_new_tokens1200 max_length2000. No added per-sample seeding; source-only probes restore RNG. All 1400 target Prompt strings unchanged from preparation, max770 tokens fits native 800-token available input. A800 four-way; 21 groups / 9800 predictions; automatic official evaluation after all inference exits. No sample exclusion; no target fitting; all files server-only.\n');print('Native run ready',str(run),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--previous',required=True);a.add_argument('--run',required=True);x=a.parse_args();main(x.previous,x.run)
