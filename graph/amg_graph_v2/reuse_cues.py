"""Import original frozen Student scores; explicitly NOT OOF, never retrain Student."""
import csv,json,shutil
import numpy as np
from .common import *
def main():
 from amg_runtime.common import canonical
 info=read(ROOT/'data/prepared.json');rows=read(ROOT/'data/input_rows.json')
 runtime=GRAPH/'amg_runtime/releases/p2p3_20261022_111315';inputs=read(runtime/'inputs_p0.json');exports=read(runtime/'weight_exports.json')['exports']
 cache=GRAPH/'amg_finetune/runs/graph_continue_20261022_123029/cache'
 q=np.zeros((len(rows),42),np.float32);av=np.zeros_like(q,bool);checks=[]
 for i,row in enumerate(rows):
  f=cache/(row['sample_id']+'.json');raw=f.read_bytes();rec=json.loads(raw);a=rec['cue']
  assert rec['sample_id']==a['sample_id']==row['sample_id']
  assert canonical({k:v for k,v in rec.items() if k!='cache_id'})==rec['cache_id'],'Cache content digest mismatch'
  assert canonical({k:v for k,v in a.items() if k!='query_input_id'})==a['query_input_id'],'Cue payload changed'
  assert a['cue_id_order']==info['cue_ids'];assert a['runtime_release_id']==read(runtime/'release_manifest.json')['release_id'];assert a['cue_release_id']==info['cue_release_id']
  for m in ['text','audio','visual']:
   assert a['model_versions'][m]['checkpoint_sha256']==inputs['checkpoints'][m]['sha256']
   assert a['model_versions'][m]['inference_weights_sha256']==exports[m]['sha256']
  assert a['input_fingerprints']['text']['text_sha256']==canonical({k:row.get('text',{}).get(k) or '' for k in ['chinese','english']})
  for m in ['audio','visual']:
   fprint=a['input_fingerprints'][m];asset=row['media_assets'][m]
   assert fprint['sha256']==asset['sha256'];assert fprint['bytes']==asset['bytes']
  av[i]=a['availability_mask']
  for j,s in enumerate(a['scores']):
   if av[i,j]:assert s is not None and np.isfinite(s) and 0<=s<=1;q[i,j]=s
   else:assert s is None
  checks.append(dict(sample_id=row['sample_id'],cache_sha256=__import__('hashlib').sha256(raw).hexdigest(),cache_id=rec['cache_id'],query_input_id=a['query_input_id'],role=row['role'],student_exposure='in_sample_training_prediction' if row['role']=='pseudo_train' else 'historical_student_validation_and_selection'))
  if i%5000==0:event('cache_verified',done=i,total=len(rows))
 save(ROOT/'data/cue_scores.npz',scores=q,available=av,sample_ids=np.array([r['sample_id'] for r in rows]))
 write(ROOT/'data/cache_verification.json',dict(passed=True,rows=len(rows),source=str(cache),student_retrained=False,oof=False,manifest_digest=digest(checks),checkpoints={m:inputs['checkpoints'][m]['sha256'] for m in ['text','audio','visual']},inference_weights={m:exports[m]['sha256'] for m in ['text','audio','visual']},available_per_cue=av.sum(0).tolist(),checks='All sample IDs, cache and Cue content digests, ontology order, checkpoint IDs, inference weight IDs, raw text and media SHA256 match frozen source release. Current raw media not reread.'))
 with (ROOT/'data/cache_inventory.jsonl').open('w') as f:
  for c in checks:f.write(json.dumps(c,ensure_ascii=False)+'\n')
 with (ROOT/'data/exposure_ledger.csv').open() as f:ledger=list(csv.DictReader(f))
 for row in ledger:
  if row['original_role']=='pseudo_train':row.update(v2_role='relation_train_reused_student_scores',history='Old Student fitted on this source sample; reused score is not OOF',allowed_use='Graph relation fitting only; no Cue Student training')
  elif row['original_role']=='pseudo_validation':row.update(history='Historical Student validation/model selection and AffectGPT continuation exposure; internal relation evaluation only')
 with (ROOT/'data/exposure_ledger.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
 info.update(student_retrained=False,cue_prediction_oof=False,fold_semantics='Five fixed source-group folds for graph relation cross-fitting and edge stability only. They are NOT Student OOF folds.',user_scope_override='User explicitly requested reusing existing Cue extractor and graph reconstruction only. Document Student OOF retraining is excluded.',validation_limitation='Internal source evaluation only: Student training predictions in relation training; historical development was exposed to Student selection and AffectGPT continuation. No strict independent or OOF generalization claim.')
 info['files_sha256']={f.name:sha(f) for f in (ROOT/'data').iterdir() if f.is_file() and f.name!='prepared.json'}
 write(ROOT/'data/prepared.json',info)
 snap=ROOT/'source_snapshot';snap.mkdir(exist_ok=True)
 shutil.copy2(PROJECT/'图构建.md',snap/'图构建.md')
 for m in ['text','audio','visual']:shutil.copy2(GRAPH/f'cue_annotation/protocols/qwen_omni_api/{m}.txt',snap/f'cue_definitions_{m}.txt')
 write(ROOT/'data/student_binding.json',dict(runtime_path=str(runtime),runtime_release_id=read(runtime/'release_manifest.json')['release_id'],cue_release_id=info['cue_release_id'],cue_ids=info['cue_ids'],checkpoints=inputs['checkpoints'],exports={m:{k:exports[m][k] for k in ['path','sha256','config']} for m in exports},unchanged=True,retrained=False,source_cache=str(cache)))
 cn=read(ROOT/'ontology/cue_nodes.json')
 for n in cn:n.update(definition_source=str(snap/f"cue_definitions_{n['modality']}.txt"),positive_rule='Clear observable presence under frozen cue definition',negative_rule='Adequate coverage and no qualifying instance',uncertain_rule='Ambiguous evidence; supervision mask=0',unobservable_rule='Insufficient input/coverage; supervision mask=0')
 write(ROOT/'ontology/cue_nodes.json',cn);event('old_student_reused',rows=len(rows),retrained=False,oof=False)
if __name__=='__main__':main()
