"""Meaningful invariants: exposure, masks, independent recomputation, unavailable and fallback."""
import json,collections
import numpy as np
from .common import *
from .runtime import SampleGraph,prompt_evidence
from .models import app_predict

def verify(release,write_report=True):
 from jsonschema import Draft202012Validator
 release=Path(release);engine=SampleGraph(release);schema=read(release/'runtime/schema.json');validator=Draft202012Validator(schema);z=np.load(ROOT/'data/labels.npz');q=np.load(ROOT/'data/cue_scores.npz');tr=z['train'];fold=z['fold'];groups=z['groups'];checks={};info=read(ROOT/'data/prepared.json')
 train_ids=set(z['sample_ids'][tr]);tune_ids=set(z['sample_ids'][z['tune']]);eval_ids=set(z['sample_ids'][z['evaluation']]);checks['source_roles_disjoint']=not(train_ids&tune_ids or train_ids&eval_ids or tune_ids&eval_ids)
 rows=read(ROOT/'data/input_rows.json');checks['reserved_500_not_read_for_build']=len(rows)==30755 and all(r['role'] in ('pseudo_train','pseudo_validation') for r in rows)
 checks['appraisal_mask_dimension_integrity']=bool(np.all(z['app_y'][~z['app_mask']]==-1) and np.all(z['app_y'][z['app_mask']]>=0))
 checks['unknown_cue_not_negative_supervision']=bool(np.any(~z['cue_mask']))
 checks['partial_emotion_sets_have_masked_cells']=bool(np.any(~z['emotion_mask']) and np.all(z['emotion_mask'][z['emotion_y']==1]))
 checks['no_cue_student_training']=info['student_retrained'] is False and read(ROOT/'data/cache_verification.json')['student_retrained'] is False
 checks['oof_deviation_explicit']=info['cue_prediction_oof'] is False and engine.manifest['cue_oof'] is False
 dims=engine.dimcols;model=dict(np.load(release/'learned_relations/G1.npz'));maxdiff=0.;crossfit=model['cross_fitted_appraisal'];qq=q['scores'][tr]
 for k in range(5):
  a=np.load(release/f'validation/relation_folds/relation_fold{k}.npz');v=fold[tr]==k;checks[f'fold_{k}_groups_disjoint']=not(set(groups[tr][v])&set(groups[tr][~v]));p=app_predict(qq[v],a['CA'],a['CA_bias'],dims);maxdiff=max(maxdiff,float(np.abs(p-crossfit[v]).max()))
 checks['cross_fitted_appraisal_independent_recomputation']=maxdiff<1e-10
 # Independent scalar logit recomputation catches orientation, bias and Cue-order errors.
 sid=0;fast=qq[sid]@model['CE']+model['CE_bias'];slow=np.array([model['CE_bias'][e]+sum(float(qq[sid,c])*float(model['CE'][c,e]) for c in range(42)) for e in range(188)]);checks['CE_scalar_weight_recomputation']=bool(np.allclose(fast,slow,atol=1e-10))
 for typ in ['CA','CE','AE']:
  for e in engine.edges[typ]:
   assert e['weight']==model[typ][e['source_index'],e['target_index']]
   assert e['fold_sign_consistency']>=engine.config['minimum_fold_sign_consistency'];assert not(e['bootstrap_lower']<=0<=e['bootstrap_upper']);assert e['dev_contribution']>0
 checks['admitted_edge_audit_recomputed']=True
 empty=engine.build('test_empty',[None]*42);validator.validate(empty);checks['empty_graph_fallback']=empty['fallback']['required'] and not empty['nodes'];checks['unavailable_not_negative']=all(a['activation_status']=='unavailable' and a['raw_score'] is None for a in empty['cue_audit'])
 deferred=engine.build('test_deferred',[.9]*42,deferred_mask=[True]*42);checks['deferred_not_active']=deferred['fallback']['required'] and not deferred['nodes'] and all(a['activation_status']=='deferred' for a in deferred['cue_audit'])
 not_requested=engine.build('test_not_requested',[.9]*42,requested_mask=[False]*42);checks['not_requested_distinct']=not_requested['fallback']['required'] and all(a['activation_status']=='not_requested' for a in not_requested['cue_audit'])
 bad=0
 for scores in [[.5]*41,[float('nan')]*42,[1.1]*42]:
  try:engine.build('test_bad',scores)
  except (ValueError,TypeError):bad+=1
 checks['invalid_scores_rejected']=bad==3
 try:engine.build('test_bad_unavailable',[0.]*42,availability=[False]*42);checks['zero_cannot_replace_unavailable']=False
 except ValueError:checks['zero_cannot_replace_unavailable']=True
 checks['fallback_prompt_empty']=prompt_evidence(empty)==''
 cache=Path(engine.binding['source_cache']);checked=0;softmax_error=0.;relation_edges=0
 for i in np.flatnonzero(z['evaluation'])[:50]:
  rec=read(cache/(str(z['sample_ids'][i])+'.json'));g=engine.build_from_old_cue(rec['cue']);validator.validate(g);d=[n['dimension_id'] for n in g['nodes'] if n['node_type']=='AppraisalEvidence'];assert len(d)==len(set(d));assert all(n['instance_id'].startswith(g['sample_id']+'::') for n in g['nodes']);instances={n['instance_id'] for n in g['nodes']}
  for e in g['edges']:
   assert e['source'] in instances
   if e.get('target_scope')=='sample':assert e['target'] in instances;relation_edges+=1
  if not engine.cal['path_branch_enabled']:assert not any(e['relation_type']=='APPRAISAL_TO_EMOTION' for e in g['edges'])
  txt=prompt_evidence(g,'polarity');assert 'Optional emotion candidate:' not in txt
  txt=prompt_evidence(g,'open_vocabulary');assert 'Optional emotion candidate:' not in txt
  checked+=1
 checks['sample_schema_instance_scope_and_exclusive_states']=checked==50;checks['failed_path_branch_never_enters_samples']=True;checks['polarity_and_open_vocabulary_protection']=True
 # Version and ontology mistakes must be rejected before producing evidence.
 rec=read(cache/(str(z['sample_ids'][0])+'.json'))['cue'];rec['cue_id_order']=list(reversed(rec['cue_id_order']))
 try:engine.build_from_old_cue(rec);checks['wrong_cue_order_rejected']=False
 except ValueError:checks['wrong_cue_order_rejected']=True
 report=dict(passed=all(checks.values()),checks=checks,independent_CA_recomputation_max_absolute_error=maxdiff,source_sample_schema_cases=checked,sample_relation_edges_checked=relation_edges,student_retrained=False,cue_oof=False,strict_document_P0_complete=False,internal_engineering_graph_complete=all(checks.values()))
 if write_report:write(release/'validation/acceptance_report.json',report)
 assert report['passed'],report
 return report
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--release',required=True);v=a.parse_args();print(json.dumps(verify(v.release),ensure_ascii=False,indent=2))
