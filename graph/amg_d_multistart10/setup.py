"""Four original-checkpoint ten-epoch D trials plus nine-dataset completion of original35."""
from graph_paths import hash_matches as _graph_hash_matches
import copy,datetime
from .common import *
def main():
 root=ROOT/'amg_d_multistart10/runs';root.mkdir(exist_ok=True);run=root/('d_multistart10_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));run.mkdir()
 previous=ROOT/'amg_bcd_polarity_oof/runs/bcd_polarity_20261025_014715';continuation=ROOT/'amg_d_graph_compare/runs/d_compare_20261025_111800';old=read(previous/'plan.json');ip=read(OLD_INFER/'plan.json');source=read(SOURCE/'plan.json')
 variants=[f'from_{b}' for b in [30,35,40,45,50]];new_variants=[v for v in variants if v!='from_35'];bases={f'from_{b}':b for b in [30,35,40,45,50]};epochs={v:list(range(b+1,b+11)) for v,b in bases.items()};starts={v:copy.deepcopy(next(x for x in source['checkpoints'] if x['base_epoch']==b)) for v,b in bases.items()}
 for v,spec in starts.items():spec.update(initialization='original_checkpoint',epochs=epochs[v],output=str(run/v))
 reuse35=[];reuse_sources={}
 for oldrun,variant,metadata_base in [(previous,'D',35),(continuation,'D_continue',40)]:
  oldp=read(oldrun/(variant+'_plan')/'plan.json')
  for ck in read(oldrun/variant/'checkpoints.json'):
   x=dict(ck,training_plan_id=oldp['plan_id'],continuation_base_epoch=metadata_base,original_base_epoch=35,reused=True,source_run=str(oldrun),source_variant=variant);reuse35.append(x);reuse_sources[ck['epoch']]=(oldrun,variant)
 require(sorted(x['epoch'] for x in reuse35)==list(range(36,46)),'Original35 reuse incomplete')
 p=copy.deepcopy(old);p.update(schema_version='d_multistart10_nine_dataset_v1',created_at_beijing=now(),purpose='Four original starts30/40/45/50 independently continue ten epochs using original graph and fixed current D settings; reuse original35 ten weights and three-dataset scores, add six remaining datasets',pipeline_run=str(run),training_run=str(run),source_previous_run=str(previous),reuse35_continuation_run=str(continuation),variants=variants,new_training_variants=new_variants,variant_bases=bases,variant_epochs=epochs,epochs=sorted({e for es in epochs.values() for e in es}),variant_settings={v:dict(graph_probability=.5,polarity_loss_weight=.1) for v in variants},gpu_training_queues={'0':['from_30','from_45'],'1':['from_40','from_50']},datasets=ip['datasets'],logical_jobs=450,new_inference_jobs=420,reused_inference_jobs=30,new_training_weights=40,reused_training_weights=10,checkpoint_count=50,dataset_samples_total=12799,sample_predictions_total=639950,new_sample_predictions=625950,reused_sample_predictions=14000,user_authorized_all_saved_epochs_target_evaluation=True,selection_policy='Fixed D settings, original graph and frozen source-selected query parameters; all50 user-requested weights tested on all9 datasets, no target-driven tuning',training_data_iterator='Four new trials run ten continuous epochs with original seed42. Reused35 ran five plus five with loader reconstructed at41; this distinction is retained.',inference_schedule='Each GPU finishes its two ten-epoch trainers before four-lane inference; shared largest-dataset-first exclusive64-sample shards, including all already-available35 weights; all450 inference jobs including30 reused must complete before one original judge perGPU',reuse35_weights=reuse35)
 p['training']=dict(old['training'],additional_epochs=10,supervision='Original MERCaptionPlus hybird(description/ovlabel),50/50 random tasks; auxiliary polarity lambda0.1 for every valid source example, with and without graph');p['limits']=copy.deepcopy(p['training']);p['graph_dropout']=dict(old['graph_dropout'],variants=variants)
 p['oof_policy']=copy.deepcopy(old['oof_policy']);p['polarity_method']=dict(old['polarity_method'],existing_optimizer='Restore each original two-group AdamW and AMP state, add the same deterministic fresh three-class polarity head in a third group')
 p.pop('active_variant',None);p.pop('plan_id',None);p['plan_id']=canonical(p);atomic_json(run/'plan.json',p)
 for name in ['original_config.json','train_records.json','train_inputs.json','human_audit_500.json','model_assets_manifest.json','training_execution.json','polarity_labels.json','query_engine_config.json']:(run/name).symlink_to(previous/name)
 for name in ['oof_cache_inventory.json','oof_reuse_verification.json']:(run/name).symlink_to(previous/name)
 for d in ['jobs','shards','predictions','scores','evaluation_jobs']:(run/d).mkdir()
 (run/'from_35').mkdir();atomic_json(run/'from_35/checkpoints.json',sorted(reuse35,key=lambda x:x['epoch']))
 for v in variants:
  folder=run/(v+'_plan');folder.mkdir();vp=copy.deepcopy(p);vp.update(active_variant=v,epochs=epochs[v],base_checkpoint=starts[v],checkpoints=[starts[v]],oof_cache_inventory_path=str(run/'oof_cache_inventory.json'),oof_verification_path=str(run/'oof_reuse_verification.json'))
  vp.pop('plan_id',None);vp['plan_id']=canonical(vp);atomic_json(folder/'plan.json',vp)
  for name in ['original_config.json','train_records.json','train_inputs.json','human_audit_500.json','model_assets_manifest.json','training_execution.json','polarity_labels.json','query_engine_config.json','oof_cache_inventory.json','oof_reuse_verification.json']:(folder/name).symlink_to(run/name)
  (folder/'cache').symlink_to(SOURCE/'cache');atomic_json(folder/'cache_manifest.json',dict(complete=True,samples=30755,plan_id=vp['plan_id'],source='Accepted original grouped Graph-OOF cache, fixed D formatter and gate'))
 reused={};job_count=0;new_predictions=0;reused_predictions=0
 for v in variants:
  for epoch in epochs[v]:
   for d,ds in p['datasets'].items():
    jid=f'{v}_epoch_{epoch}_{d}';job=dict(job_id=jid,variant=v,base_epoch=bases[v],epoch=epoch,dataset=d,samples=ds['samples'],state='pending',attempts=0,plan_id=p['plan_id'],shards=[])
    if v=='from_35' and d in ['MER2023','SIMS','OVMERDPlus']:
     oldrun,ov=reuse_sources[epoch];source_jid=f'{ov}_epoch_{epoch}_{d}';jobfile=oldrun/'jobs'/(source_jid+'.json');scorefile=oldrun/'scores'/(source_jid+'.json');oj=read(jobfile);oscore=read(scorefile);ck=next(x for x in reuse35 if x['epoch']==epoch)
     require(oj['state']=='complete' and oj['checkpoint']['sha256']==ck['sha256']==oscore['checkpoint']['sha256'],'Stale original35 result')
     require(_graph_hash_matches(oscore['raw_path'], oscore['raw_sha256'], sha(oscore['raw_path'])),'Reused raw predictions changed')
     job.update(state='complete',checkpoint=ck,prediction_path=oj['prediction_path'],official_npz=oj['official_npz'],finished_at_beijing=oj['finished_at_beijing'],reused=True,source_job_path=str(jobfile),source_job_sha256=sha(jobfile))
     result=copy.deepcopy(oscore);result.update(job_id=jid,variant=v,base_epoch=35,plan_id=p['plan_id'],reused=True,source_score_path=str(scorefile),source_score_sha256=sha(scorefile),source_plan_id=oscore['plan_id'],source_job_id=source_jid);atomic_json(run/'scores'/(jid+'.json'),result)
     reused[jid]=dict(job_path=str(jobfile),job_sha256=sha(jobfile),score_path=str(scorefile),score_sha256=sha(scorefile),raw_path=oscore['raw_path'],raw_sha256=oscore['raw_sha256'],checkpoint_sha256=ck['sha256']);reused_predictions+=ds['samples']
    else:
     for lo in range(0,ds['samples'],64):
      name=jid+f'_{lo:04d}.json';job['shards'].append(name);atomic_json(run/'shards'/name,dict(job_id=jid,variant=v,epoch=epoch,dataset=d,dataset_samples=ds['samples'],start=lo,stop=min(lo+64,ds['samples']),samples=min(64,ds['samples']-lo),state='pending',attempts=0))
     new_predictions+=ds['samples']
    atomic_json(run/'jobs'/(jid+'.json'),job);atomic_json(run/'evaluation_jobs'/(jid+'.json'),dict(job_id=jid,state='complete' if job['state']=='complete' else 'pending',attempts=0,estimated_seconds={'MER2023':14,'MER2024':35,'MELD':80,'IEMOCAPFour':40,'CMUMOSI':30,'CMUMOSEI':190,'SIMS':22,'SIMSv2':45,'OVMERDPlus':19}[d]));job_count+=1
 atomic_json(run/'reuse_manifest.json',dict(weights=reuse35,scores=reused,reused_jobs=30,reused_predictions=reused_predictions,source_runs=[str(previous),str(continuation)]))
 require(job_count==450 and len(reused)==30 and new_predictions==625950 and reused_predictions==14000,'Wrong new/reuse budget')
 (run/'README.md').write_text('Original graph plus current D:50% attempted graph presentations,lambda0.1 polarity,compact512-token evidence,confidence gate,grouped5-foldGraphOOF,raw audio/face/subtitle,batch3,5000steps/epoch,lr1e-5,noGC. Four originals30/40/45/50 train ten continuous epochs each:40 new weights. Original35 ten weights36–45 reused with exact per-weight source plan and continuation base; already-scored three datasets30 jobs reused with provenance, add six datasets60 jobs. Nine targets MER2023/MER2024/MELD/IEMOCAPFour/CMUMOSI/CMUMOSEI/SIMS/SIMSv2/OVMERDPlus. New inference420 jobs625950 predictions; combined450 jobs639950 predictions. GPU0 trains30 then45;GPU1 trains40 then50. Free card after its queue starts four inference workers; shared64-sample largest-dataset-first shards. All inference completes and exits before dual judges,one perGPU. Native HIT/WAF/F_s routes and frozen original evaluator resources. No local files.\n')
 atomic_json(root/'current.json',dict(path=str(run),plan_id=p['plan_id']));print(run,flush=True)
if __name__=='__main__':main()
