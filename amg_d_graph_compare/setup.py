"""Create two D-setting trials without changing historical experiments."""
import argparse,copy,datetime
from .common import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--new-base',type=int,choices=[35,40],required=True);a=ap.parse_args()
 previous=ROOT/'amg_bcd_polarity_oof/runs/bcd_polarity_20261025_014715';old=read(previous/'plan.json');assets=Path(read(ROOT/'amg_d_graph_compare/assets/current.json')['path']);asset_plan=plan(assets)
 require(read(assets/'oof_manifest.json')['complete'] and read(assets/'target_cache_manifest.json')['complete'],'New graph evidence incomplete')
 root=ROOT/'amg_d_graph_compare/runs';root.mkdir(exist_ok=True);run=root/('d_compare_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));run.mkdir()
 saved=next(x for x in read(previous/'D/checkpoints.json') if x['epoch']==40)
 base40=dict(base_epoch=40,path=saved['path'],sha256=saved['sha256']);base35={k:old['base_checkpoint'][k] for k in ['base_epoch','path','sha256']}
 variants=['D_continue','D_newgraph'];bases={'D_continue':base40,'D_newgraph':base40 if a.new_base==40 else base35};epochs={v:list(range(bases[v]['base_epoch']+1,bases[v]['base_epoch']+6)) for v in variants}
 p=copy.deepcopy(old);p.update(schema_version='d_graph_compare_v1',purpose='Continue current D for five additional epochs and compare a new ten-emotion source graph under identical D settings',created_at_beijing=now(),source_previous_run=str(previous),pipeline_run=str(run),training_run=str(run),variants=variants,variant_settings={v:dict(graph_probability=.5,polarity_loss_weight=.1) for v in variants},variant_bases={v:bases[v]['base_epoch'] for v in variants},variant_epochs=epochs,epochs=sorted({e for es in epochs.values() for e in es}),gpu_training_queues={'0':['D_continue'],'1':['D_newgraph']},logical_jobs=30,sample_predictions_total=14000,new_graph_assets=str(assets),same_starting_checkpoint=(a.new_base==40),training_data_iterator='Rebuilt with original seed42; previous checkpoint did not store DataLoader worker states. Both new trials use the same sampler and graph-mask stream.',polarity_method=dict(old['polarity_method'],existing_optimizer='For D40 restore saved polarity head and all three AdamW groups; original35 creates a fresh head after two-group restoration'),selection_policy='Two user-authorized trials; graph query parameters, gate and polarity coefficient frozen before evaluation; all ten weights scored on three datasets')
 p['graph_dropout'].update(variants=variants,inference='Each trial uses its corresponding full source graph and the same compact formatter and confidence gate; no random dropout')
 p.pop('active_variant',None);p.pop('plan_id',None);p['plan_id']=canonical(p);atomic_json(run/'plan.json',p)
 for f in ['original_config.json','train_records.json','train_inputs.json','human_audit_500.json','model_assets_manifest.json','training_execution.json','polarity_labels.json']:(run/f).symlink_to(previous/f)
 for d in ['jobs','predictions','scores','evaluation_jobs','shards']:(run/d).mkdir()
 for variant in variants:
  folder=run/(variant+'_plan');folder.mkdir();vp=copy.deepcopy(p);vp.update(active_variant=variant,base_checkpoint=bases[variant],epochs=epochs[variant],checkpoints=[dict(bases[variant],output=str(run/variant),epochs=epochs[variant])],oof_cache_inventory_path=str(folder/'oof_cache_inventory.json'),oof_verification_path=str(folder/'oof_reuse_verification.json'))
  if variant=='D_newgraph':
   folds={}
   for fold in range(5):
    fm=read(assets/'folds'/str(fold)/'manifest.json');cfg=read(assets/'folds'/str(fold)/'query_config.json');folds[str(fold)]=dict(graph_id=fm['graph_release_id'],query_config_id=canonical(cfg),manifest_sha256=sha(assets/'folds'/str(fold)/'manifest.json'))
   vp.update(graph_release_id=asset_plan['graph_release_id'],query_config_path=str(assets/'query_engine_config.json'),query_config_id=asset_plan['query_config_id'],target_cache=str(assets/'target_cache'),oof_reference_run=str(assets),oof_reference_plan_id=asset_plan['plan_id'],oof_cache=str(assets/'oof_cache'),oof_manifest_sha256=sha(assets/'oof_manifest.json'),oof_assignment_sha256=sha(assets/'fold_assignment.json'),oof_folds=folds,new_graph_path=asset_plan['new_graph_path'],new_target_inventory=str(assets/'target_cache_inventory.json'))
   vp['inputs']=dict(vp['inputs'],query_config_sha256=sha(vp['query_config_path']));vp['oof_policy']=dict(vp['oof_policy'],emotion_ontology='New ten-emotion mapping; each fold excludes held groups',inference_graph='New full ten-emotion source graph')
  vp.pop('plan_id',None);vp['plan_id']=canonical(vp);atomic_json(folder/'plan.json',vp)
  for f in ['original_config.json','train_records.json','train_inputs.json','human_audit_500.json','model_assets_manifest.json','training_execution.json','polarity_labels.json']:(folder/f).symlink_to(run/f)
  (folder/'query_engine_config.json').symlink_to(vp['query_config_path']);(folder/'cache').symlink_to(SOURCE/'cache')
  atomic_json(folder/'cache_manifest.json',dict(complete=True,samples=30755,plan_id=vp['plan_id'],source='Grouped five-fold Graph-OOF, matching this trial graph ontology'))
  for epoch in epochs[variant]:
   for d,spec in p['datasets'].items():
    jid=f'{variant}_epoch_{epoch}_{d}';job=dict(job_id=jid,variant=variant,base_epoch=bases[variant]['base_epoch'],epoch=epoch,dataset=d,samples=spec['samples'],state='pending',attempts=0,plan_id=p['plan_id'],shards=[])
    for lo in range(0,job['samples'],64):
     name=jid+f'_{lo:04d}.json';job['shards'].append(name);atomic_json(run/'shards'/name,dict(job_id=jid,variant=variant,epoch=epoch,dataset=d,dataset_samples=job['samples'],start=lo,stop=min(lo+64,job['samples']),samples=min(64,job['samples']-lo),state='pending',attempts=0))
    atomic_json(run/'jobs'/(jid+'.json'),job);atomic_json(run/'evaluation_jobs'/(jid+'.json'),dict(job_id=jid,state='pending',attempts=0,estimated_seconds={'MER2023':14,'SIMS':22,'OVMERDPlus':19}[d]))
 (run/'README.md').write_text('D_continue: current D checkpoint40, original graph, epochs41–45. D_newgraph: ten-emotion rebuilt graph, start epoch '+str(a.new_base)+', five further epochs. Both keep 50% graph training, polarity coefficient0.1, compact512-token evidence, same confidence gate and five-fold grouped Graph-OOF, raw audio/face/subtitles, batch3,5000steps/epoch,lr1e-5,no gradient checkpointing. Saved D40 polarity head, optimizer and scaler are restored when starting40. Loader rebuilt with original seed42; old checkpoints have no sampler/worker states. GPU0/1 one trainer each; free GPU starts four inference workers, then other GPU joins; global largest-dataset-first exclusive64-sample shards. Ten weights x MER2023/SIMS/OVMERDPlus =30 jobs,14000 predictions. Wait for all inference and GPU release, then one original-metric evaluator on each GPU. All data and results remain on the server.\n')
 atomic_json(root/'current.json',dict(path=str(run),plan_id=p['plan_id']));print(run,flush=True)
if __name__=='__main__':main()
