"""CPU validation of frozen D settings, original starts, nine-set routing and reuse."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,copy,os,sys,shutil
from .common import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);a=ap.parse_args();run=Path(a.run);p=plan(run);pkg=ROOT/'amg_d_multistart10';previous=Path(p['source_previous_run']);old=plan(previous)
 for f in pkg.glob('*.py'):compile(f.read_text(),str(f),'exec')
 records=read(run/'train_records.json');audit=read(run/'human_audit_500.json');labels=read(run/'polarity_labels.json');ids={r['sample_id'] for r in records}
 require(len(records)==len(ids)==30755 and len(audit)==500 and not ids&{r['sample_id'] for r in audit},'Training/audit mismatch')
 for name,key in [('train_records.json','train_records_sha256'),('human_audit_500.json','audit_records_sha256')]:require(_graph_hash_matches(run / name, p['inputs'][key], sha(run / name)),'Source data changed')
 require(_graph_hash_matches(run / 'polarity_labels.json', p['polarity_labels_sha256'], sha(run / 'polarity_labels.json')) and {r['sample_id'] for r in labels}==ids,'Polarity labels changed')
 require(sum(r['valid_for_polarity_loss'] for r in labels)==30688 and sum(not r['valid_for_polarity_loss'] for r in labels)==67,'Polarity mask changed')
 for key,value in old['training'].items():
  if key not in ['additional_epochs','supervision']:require(p['training'][key]==value,'D training setting drift: '+key)
 require(p['training']['additional_epochs']==10 and p['policy']==old['policy'] and p['graph_release_id']==old['graph_release_id'],'Graph/method changed')
 for name in ['policy.py','auxiliary.py']:require(_graph_hash_matches(pkg / name, sha(ROOT / 'amg_bcd_polarity_oof' / name), sha(pkg / name)),'Loss/format code changed')
 accepted=read(run/'oof_reuse_verification.json');require(accepted['passed'] and _graph_hash_matches(run / 'oof_cache_inventory.json', accepted['inventory_sha256'], sha(run / 'oof_cache_inventory.json')),'Accepted OOF inventory changed')
 inventory=read(run/'oof_cache_inventory.json');require(set(inventory)==ids,'OOF membership changed')
 for path,digest in accepted['files_sha256'].items():require(_graph_hash_matches(path, digest, sha(path)),'OOF source resource changed')
 require(_graph_hash_matches(run / 'query_engine_config.json', p['inputs']['query_config_sha256'], sha(run / 'query_engine_config.json')) and canonical(read(run/'query_engine_config.json'))==p['query_config_id'],'Frozen query changed')
 for filename,binding in read(run/'model_assets_manifest.json')['assets'].items():
  st=Path(filename).stat();require(st.st_size==binding['bytes'] and st.st_mtime_ns==binding['mtime_ns'],'Pretrained assets changed')
 sys.path.insert(0,str(ROOT/"AffectGPT"))
 from .dataset import graph_enabled
 masks={v:[graph_enabled(r['sample_id'],1,v) for r in records] for v in p['variants']};require(all(mask==masks['from_35'] for mask in masks.values()),'Paired graph masks changed');fraction=sum(masks['from_35'])/30755;require(.49<fraction<.51,'Wrong graph keep probability')
 import torch
 base35=read(previous/'plan.json')['base_checkpoint'];reference=torch.load(_graph_resolve_path(base35['path']), map_location='cpu', weights_only=True);architecture={k:tuple(v.shape) for k,v in reference['model'].items()};del reference
 checkpoints={}
 for v in p['new_training_variants']:
  vp=plan(run/(v+'_plan'));spec=vp['base_checkpoint'];require(spec['base_epoch']==p['variant_bases'][v] and vp['epochs']==list(range(spec['base_epoch']+1,spec['base_epoch']+11)),'Start/epoch mismatch')
  require(vp['variant_settings'][v]==dict(graph_probability=.5,polarity_loss_weight=.1) and spec['initialization']=='original_checkpoint','Wrong D settings/start')
  require(_graph_hash_matches(spec['path'], spec['sha256'], sha(spec['path'])),'Original starting checkpoint changed')
  ck=torch.load(_graph_resolve_path(spec['path']), map_location='cpu', weights_only=True);require(ck['epoch']==spec['base_epoch'] and ck.get('polarity_head') is None,'Wrong original checkpoint/head')
  require({k:tuple(t.shape) for k,t in ck['model'].items()}==architecture,'Original model architecture mismatch');require([len(g['params']) for g in ck['optimizer']['param_groups']]==[402,10],'Original optimizer mismatch')
  checkpoints[v]=dict(base_epoch=ck['epoch'],sha256=spec['sha256'],native_optimizer_groups=[402,10],new_head_seed=4242,additional_epochs=10,total_steps=50000);del ck
  print('ORIGINAL_CHECKPOINT_VERIFIED',v,flush=True)
 reuse=read(run/'reuse_manifest.json');require(reuse['reused_jobs']==len(reuse['scores'])==30,'Reuse count mismatch');reused=read(run/'from_35/checkpoints.json');require([c['epoch'] for c in reused]==list(range(36,46)),'Reused35 epochs wrong')
 for c in reused:
  require(_graph_hash_matches(c['path'], c['sha256'], sha(c['path'])),'Reused35 weight changed');source=Path(c['source_run']);vp=plan(source/(c['source_variant']+'_plan'));require(vp['plan_id']==c['training_plan_id'],'Reused35 training plan mismatch')
  require(c['continuation_base_epoch']==(35 if c['epoch']<=40 else 40),'Reused35 continuation base wrong')
 for jid,binding in reuse['scores'].items():
  for pathkey,shakey in [('job_path','job_sha256'),('score_path','score_sha256'),('raw_path','raw_sha256')]:require(_graph_hash_matches(binding[pathkey], binding[shakey], sha(binding[pathkey])),'Prior result changed')
  score=read(run/'scores'/(jid+'.json'));original=read(binding['score_path']);require(score['metrics']==original['metrics'] and score['main_score']==original['main_score'] and score['checkpoint']['sha256']==binding['checkpoint_sha256'],'Reused metrics changed')
 # Source graph caches are reused; all target evidence must match fixed graph/query and input versions.
 coverage={};cache_count=0
 for d,ds in p['datasets'].items():
  require(_graph_hash_matches(ds['path'], ds['sha256'], sha(ds['path'])),'Target manifest changed');target_rows=read(ds['path']);require(len(target_rows)==ds['samples'],'Target coverage changed');coverage[d]=len(target_rows)
  for row in target_rows:
   x=read(target_cache(p,row['sample_id']));require(x['sample_id']==row['sample_id'] and x['cache_id']==canonical({k:v for k,v in x.items() if k!='cache_id'}),'Target cache corrupt')
   require(x['evidence']['graph_release_id']==p['graph_release_id'] and x['evidence']['query_config_id']==p['query_config_id'],'Wrong target graph/query');cache_count+=1
  print('TARGET_CACHE_VERIFIED',d,len(target_rows),flush=True)
 require(cache_count==sum(coverage.values())==12799,'Wrong total target samples')
 source_lock=read(OLD_INFER/'evaluation_all_20261023_175630/evaluation_lock.json');prior_lock=read(previous/'evaluation_resources.json')
 for path,digest in source_lock['files_sha256'].items():require(_graph_hash_matches(path, digest, sha(path)),'Original evaluation resource changed')
 require(all(source_lock['files_sha256'][path]==digest for path,digest in prior_lock['files'].items()),'Reused three-set scoring protocol changed')
 lock=dict(files=source_lock['files_sha256'],source_lock_id=source_lock['lock_id'],original_sampling_preserved=True);lock['lock_id']=canonical(lock);atomic_json(run/'evaluation_resources.json',lock)
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/'AffectGPT'));import evaluation
 from amg_inference.full_score import truth,DISCRETE,DIMENSION
 require(DISCRETE=={'MER2023','MER2024','MELD','IEMOCAPFour'} and DIMENSION=={'CMUMOSI','CMUMOSEI','SIMS','SIMSv2'},'Metric routes wrong')
 truth_counts={d:len(truth(d,p,evaluation)) for d in p['datasets']};require(truth_counts==coverage,'Native ground-truth coverage differs')
 alljobs=jobs(run);pending=[j for j in alljobs if j['state']=='pending'];require(len(alljobs)==450 and len(pending)==420 and complete_count(run)==30,'Job counts wrong')
 require(sum(j['samples'] for j in pending)==625950 and sum(j['samples'] for j in alljobs)==639950,'Prediction budget wrong')
 require(len(list((run/'shards').glob('*.json')))==10010,'Shard budget wrong')
 require(len([j for j in pending if j['variant']=='from_35'])==60 and all(j['dataset'] not in ['MER2023','SIMS','OVMERDPlus'] for j in pending if j['variant']=='from_35'),'35 supplemental datasets wrong')
 # Exercise actual exclusive LPT selection against a small isolated queue.
 from .infer_worker import choose
 fixture=run/'claim_fixture';fixture.mkdir();(fixture/'jobs').mkdir();(fixture/'shards').mkdir();(fixture/'from_35').mkdir();atomic_json(fixture/'from_35/checkpoints.json',[dict(epoch=36,path='fixture',sha256='fixture')])
 for i,n in enumerate([411,4659,2610]):
  atomic_json(fixture/'shards'/f'{i}.json',dict(job_id=str(i),variant='from_35',epoch=36,dataset_samples=n,samples=64,state='pending',attempts=0))
  atomic_json(fixture/'jobs'/f'{i}.json',dict(job_id=str(i),variant='from_35',epoch=36,samples=n,state='pending',shards=[f'{i}.json']))
 first=choose(fixture,p);second=choose(fixture,p);require(first[2]['dataset_samples']==4659 and second[2]['dataset_samples']==2610,'LPT/exclusive scheduler failed');first[1].close();second[1].close()
 require(not (run/'evaluation_barrier.json').exists(),'Scoring started early')
 # Reuse native D causal/gradient checks; only epoch count/start/queue code changed.
 require(read(previous/'cpu_preflight.json')['passed'],'Prior D checks missing');free=shutil.disk_usage(ROOT).free;require(free>100*1024**3,'Insufficient disk for40 weights and predictions')
 paths=list(pkg.glob('*.py'))
 for folder in ['amg_finetune_nogc','amg_runtime','amg_inference']:paths+=list((ROOT/folder).glob('*.py'))
 paths += [run/'plan.json',run/'reuse_manifest.json',run/'oof_cache_inventory.json',run/'oof_reuse_verification.json',run/'from_35/checkpoints.json',ROOT/'AffectGPT/my_affectgpt/models/affectgpt.py',ROOT/'AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py']
 for v in p['variants']:paths+=[run/(v+'_plan')/'plan.json']
 manifest=dict(files={str(f.relative_to(ROOT)):sha(f) for f in paths},created_at_beijing=now());atomic_json(run/'code_manifest.json',manifest)
 for v in p['variants']:(run/(v+'_plan')/'code_manifest.json').symlink_to(run/'code_manifest.json')
 from .report import summarize
 require(summarize(run,p)==30,'Reused report count wrong')
 report=dict(passed=True,cpu_only=True,original_starts=checkpoints,reused_weights=10,new_weights=40,training_records=30755,audit_excluded=500,polarity_valid=30688,polarity_ignored=67,paired_graph_keep_fraction=fraction,accepted_grouped_graph_oof_verified=True,all_D_settings_preserved=True,target_caches_verified=12799,native_truth_counts=truth_counts,new_inference_jobs=420,reused_jobs=30,total_jobs=450,shards=10010,new_predictions=625950,combined_predictions=639950,exclusive_lpt=True,original_evaluation_resources_preserved=True,global_scoring_barrier=True,completed_at_beijing=now())
 atomic_json(run/'cpu_preflight.json',report);print('CPU_PREFLIGHT_PASSED',report,flush=True)
if __name__=='__main__':main()
