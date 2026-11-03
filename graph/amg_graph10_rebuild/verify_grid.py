from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import json
import numpy as np,pandas as pd
from .data import BASE,PROJECT,read,write,sha,load
from .build import RUN,RELATIONS
def main():
 prot=read(RUN/'manifest/protocol.json');sp=prot['source_paths']
 d=load(release_path=sp['release'],emotion_run=sp['emotion_run'],plan_path=sp['source_plan'],annotation_verification=sp['annotation_verification'])
 f=pd.read_parquet(RUN/'graph/candidate_edge_audit.parquet');g=read(RUN/'validation/grid_results.json')
 assert len(g['results'])==12
 assert {(r['min_support'],r['joint_support_threshold']) for r in g['results']}=={(s,j) for s in [5,10,20] for j in [0,1,3,5]}
 P=d['P'][d['val']];Q=P[:,:42].astype(float);truth=d['E'][d['val']];valid=d['Em'][d['val']]&(truth.sum(1)>0)
 with np.load(_graph_resolve_path(RUN / 'train_joint_support.npz')) as z:J=z['support']
 def norm(x):
  den=x.sum(1);out=np.zeros_like(x);ok=den>0;out[ok]=x[ok]/den[ok,None];return out
 computed=[]
 for s in [5,10,20]:
  keep=f.estimable&(f.support_count_groups>=s)&(f.npmi_ci95_low>0)&(f.fdr_q<.05)&(f.bootstrap_valid_replicates>=950)
  W=[np.zeros((42,16)),np.zeros((42,10)),np.zeros((16,10))]
  for r in f[keep].itertuples():
   if r.relation_type==RELATIONS[0]:W[0][r.source_index,r.target_index-42]=r.npmi_ci95_low
   elif r.relation_type==RELATIONS[1]:W[1][r.source_index,r.target_index-58]=r.npmi_ci95_low
   else:W[2][r.source_index-42,r.target_index-58]=r.npmi_ci95_low
  a=Q@W[0];rec=[];cover=[]
  for dim in range(6):
   inds=np.flatnonzero(d['dim_of_state']==dim);scores=a[:,inds];avail=scores.sum(1)>0;pred=inds[np.argmax(scores,axis=1)]
   for ai in inds:
    pos=P[:,42+ai]
    if pos.any():rec.append(float((avail&(pred==ai))[pos].mean()))
   m=d['Am'][d['val'],dim]
   if m.any():cover.append(float(avail[m].mean()))
  app=float(np.mean(rec));direct=norm(Q@W[1])
  for joint in [0,1,3,5]:
   tensor=W[0][:,:,None]*W[2][None,:,:]*((J>=joint)&(J>0))
   via=norm(np.einsum('nc,cae->ne',Q,tensor,optimize=True));score=.5*direct+.5*via
   order=np.argsort(-score,axis=1,kind='stable')[:,:5]
   hits=np.take_along_axis(truth,order,axis=1)&(np.take_along_axis(score,order,axis=1)>0)
   emo=float((hits.sum(1)[valid]/truth.sum(1)[valid]).mean())
   metric=dict(min_support=s,joint_support_threshold=joint,edges=int(keep.sum()),objective=.5*(app+emo),
    appraisal_macro_state_recall_at1=app,emotion_sample_macro_recall_at5=emo,
    appraisal_valid_dimension_query_coverage=float(np.mean(cover)),emotion_query_coverage=float((score.sum(1)>0)[valid].mean()),
    appraisal_evaluable_states=len(rec),emotion_evaluable_samples=int(valid.sum()))
   expected=next(r for r in g['results'] if (r['min_support'],r['joint_support_threshold'])==(s,joint))
   assert set(metric)==set(expected)
   for k in metric:np.testing.assert_allclose(metric[k],expected[k],rtol=1e-12,atol=1e-14,err_msg=str((s,joint,k)))
   computed.append(metric)
 selected=sorted(computed,key=lambda r:(-round(r['objective'],12),-r['min_support'],-r['joint_support_threshold']))[0]
 for k in selected:np.testing.assert_allclose(selected[k],g['selected'][k],rtol=1e-12,atol=1e-14)
 for rel,h in read(BASE/'original_preservation_baseline.json').items():assert _graph_hash_matches(PROJECT / rel, h, sha(PROJECT / rel)),rel
 pre=read(BASE/'preflight/input_selection.json');assert pre['passed'] and pre['graph_fit_samples']==27679
 out=dict(passed=True,independently_recomputed_grid_combinations=12,metrics_and_selection_verified=True,
  original_and_previous_ten_node_graphs_preserved=True,selected=selected,
  no_target_dataset_used=True,model_calls=0)
 write(RUN/'manifest/grid_verification.json',out);print(json.dumps(out,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
