import subprocess,datetime,copy
from .common import *
def main():
 pkg=GRAPH/'amg_rl_oppo_graph10'
 run=Path(sys.argv[1]) if len(sys.argv)>1 else pkg/'runs'/('official_plus_graph10_'+datetime.datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S'))
 for d in ['inputs','jobs','shards','predictions','workers','scores','logs','official','validation']:(run/d).mkdir(parents=True,exist_ok=True)
 dump(pkg/'preparing.json',dict(run=str(run),state='preparing',time=now()))
 oldrun=Path(read(GRAPH/'amg_base7_graph10/current_run.json')['run']);old=read(oldrun/'plan.json')
 p=dict(schema='rl_oppo_official_plus_graph10_v1',created_at_beijing=now(),run=str(run),prior_run=str(oldrun),prior_datasets=old['datasets'],graph_cache_directory=old['graph_cache_directory'],graph_cache_plan_id=old['graph_cache_plan_id'],graph_release_id=old['graph_release_id'],query_config_id=old['query_config_id'],node_counts=old['node_counts'],graph_policy='D compact+gate; exact prior format_evidence; 512 tokens; frozen graph10',graph_only_change=True,models={},protected_sources={})
 (run/'cache_inventory.json').write_bytes((oldrun/'cache_inventory.json').read_bytes())
 p['cache_inventory_sha256']=sha(run/'cache_inventory.json');dump(run/'plan_draft.json',p)
 procs=[]
 for role in ['rl','oppo']:
  f=(run/'logs'/('preflight_'+role+'.log')).open('wb')
  z=subprocess.Popen([PYTHON,'-u','-B','-m','amg_rl_oppo_graph10.native_'+role,'--run',str(run)],cwd=GRAPH,env=env(),stdout=f,stderr=subprocess.STDOUT);f.close();procs.append((role,z))
 for role,z in procs:
  require(z.wait()==0,'Native preflight failed: '+role+'; see '+str(run/'logs'/('preflight_'+role+'.log')))
 family='mercaptionplus_outputhybird_bestsetup_bestfusion_face_r1stage2_mer25ov1000_continue60_g4_formatbeta00_ovlabel_numrestrict3'
 ckptdir=RL/'output'/family/(family+'_20251009171')
 rlcheckpoints={}
 for f in sorted(ckptdir.glob('checkpoint_*.pth')):
  epoch=int(f.name.split('_')[1]);key='rl_e%03d'%epoch
  rlcheckpoints[key]=dict(id=key,path=str(f),sha256=sha(f),epoch=epoch)
 require({x['epoch'] for x in rlcheckpoints.values()}==set(range(5,61,5)),'Expected 12 released RL checkpoints')
 manifest=read(OPPO/'models/download_manifest_20261028.json')
 released=next(x for x in manifest['models'] if x['name']=='OPPO')
 weights=[dict(path=str(OPPO/'models/OPPO'/x['path']),size=x['size'],sha256=x['hash']) for x in released['files'] if x['path'].endswith('.safetensors')]
 for x in weights:require(Path(x['path']).stat().st_size==x['size'],'OPPO model size mismatch')
 p['models']['rl']=dict(checkpoints=rlcheckpoints,datasets=read(run/'rl_preflight.json')['datasets'],contract=read(run/'rl_preflight.json')['contract'],scoring=dict(OVMERDPlus='AffectGPT-RL/statistic.py calculate_ov_zeroshot',other_eight='original AffectGPT/evaluation.py official MER-UniBench functions; no scorer supplied for these in RL release'))
 p['models']['oppo']=dict(checkpoints={'oppo_release':dict(id='oppo_release',path=str(OPPO/'models/OPPO'),repo=released['repo'],revision=released['revision'],epoch=None,sha256=canonical(weights),weight_manifest=weights)},datasets=read(run/'oppo_preflight.json')['datasets'],contract=read(run/'oppo_preflight.json')['contract'],scoring=dict(source='OPPO/affect_r1/merbench/evaluation.py',answer_selection='full',use_answer_openset=True,skip_llm=False))
 sources=list(pkg.glob('*.py'))+[RL/'inference_hybird.py',RL/'statistic.py',RL/'config.py',RL/'my_affectgpt/conversation/conversation_video.py',RL/'my_affectgpt/models/affectgpt.py',RL/'my_affectgpt/models/affectgpt_r1_noref_ovlabel4.py',RL/'my_affectgpt/evaluation/ew_metric.py',BASE/'evaluation.py',BASE/'config.py',OPPO/'affect_r1/merbench/run_inference.py',OPPO/'affect_r1/merbench/evaluation.py',OPPO/'affect_r1/merbench/submit_merbench_infer.sh',OPPO/'affect_r1/merbench/run_merbench_eval.sh',OPPO/'affect_r1/merbench/result_writer.py',GRAPH/'amg_bcd/policy.py',GRAPH/'amg_finetune_nogc/prompts.py',Path(old['query_config_path']),Path(old['new_graph_path'])/'graph/graph.json',Path(old['new_graph_path'])/'graph/paths_cue_appraisal_emotion.csv']
 sources+=list((RL/'my_affectgpt/datasets/datasets').glob('*.py'))
 sources+=list((OPPO/'affect_r1/merbench/affectgpt_local').glob('*.py'))
 sources+=list((BASE/'my_affectgpt/evaluation').glob('*.py'))+list((BASE/'toolkit/utils').glob('*.py'))
 sources+=list((RL/'my_affectgpt/evaluation').glob('*.py'))+list((RL/'toolkit/utils').glob('*.py'))
 sources+=list((run/'inputs').glob('*.json'))+[run/'rl_original_config.json',run/'rl_preflight.json',run/'oppo_preflight.json',run/'cache_inventory.json',run/'validation/rl_media_equivalence.json']
 p['protected_sources']={str(f):sha(f) for f in sources}
 p['plan_id']=canonical(p);dump(run/'plan.json',p)
 count=0
 for role,model in p['models'].items():
  for cid,spec in model['checkpoints'].items():
   for d,ds in model['datasets'].items():
    jid=cid+'_'+d;shards=[]
    for start in range(0,ds['samples'],32):
     sid=jid+'_%05d'%start;shards.append(sid)
     dump(run/'shards'/(sid+'.json'),dict(id=sid,job_id=jid,role=role,checkpoint=cid,dataset=d,start=start,stop=min(start+32,ds['samples']),state='pending',attempts=0))
    dump(run/'jobs'/(jid+'.json'),dict(id=jid,role=role,checkpoint=cid,dataset=d,samples=ds['samples'],shards=shards,state='pending',score_state='pending'));count+=1
 dump(run/'preparation.json',dict(state='complete',jobs=count,predictions=13*12799,samples_per_checkpoint=12799,rl_checkpoints=12,oppo_checkpoints=1,time=now()))
 (run/'README.md').write_text('Official inference + prior frozen Cue/Appraisal/10-emotion graph, D compact+gate (512-token graph budget). 12 RL checkpoints x 9 datasets plus OPPO release x 9 datasets: 117 jobs / 166387 predictions. Native sample bodies are compiled from each official source; only graph text is appended. RL official generation 1200/2000, OPPO launcher default 1024 tokens. No target-label graph fitting, retraining, subtitle truncation, output filtering, per-sample RNG reseeding, or changed decoding parameters. RL OV evaluation uses its own statistic.py; other eight use original official AffectGPT MER-UniBench evaluator. OPPO uses its own evaluator with full answer and use-answer-openset. Native preprocessing and dataset membership audited. Sample outputs are resumable. Evaluation starts after the node inference workers exit. All files stay on servers.\n')
 dump(pkg/'current_run.json',dict(run=str(run)))
 dump(pkg/'preparing.json',dict(run=str(run),state='complete',time=now()))
 print('PREPARED',run,flush=True)
if __name__=='__main__':main()
