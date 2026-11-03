"""Verify the two frozen D trials, graph provenance, queues and restored-checkpoint contract."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,collections,copy,os,sys
from .common import *
from .verify_oof import verify_oof
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);a=ap.parse_args();run=Path(a.run);p=plan(run);pkg=ROOT/'amg_d_graph_compare';oldrun=Path(p['source_previous_run']);previous=plan(oldrun)
 for f in pkg.glob('*.py'):compile(f.read_text(),str(f),'exec')
 records=read(run/'train_records.json');audit=read(run/'human_audit_500.json');labels=read(run/'polarity_labels.json');ids={r['sample_id'] for r in records}
 require(len(records)==len(ids)==30755 and len(audit)==500 and not ids&{r['sample_id'] for r in audit},'Training/audit split changed')
 require(_graph_hash_matches(run / 'train_records.json', p['inputs']['train_records_sha256'], sha(run / 'train_records.json')) and _graph_hash_matches(run / 'human_audit_500.json', p['inputs']['audit_records_sha256'], sha(run / 'human_audit_500.json')),'Source data changed')
 require(_graph_hash_matches(run / 'polarity_labels.json', p['polarity_labels_sha256'], sha(run / 'polarity_labels.json')) and {r['sample_id'] for r in labels}==ids,'Polarity labels changed')
 require(sum(r['valid_for_polarity_loss'] for r in labels)==30688 and sum(not r['valid_for_polarity_loss'] for r in labels)==67,'Polarity masks changed')
 accepted=read(oldrun/'cpu_preflight.json');require(accepted['passed'],'Previous method not verified')
 for name in ['auxiliary.py','policy.py']:
  require(_graph_hash_matches(pkg / name, sha(ROOT / 'amg_bcd_polarity_oof' / name), sha(pkg / name)),'D loss or formatting changed')
 require(p['training']==previous['training'] and p['policy']==previous['policy'],'D training settings changed')
 report_by_variant={};protected=[]
 for v in p['variants']:
  folder=run/(v+'_plan');vp=plan(folder);base=vp['base_checkpoint'];require(_graph_hash_matches(base['path'], base['sha256'], sha(base['path'])),'Starting checkpoint changed')
  require(vp['epochs']==list(range(base['base_epoch']+1,base['base_epoch']+6)),'Wrong continuation epochs')
  require(vp['variant_settings'][v]==dict(graph_probability=.5,polarity_loss_weight=.1),'Wrong D settings')
  require(_graph_hash_matches(folder / 'query_engine_config.json', vp['inputs']['query_config_sha256'], sha(folder / 'query_engine_config.json')),'Query file changed')
  oldcfg=read(previous['query_config_path']);cfg=read(vp['query_config_path']);restored=dict(cfg);restored['graph_release_id']=oldcfg['graph_release_id'];require(restored==oldcfg,'Query parameters changed')
  if v=='D_continue':
   prior=read(oldrun/'oof_reuse_verification.json');require(prior['passed'] and _graph_hash_matches(oldrun / 'oof_cache_inventory.json', prior['inventory_sha256'], sha(oldrun / 'oof_cache_inventory.json')),'Accepted OOF inventory changed')
   for f,digest in prior['files_sha256'].items():require(_graph_hash_matches(f, digest, sha(f)),'Accepted fold resource changed')
   for name in ['oof_cache_inventory.json','oof_reuse_verification.json']:(folder/name).symlink_to(oldrun/name)
   report_by_variant[v]=dict(passed=True,samples=30755,accepted_verification_reused=True,accepted_verification_sha256=sha(oldrun/'oof_reuse_verification.json'))
  else:
   report_by_variant[v]=verify_oof(folder,vp)
   newref=Path(vp['oof_reference_run']);oldref=Path(previous['oof_reference_run']);require(read(newref/'fold_assignment.json')['assignments']==read(oldref/'fold_assignment.json')['assignments'],'Graph-only comparison uses different folds')
   for fold in range(5):
    n=read(newref/'folds'/str(fold)/'graph.json');o=read(oldref/'folds'/str(fold)/'graph.json');ca=lambda g:{(e['source_node_id'],e['target_node_id']):(e['edge_weight'],e['support_count_groups']) for e in g['statistical_edges'] if e['relation_type']=='CUE_TO_APPRAISAL_STATE'}
    require(ca(n)==ca(o),'Unchanged Cue/Appraisal fold statistics differ')
    require(len([x for x in n['nodes'] if x['node_type']=='EmotionConcept'])==10,'New graph fold ontology differs')
   newg=Path(vp['new_graph_path']);audit_report=read(newg/'manifest/complete_audit.json');require(audit_report['passed'] and audit_report['release_id']==vp['graph_release_id'],'New full graph audit failed')
   for f,digest in audit_report['report_sha256'].items():require(_graph_hash_matches(ROOT / f, digest, sha(ROOT / f)),'New graph audit resource changed')
   assets=Path(p['new_graph_assets']);tm=read(assets/'target_cache_manifest.json');inventory=read(assets/'target_cache_inventory.json');require(tm['complete'] and tm['samples']==len(inventory)==1400 and _graph_hash_matches(assets / 'target_cache_inventory.json', tm['inventory_sha256'], sha(assets / 'target_cache_inventory.json')),'New target cache incomplete')
   for d,spec in p['datasets'].items():
    for row in read(spec['path']):
     x=read(target_cache(vp,row['sample_id']));require(x['cache_id']==canonical({k:z for k,z in x.items() if k!='cache_id'})==inventory[row['sample_id']],'New target record changed')
     require(x['evidence']['graph_release_id']==vp['graph_release_id'] and x['evidence']['query_config_id']==vp['query_config_id'],'New target graph mismatch')
   protected += [assets/'target_cache_manifest.json',assets/'target_cache_inventory.json',newg/'manifest/complete_audit.json',newg/'manifest/protocol.json',newg/'graph/graph.json',newg/'graph/paths_cue_appraisal_emotion.csv']
  protected += [folder/'oof_cache_inventory.json',folder/'oof_reuse_verification.json',folder/'plan.json',folder/'query_engine_config.json']
 for d,spec in p['datasets'].items():require(_graph_hash_matches(spec['path'], spec['sha256'], sha(spec['path'])) and len(read(spec['path']))==spec['samples'],'Target data changed')
 for filename,binding in read(run/'model_assets_manifest.json')['assets'].items():
  st=Path(filename).stat();require(st.st_size==binding['bytes'] and st.st_mtime_ns==binding['mtime_ns'],'Model assets changed')
 import torch
 for v in p['variants']:
  vp=plan(run/(v+'_plan'));ck=torch.load(_graph_resolve_path(vp['base_checkpoint']['path']), map_location='cpu', weights_only=True);require(ck['epoch']==vp['base_checkpoint']['base_epoch'],'Checkpoint epoch mismatch')
  sizes=[len(g['params']) for g in ck['optimizer']['param_groups']]
  if ck['epoch']==40:require(sizes==[402,10,2] and set(ck['polarity_head'])=={'weight','bias'} and ck['amg_finetune']['plan_id']==plan(oldrun/'D_plan')['plan_id'],'Current D40 state missing')
  else:require(sizes==[402,10],'Original35 optimizer differs')
  del ck
 # Same graph mask stream for both trials; no new dropout or loss setting.
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/'AffectGPT'))
 from .dataset import graph_enabled
 masks={v:[graph_enabled(r['sample_id'],1,v) for r in records] for v in p['variants']};require(masks[p['variants'][0]]==masks[p['variants'][1]],'Paired masks differ');fraction=sum(masks[p['variants'][0]])/30755;require(.49<fraction<.51,'Graph keep rate changed')
 from my_affectgpt.models.tokenizer import load_tokenizer_from_LLM
 from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
 from .policy import make_tokens
 t=load_tokenizer_from_LLM('Qwen25');reader=BaseDataset.__new__(BaseDataset);reader.tokenizer=t;reader.dataset='MERCaptionPlus';reader.face_or_frame='multiface_audio_face_text';cfg=read(run/'original_config.json')['model']
 for key in ['num_audio_query_token','num_video_query_token','num_multi_query_token','num_image_query_token']:setattr(reader,key,cfg[key])
 for attr,marker in [('IMAGE_PATCH_TOKEN_ID','<ImageHere>'),('AUDIO_PATCH_TOKEN_ID','<AudioHere>'),('FRAME_PATCH_TOKEN_ID','<FrameHere>'),('FACE_PATCH_TOKEN_ID','<FaceHere>'),('MULTI_PATCH_TOKEN_ID','<MultiHere>')]:setattr(reader,attr,t.get_vocab()[marker])
 selected={r['sample_id']:r for r in records[::640]}
 for key,n in [('description',24),('subtitle',16)]:
  for r in sorted(records,key=lambda r:len(r[key]),reverse=True)[:n]:selected[r['sample_id']]=r
 maximum=0;checked=0
 for v in p['variants']:
  vp=plan(run/(v+'_plan'))
  for row in selected.values():
   ev=read(Path(vp['oof_cache'])/(row['sample_id']+'.json'))['evidence']
   for keep in [True,False]:
    for task in ['description','ovlabel']:
     prompt,answer,text,info=make_tokens(reader,row,ev,task,p['training'],v,None if keep else 0.0);length=len(prompt)+len(answer)+2;maximum=max(maximum,length);checked+=1
     require(length<=1398 and info['graph_tokens']<=512 and (keep or info['graph_tokens']==0),'Prompt memory/dropout limit changed')
     for marker,count in zip(['<ImageHere>','<AudioHere>','<FrameHere>','<FaceHere>','<MultiHere>'],[0,1,0,1,1]):require(text.count(marker)==count,'Raw modality missing')
 require(len(jobs(run))==30 and len(list((run/'shards').glob('*.json')))==240 and sum(j['samples'] for j in jobs(run))==14000,'Wrong prediction budget')
 # Verify that real shard selection locks exclusive jobs and prioritizes largest dataset.
 from .infer_worker import choose
 fixture=run/'claim_fixture';fixture.mkdir();(fixture/'shards').mkdir();variant=p['variants'][0];(fixture/variant).mkdir();atomic_json(fixture/variant/'checkpoints.json',[dict(epoch=41,path='fixture',sha256='fixture')])
 for i,n in enumerate([411,532,457]):atomic_json(fixture/'shards'/f'{i}.json',dict(variant=variant,epoch=41,dataset_samples=n,samples=64,state='pending',attempts=0))
 first=choose(fixture,p);second=choose(fixture,p);require(first[2]['dataset_samples']==532 and second[2]['dataset_samples']==457,'Exclusive/LPT scheduling failed');first[1].close();second[1].close()
 require(complete_count(run)==0 and not (run/'evaluation_barrier.json').exists(),'Scoring started before inference')
 resources=read(oldrun/'evaluation_resources.json')
 for f,digest in resources['files'].items():require(_graph_hash_matches(f, digest, sha(f)),'Original metrics changed')
 atomic_json(run/'evaluation_resources.json',resources)
 paths=list(pkg.glob('*.py'))
 for folder in ['amg_finetune_nogc','amg_runtime','amg_inference','amg_graph10_rebuild']:paths+=list((ROOT/folder).glob('*.py'))
 paths+=protected+[run/'plan.json',ROOT/'AffectGPT/my_affectgpt/models/affectgpt.py',ROOT/'AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py']
 manifest=dict(files={str(f.relative_to(ROOT)):sha(f) for f in paths},created_at_beijing=now());atomic_json(run/'code_manifest.json',manifest)
 for v in p['variants']:(run/(v+'_plan')/'code_manifest.json').symlink_to(run/'code_manifest.json')
 report=dict(passed=True,cpu_only=True,variants=report_by_variant,graph_keep_fraction_first_visit=fraction,paired_graph_masks=True,starting_weights_and_optimizer_contract_valid=True,all_D_settings_preserved=True,new_graph_and_folds_audited=True,maximum_checked_sequence_tokens=maximum,prompt_tasks_checked=checked,raw_modalities_preserved=True,logical_jobs=30,shards=240,predictions=14000,lpt_exclusive_claim=True,global_scoring_barrier=True,completed_at_beijing=now())
 atomic_json(run/'cpu_preflight.json',report);print(report,flush=True)
if __name__=='__main__':main()
