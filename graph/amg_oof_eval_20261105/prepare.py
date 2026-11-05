import argparse,collections,gzip,json,shutil,time,sys
import numpy as np
from .common import *
def main(run):
 from amg_runtime.common import canonical
 sys.path.insert(0,str(Path(read(GRAPH/'amg_graph_v2/current_student_oof.json')['path'])/'runtime/source'))
 from amg_oof_release.runtime_oof import SampleGraphOOF
 from .prompt.adapter import UnifiedAMGPromptAdapter
 from .prompt.integration import AffectGPTUnifiedBridge
 from .prompt.tokenization import actual_interfaces
 run=Path(run);run.mkdir(parents=True,exist_ok=True)
 for d in ['inputs','cache','graphs','jobs','shards','workers','logs','predictions','scores','source']: (run/d).mkdir(exist_ok=True)
 old=GRAPH/'amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105';op=read(old/'plan.json');ap=read(GRAPH/'amg_graph_v2/current_unified_prompt.json');gp=read(GRAPH/'amg_graph_v2/current_student_oof.json');assert gp['status']=='verified_internal_oof_release';assert ap['acceptance_passed']
 graph=SampleGraphOOF(gp['path']);t,reader,chat,tokenbinding=actual_interfaces();adapter=UnifiedAMGPromptAdapter(t);bridge=AffectGPTUnifiedBridge(adapter);config=read(old/'original_config.json');write(run/'original_config.json',config)
 directory=PROJECT/'AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230';checkpoints={}
 for f in sorted(directory.glob('checkpoint_*.pth')):
  epoch=int(f.name.split('_')[1]);checkpoints[str(epoch)]=dict(path=str(f),epoch=epoch,sha256=sha(f))
 assert set(checkpoints)=={'30','35','40','45','50','55','60'}
 generation=dict(num_beams=1,temperature=1,do_sample=True,top_p=.9,max_new_tokens=1200,max_length=2000)
 p=dict(version='base7_Student_OOF_graph_unified_P4_NATIVE_two_nodes_three_targets',created_at=now(),run=str(run),training_run=str(run),checkpoints=checkpoints,datasets={},generation=generation,prompt_question='Please recognize all possible emotional states of the character.',graph_release_id=gp['release_id'],graph_release_path=gp['path'],prompt_release_id='unified_P4_OOF_'+digest({f.name:sha(f) for f in sorted((ROOT/'prompt').iterdir()) if f.is_file()})[:16],prompt_release_path=str(ROOT/'prompt'),prompt_parent_release_id=ap['release_id'],concurrency=8,concurrency_per_gpu=4,nodes=['A800','A100'],per_process_memory_fraction=.24,seed=None,seed_rule='Native inference_hybird.py: no added per-sample RNG reseeding',logical_jobs=21,total_predictions=9800,shard_size=16,target_labels_used_for_prompt_selection=False,Student_retrained=False,G1_refitted=False,graph_relationships_trained_from_Student_OOF=True,calibration_or_threshold_changed=False,excluded_samples=0,ovmerd_mapping='Repository OVMERDPlus official 532-sample test split')
 inventory={};records={};stats=collections.Counter();counts=[];fullcounts=[];cachebase=GRAPH/'amg_inference/runs/graph_225_20261022_174537/cache'
 for d in ['MER2023','SIMS','OVMERDPlus']:
  source=old/'inputs'/(d+'.json');rows=read(source);assert len(rows)=={'MER2023':411,'SIMS':457,'OVMERDPlus':532}[d];assert len({r['name'] for r in rows})==len(rows);dest=run/'inputs'/(d+'.json');write(dest,rows);p['datasets'][d]=dict(op['datasets'][d],path=str(dest),sha256=sha(dest));stats[d]=len(rows)
  for row in rows:
   f=cachebase/(canonical(row['sample_id'])+'.json');cached=read(f);assert cached['cache_id']==canonical({k:v for k,v in cached.items() if k!='cache_id'});assert cached['sample_id']==row['sample_id'];safe={k:row[k] for k in ['sample_id','text','audio_path','video_path']};assert cached['input_id']==canonical(safe),'Old Cue input differs'
   for field in ['audio_path','face_path','video_path']:assert Path(row[field]).is_file(),field+' absent '+row['sample_id']
   g=graph.build_from_old_cue(cached['cue']);prepared=bridge.prepare(reader,chat,g,p['prompt_question'],row['subtitle'],max_length=2000,max_new_tokens=1200);packet=prepared['evidence'];b=dict(sample_id=row['sample_id'],dataset=d,name=row['name'],row_sha256=digest(row),source_cue_cache_id=cached['cache_id'],source_cue_cache_sha256=sha(f),graph_release_id=gp['release_id'],prompt_release_id=p['prompt_release_id'],packet=packet,final_prompt=prepared['prompt']);b['cache_id']=digest(b);out=run/'cache'/(key(row['sample_id'])+'.json');write(out,b);inventory[row['sample_id']]=dict(path=str(out),sha256=sha(out),cache_id=b['cache_id']);records[row['sample_id']]=row;counts.append(packet['audit']['evidence_tokens']);fullcounts.append(packet['audit']['full_prompt_tokens']);stats['fallback']+=int(packet['audit']['fallback']);stats['CA_relations']+=packet['audit']['CA_edge_count'];stats['CE_relations']+=packet['audit']['CE_edge_count']
   with gzip.open(run/'graphs'/(key(row['sample_id'])+'.json.gz'),'wt',encoding='utf-8') as z:z.write(json.dumps(g,ensure_ascii=False,separators=(',',':')))
   if len(inventory)%100==0:write(run/'prepare_status.json',dict(state='preparing_frozen_target_prompts',completed=len(inventory),total=1400,at=now()));print('target prompts',len(inventory),'/1400',flush=True)
 assert len(inventory)==1400 and max(fullcounts)<=800 and max(counts)<=1000
 write(run/'cache_inventory.json',inventory);write(run/'tokenizer_binding.json',tokenbinding);p['cache_inventory_sha256']=sha(run/'cache_inventory.json')
 oldprobe=read(GRAPH/'amg_unified_eval/runs/base7_unified_P4_NATIVE_A800_20261103_214723/source_probe.json')
 write(run/'source_probe.json',oldprobe)
 p['prompt_policy_sha256']=digest({f.name:sha(f) for f in sorted((ROOT/'prompt').iterdir()) if f.is_file()});p['source_probe_sha256']=sha(run/'source_probe.json');p['original_config_sha256']=sha(run/'original_config.json');p['plan_id']=digest(p);write(run/'plan.json',p)
 for epoch in checkpoints:
  for d,spec in p['datasets'].items():
   jid=f'epoch_{int(epoch):03d}_{d}';shards=[]
   for start in range(0,spec['samples'],16):
    shard=jid+f'_{start:05d}';shards.append(shard);write(run/'shards'/(shard+'.json'),dict(id=shard,job_id=jid,epoch=int(epoch),dataset=d,start=start,stop=min(start+16,spec['samples']),state='pending',attempts=0))
   write(run/'jobs'/(jid+'.json'),dict(id=jid,epoch=int(epoch),dataset=d,samples=spec['samples'],shards=shards,state='pending',score_state='pending'))
 write(run/'preparation_report.json',dict(passed=True,unique_target_samples=1400,checkpoints=7,inference_groups=21,total_predictions=9800,target_membership_unchanged=True,excluded_samples=0,statistics=dict(stats),maximum_AMG_tokens=max(counts),maximum_full_prompt_tokens=max(fullcounts),generation_reserve=1200,total_context=2000,capacity_probe=False,extra_smoke_generations=False,prompt_and_graph_frozen=True,no_target_labels_used_for_selection=True))
 write(run/'prepare_status.json',dict(state='complete',samples=1400,at=now()));write(ROOT/'current_run.json',dict(run=str(run),plan_id=p['plan_id'],status='prepared'));print('Prepared',str(run),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);main(a.parse_args().run)
