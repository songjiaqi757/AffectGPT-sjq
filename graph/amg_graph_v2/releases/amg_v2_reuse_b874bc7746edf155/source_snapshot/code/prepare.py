"""Freeze source-only data, masks, exact-media groups, folds and exposure ledger."""
import collections,csv,json,sys
import numpy as np
from .common import *

def main():
 out=ROOT/'data';out.mkdir(exist_ok=True)
 if (out/'prepared.json').exists():
  event('data_already_prepared');return
 from cue_student.data import Release
 pointer=read(GRAPH/'cue_student/artifacts/current_release.json');r=Release(pointer['path'])
 rows=[x for x in r.rows if x['role'] in ('pseudo_train','pseudo_validation')]
 assert len(rows)==30755
 ri={x['sample_id']:i for i,x in enumerate(r.rows)};ids=[x['sample_id'] for x in rows]
 pos=[ri[x] for x in ids];cy=r.targets[pos].astype(np.float32);cm=r.mask[pos].astype(bool)
 app=GRAPH/'appraisal_annotation/runs/mercaptionplus_v2_4';ont=read(app/'ontology.json')
 dims=list(ont['dimensions']);states=sum(ont['dimensions'].values(),[])
 state_dim=[dims.index(d) for d in dims for _ in ont['dimensions'][d]]
 ay=np.full((len(rows),6),-1,np.int64);am=np.zeros((len(rows),6),bool)
 h=__import__('hashlib').sha256()
 for i,row in enumerate(rows):
  f=app/'annotations'/(row['sample_id']+'.json');raw=f.read_bytes();rec=json.loads(raw)
  assert rec['sample_id']==row['sample_id'];assert rec['versions']['prompt_version']=='appraisal_teacher_v2.4'
  h.update(row['sample_id'].encode());h.update(__import__('hashlib').sha256(raw).digest())
  items=rec['annotation']['dimensions'];assert len(items)==6
  for a in items:
   d=dims.index(a['dimension_id']);am[i,d]=a['valid']
   if a['valid']:
    assert a['state'] in ont['dimensions'][dims[d]]
    ay[i,d]=ont['dimensions'][dims[d]].index(a['state'])
  if i%5000==0:event('appraisal_labels',done=i,total=len(rows))
 er=GRAPH/'emotion_nodes/runs'/read(GRAPH/'emotion_nodes/runs/current.json')['run_id']
 en=read(er/'nodes.json');names=[n['canonical_name'] for n in en];eid=[n['id'] for n in en]
 ey=np.zeros((len(rows),188),np.float32);em=np.zeros_like(ey,bool);idx={s:i for i,s in enumerate(ids)};seen=set();ec=collections.Counter()
 with (er/'labels.jsonl').open() as f:
  for line in f:
   a=json.loads(line)
   if a['sample_id'] not in idx:continue
   i=idx[a['sample_id']];seen.add(a['sample_id']);assert a['data_role']==rows[i]['role']
   for name in a['canonical_labels']:
    if name in names:ey[i,names.index(name)]=1;em[i,names.index(name)]=True
   complete=bool(a['canonical_labels']) and not a['oov_canonical_labels'] and not a['dropped_terms']
   if complete:em[i,:]=True;ec['complete_mapping_closed_world']+=1
   else:ec['partial_or_unmapped_positive_only']+=1
 assert seen==set(ids)
 parent=list(range(len(rows)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:parent[max(a,b)]=min(a,b)
 keys={}
 for i,row in enumerate(rows):
  kk=['group:'+row['group_id']]+[m+':'+a['sha256'] for m,a in row.get('media_assets',{}).items()]
  for k in kk:
   if k in keys:union(i,keys[k])
   else:keys[k]=i
 groups=[ids[find(i)] for i in range(len(rows))]
 tr=np.array([x['role']=='pseudo_train' for x in rows]);dev=~tr
 assert not(set(np.array(groups)[tr])&set(np.array(groups)[dev])),'Exact media duplicate crosses historical roles; fail closed'
 unique=sorted(set(np.array(groups)[tr]),key=lambda x:digest([20261103,x]));assignment={g:k%5 for k,g in enumerate(unique)}
 folds=np.array([assignment[g] if t else -1 for g,t in zip(groups,tr)],np.int64)
 devgroups=sorted(set(np.array(groups)[dev]),key=lambda g:digest(['v2_internal_development_split',g]))
 tune_groups=set(devgroups[::2]);tune=np.array([not t and g in tune_groups for g,t in zip(groups,tr)]);evaluation=dev&~tune
 cues=sum([r.ontology['cue_ids'][m] for m in ['text','audio','visual']],[])
 write(out/'input_rows.json',rows)
 save(out/'labels.npz',cue_y=cy,cue_mask=cm,app_y=ay,app_mask=am,emotion_y=ey,emotion_mask=em,train=tr,tune=tune,evaluation=evaluation,fold=folds,sample_ids=np.array(ids),groups=np.array(groups))
 ontology=ROOT/'ontology';ontology.mkdir(exist_ok=True)
 write(ontology/'cue_nodes.json',[dict(cue_id=c,node_type='CueType',modality=m,ontology_version=r.manifest['release_id'],definition_source=str(GRAPH/'cue_annotation/protocols')) for m in ['text','audio','visual'] for c in r.ontology['cue_ids'][m]])
 write(ontology/'appraisal_dimensions.json',[dict(id=d,node_type='AppraisalDimension',states=ont['dimensions'][d],definition=ont.get('definitions',{}).get(d),valid_training_samples=int(am[tr,j].sum())) for j,d in enumerate(dims)])
 write(ontology/'appraisal_states.json',[dict(id=s,node_type='AppraisalState',dimension_id=d) for d in dims for s in ont['dimensions'][d]])
 write(ontology/'emotion_nodes.json',en)
 write(ontology/'emotion_family_mapping.json',dict(enabled=False,reason='No audited strict family mapping; preserve 188 concepts'))
 with (out/'exposure_ledger.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['sample_id','original_role','v2_role','group_id','fold','history','allowed_use']);w.writeheader()
  for i,row in enumerate(rows):w.writerow(dict(sample_id=ids[i],original_role=row['role'],v2_role='relation_train_oof' if tr[i] else 'development_tune' if tune[i] else 'internal_heldout_evaluation',group_id=groups[i],fold=int(folds[i]),history='Historical source training/development; not a fresh independent confirmation',allowed_use='OOF Student and relations' if tr[i] else 'Calibration and policy selection' if tune[i] else 'Frozen policy internal evaluation only'))
  for row in r.rows:
   if row['role'] not in ('pseudo_train','pseudo_validation'):w.writerow(dict(sample_id=row['sample_id'],original_role=row['role'],v2_role='untouched_reserved',group_id=row['group_id'],fold=-1,history='Reserved; no raw labels or media read by v2',allowed_use='none'))
 info=dict(protocol_version='amg_v2_20261103',cue_release_id=r.manifest['release_id'],cue_ids=cues,dimensions=dims,states=states,state_dim=state_dim,emotion_ids=eid,emotion_names=names,emotion_mask_policy='Only fully mapped nonempty source label sets receive explicit protocol-authorized closed-world negatives. Partial/OOV/dropped/empty sets retain mapped positives; all other cells masked.',emotion_mask_counts=dict(ec),source_plan=str(PROJECT/'图构建.md'),source_plan_sha256=sha(PROJECT/'图构建.md'),source_files={str(f):sha(f) for f in [Path(r.path)/'manifest.json',Path(r.path)/'members.json',Path(r.path)/'labels.npz',er/'nodes.json',er/'labels.jsonl',app/'ontology.json']},appraisal_annotation_ordered_sha256=h.hexdigest(),counts=dict(train=int(tr.sum()),tune=int(tune.sum()),internal_evaluation=int(evaluation.sum()),gold_reserved=300,diagnostic_reserved=200),fold_counts=[int((folds==k).sum()) for k in range(5)],group_limitations='Manifest provenance mostly unknown; union exact audio/video SHA256 and supplied group IDs. Near duplicates and original-source independence not fully verified.',independent_confirmation=False)
 write(out/'split_manifest.json',dict(sample_ids=ids,groups=groups,folds=folds.tolist(),train_ids=np.array(ids)[tr].tolist(),tune_ids=np.array(ids)[tune].tolist(),evaluation_ids=np.array(ids)[evaluation].tolist()))
 write(out/'label_manifest.json',dict(appraisal_valid_by_dimension=am[tr].sum(0).tolist(),emotion_positive=ey[tr].sum(0).astype(int).tolist(),emotion_valid=em[tr].sum(0).tolist(),cue_valid=cm[tr].sum(0).tolist(),mask_policy=info['emotion_mask_policy']))
 info['files_sha256']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.name!='prepared.json'}
 write(out/'prepared.json',info);event('prepared',**info['counts'])
if __name__=='__main__':main()
