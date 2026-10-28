import argparse,copy,csv,os,traceback
from pathlib import Path
from .common import *
from amg_runtime.engine import GraphQueryEngine
from amg_finetune_nogc.common import bound_query
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);a=ap.parse_args();run=Path(a.run);p=plan(run)
 inputs=read(Path(p['runtime_path'])/'inputs_p0.json');policy=read(Path(p['runtime_path'])/'cue_policy.json');g=Path(p['new_graph_path']);cfg=read(p['query_config_path'])
 inputs['graph'].update(release_id=p['graph_release_id'],graph_file=str(g/'graph/graph.json'),path_file=str(g/'graph/paths_cue_appraisal_emotion.csv'))
 with (g/'graph/paths_cue_appraisal_emotion.csv').open() as f:paths=list(csv.DictReader(f))
 engine=GraphQueryEngine(read(g/'graph/graph.json'),paths,inputs,policy,cfg,p['runtime_release_id'])
 atomic_json(run/'inputs_full_graph.json',inputs);inventory={};count=0
 for d,spec in p['datasets'].items():
  for row in read(spec['path']):
   old=read(OLD_INFER/'cache'/(sid_key(row['sample_id'])+'.json'));require(old['cache_id']==canonical({k:v for k,v in old.items() if k!='cache_id'}),'Old target cache corrupt')
   cue=copy.deepcopy(old['cue']);cue['graph_release_id']=p['graph_release_id'];cue['query_input_id']=canonical({k:v for k,v in cue.items() if k!='query_input_id'})
   ev=bound_query(engine.query(cue),engine)
   x=dict(sample_id=row['sample_id'],source_cache_id=old['cache_id'],cue=cue,evidence=ev,input_record_id=canonical({k:row[k] for k in ['sample_id','text','audio_path','video_path']}),graph_release_id=p['graph_release_id']);x['cache_id']=canonical(x)
   atomic_json(Path(p['target_cache'])/(sid_key(row['sample_id'])+'.json'),x);inventory[row['sample_id']]=x['cache_id'];count+=1
   if count%100==0:print('TARGET_CACHE',count,flush=True)
 atomic_json(run/'target_cache_inventory.json',inventory)
 atomic_json(run/'target_cache_manifest.json',dict(complete=True,samples=count,graph_release_id=p['graph_release_id'],query_config_id=p['query_config_id'],inventory_sha256=sha(run/'target_cache_inventory.json'),original_frozen_cues_reused=True,no_target_annotations_used=True))
 print('TARGET_COMPLETE',count,flush=True)
if __name__=='__main__':main()
