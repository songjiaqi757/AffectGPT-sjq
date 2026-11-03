"""Check exposure, bootstrap integrity, frozen logits, complete provenance and actual prompts."""
import copy,json
import numpy as np
from jsonschema import Draft202012Validator
from .common import *
from .runtime import SampleGraphV21
from .calibration import *

def verify(release):
 release=Path(release);m=read(release/'release_manifest.json');c=read(release/'config.json');engine=SampleGraphV21(release);data=dict(np.load(ROOT/'data/development.npz'));evaldata=dict(np.load(ROOT/'data/internal_evaluation.npz'));groups=data['groups'];checks={};schema=Draft202012Validator(read(release/'runtime/sample_graph_schema.json'));reports=[read(ROOT/'work/cues'/f'{j:02d}.json') for j in range(42)];policy=engine.policy['cues']
 legacy_labels=np.load(BASE/'data/labels.npz');checks['original_development_and_evaluation_membership_preserved']=np.array_equal(data['sample_ids'],legacy_labels['sample_ids'][legacy_labels['tune']]) and np.array_equal(evaldata['sample_ids'],legacy_labels['sample_ids'][legacy_labels['evaluation']]) and len(data['sample_ids'])==1538 and len(evaldata['sample_ids'])==1538
 checks['calibration_not_Student_parameter_training']=not(set(data['sample_ids'])&set(legacy_labels['sample_ids'][legacy_labels['train']]))
 checks['text_similarity_is_audit_only']=c['near_duplicate_action']=='audit_only_do_not_exclude' and read(ROOT/'data/student_overlap_report.json')['excluded_development_near_training_groups']==[]
 checks['development_evaluation_ID_disjoint']=not(set(data['sample_ids'])&set(evaldata['sample_ids']))
 checks['no_Student_or_relation_fit']=m['student_retrained'] is False and m['G1_refitted'] is False
 checks['frozen_G1_file_hash_identical']=sha(BASELINE/'learned_relations/G1.npz')==sha(release/'learned_relations/G1.npz')==m['baseline_G1_sha256']
 checks['baseline_release_artifacts_unchanged']=all(sha(BASELINE/f)==expected for f,expected in read(BASELINE/'release_manifest.json')['artifact_sha256'].items())
 for j,r in enumerate(reports):
  valid=np.flatnonzero(data['label_mask'][:,j]&data['available'][:,j]&np.isfinite(data['scores'][:,j]));assert r['valid_indices']==valid.tolist()
  for fold in r['calibration'].get('trace',[]):
   a=np.array(fold['training_indices']);b=np.array(fold['heldout_indices']);assert not(set(a)&set(b));assert not(set(groups[a])&set(groups[b]));assert set(a)|set(b)==set(valid);assert fold['positive']==int(data['targets'][a,j].sum());assert all(data['label_mask'][a,j])
  for trace in r['nested_group_cv']['traces']:
   a=set(trace['training_indices']);b=set(trace['heldout_indices']);assert not(a&b);assert not(set(groups[list(a)])&set(groups[list(b)]))
   for inner in trace['inner_calibration'].get('trace',[]):assert set(inner['training_indices'])<=a and set(inner['heldout_indices'])<=a and not(set(inner['training_indices'])&b)
  p=policy[j];tc=p['candidate']['threshold'];te=p['evidence']['threshold']
  if te is not None:
   assert tc is not None and te>=tc;assert p['evidence']['precision']>=c['evidence']['minimum_precision'];assert p['evidence']['group_precision_lcb']>=c['evidence']['minimum_group_precision_lcb'];assert p['evidence']['predictions']>=c['evidence']['minimum_predictions'];assert p['evidence']['prediction_groups']>=c['evidence']['minimum_prediction_groups'];assert p['stability']['evidence']['activation_rate']>=c['evidence']['minimum_bootstrap_activation_rate']
  if p['calibration']['method']=='deferred':assert tc is None and te is None
  for name in ['candidate','evidence']:
   stats=p['stability'].get(name)
   if stats is not None:assert stats['successful_replicates']+stats['failed_replicates']==stats['replicates']==1000;assert stats['activation_rate']==stats['successful_replicates']/1000
 checks.update(valid_labels_only=True,OOF_self_and_group_exclusion=True,nested_outer_holdout_never_used_for_calibration_or_search=True,threshold_ordering_and_precision_support=True,bootstrap_failures_retained=True,unstable_evidence_deferred=True,all_42_policies_have_status=True)
 # Deterministic replay of a real development Cue, including all 1,000 stability searches.
 j=next(i for i,p in enumerate(policy) if p['candidate']['threshold'] is not None);r=reports[j];ii=np.array(r['valid_indices']);seed=c['seed']+j*1000003;model,p=crossfit_platt(data['scores'][ii,j].astype(float),data['targets'][ii,j].astype(int),groups[ii],ii,c,seed);again,_,_=admission_policy(data['targets'][ii,j].astype(int),p,groups[ii],c,seed+17);checks['deterministic_policy_replay']=digest(again)==digest(r['policy']);checks['deterministic_calibration_replay']=digest(model)==digest(r['calibration'])
 # Synthetic admission fixtures only exercise runtime boundaries, never enter release policy fitting.
 fixture=copy.copy(engine);fixture.policy=copy.deepcopy(engine.policy)
 for p in fixture.policy['cues']:p.update(calibration=dict(method='identity',slope=1.,intercept=0.),candidate=dict(status='admitted',threshold=.3),evidence=dict(status='admitted',threshold=.8))
 def make(name,scores,**kw):
  g=fixture.build(name,scores,**kw);fixture.prompt(g,'open_vocabulary','relation_aware');schema.validate(g);return g
 empty=make('empty',[None]*42);checks['empty_unavailable_fallback']=empty['fallback']['required'] and not empty['nodes'] and all(a['admission_status']=='unavailable' for a in empty['cue_audit'])
 candidate=make('candidate',[.5]*42);checks['candidate_only_never_formal_or_prompt']=all(a['admission_status']=='candidate_only' for a in candidate['cue_audit']) and not candidate['nodes'] and not any(candidate['masks']['prompt'])
 below=make('below',[.1]*42);checks['below_candidate_never_formal']=all(a['admission_status']=='below_candidate' for a in below['cue_audit']) and not below['nodes']
 deferred=make('deferred',[.9]*42,deferred_mask=[True]*42);checks['deferred_preserves_continuous_model_input']=all(a['admission_status']=='deferred' for a in deferred['cue_audit']) and np.allclose(np.array(deferred['relation_contributions']['CE']['logits']),np.repeat(.9,42)@engine.model['CE']+engine.model['CE_bias'])
 nr=make('not_requested',[.9]*42,requested_mask=[False]*42);checks['not_requested_never_formal']=not nr['nodes'] and all(a['admission_status']=='not_requested' for a in nr['cue_audit'])
 invalid=make('invalid',[float('nan')]+[.9]*41,availability=[True]*42,modality_available=dict(text=True,audio=True,visual=True));checks['invalid_Cue_does_not_invalidate_modality']=invalid['cue_audit'][0]['admission_status']=='invalid_score' and invalid['modality_available']['text'] and invalid['masks']['model'][0] is False and invalid['masks']['available'][0] is True
 formal=make('formal',[.9]*42);checks['only_evidence_active_CueEvidence']=all(n['admission_status']=='evidence_active' for n in formal['nodes'] if n['node_type']=='CueEvidence') and formal['coverage']['cue_count']==42
 checks['thresholds_never_mask_G1_input']=np.allclose(np.array(candidate['relation_contributions']['CE']['logits']),np.repeat(.5,42)@engine.model['CE']+engine.model['CE_bias']) and np.allclose(np.array(deferred['relation_contributions']['CA']['logits']),np.repeat(.9,42)@engine.model['CA']+engine.model['CA_bias'])
 hidden=make('hidden',[.9]+[.5]*41);checks['hidden_contributions_are_not_visible_support']=all(a['admission_status']=='candidate_only' for a in hidden['cue_audit'][1:]) and any(v>0 for v in hidden['relation_contributions']['CE']['provenance']['hidden_absolute_fraction'])
 # Actual source examples: validate every matrix entry against the frozen W and full logits.
 maxerr=0.;maxclosure=0.;formal_count=0
 for i in range(min(32,len(evaldata['scores']))):
  g=engine.build(str(evaldata['sample_ids'][i]),[float(v) if a else None for v,a in zip(evaldata['scores'][i],evaldata['available'][i])],evaldata['available'][i].tolist());engine.prompt(g,'polarity');schema.validate(g);qm=np.where(evaldata['available'][i],evaldata['scores'][i],0.)
  for typ in ['CA','CE']:
   row=g['relation_contributions'][typ];mat=np.array(row['contributions']);maxerr=max(maxerr,float(np.max(np.abs(mat-qm[:,None]*engine.model[typ]))));maxclosure=max(maxclosure,float(np.max(np.abs(mat.sum(0)+engine.model[typ+'_bias']-np.array(row['logits'])))))
   assert row['graph_cue_exposure_mask']==g['masks']['evidence'] and row['prompt_cue_exposure_mask']==g['masks']['prompt'];prov=row['provenance'];assert np.allclose(np.array(prov['hidden_absolute_fraction'])+np.array(prov['absolute_visible_fraction']),1)
  for n in g['nodes']:
   if n['node_type']!='CueEvidence':assert n['support_status']=='evidence_supported' and n['absolute_visible_fraction']>=c['formal_relation_min_absolute_visible_fraction'];formal_count+=1
  assert all(not a['entered_prompt'] for a in g['cue_audit'] if a['admission_status']!='evidence_active');assert not any(n['entered_prompt'] for n in g['nodes'] if n['node_type']=='EmotionEvidence')
 checks['all_CA_CE_cells_match_frozen_weights']=maxerr<1e-12;checks['contribution_sum_plus_bias_reconstructs_logits']=maxclosure<1e-10;checks['graph_and_prompt_provenance_masks_consistent']=True;checks['partially_supported_and_model_only_never_formal']=True;checks['polarity_and_open_vocabulary_protection']=True
 tiny=copy.deepcopy(c);tiny.update(bootstrap_replicates=20,threshold_stability_replicates=20,stability_inner_ci_replicates=20);search=GroupThresholdSearch(np.zeros(100,int),np.repeat(.9,100),np.array([str(i) for i in range(100)]),tiny,42);checks['no_positive_predictions_cannot_claim_precision']=search.original(c['evidence'])['threshold'] is None
 checks['human_audit_not_used_for_tuning']=read(ROOT/'data/split_audit_report.json')['manual_audit_labels_read'] is False;checks['target_datasets_not_used']=m['target_datasets_used'] is False
 result=dict(passed=all(checks.values()),checks=checks,contribution_max_absolute_error=maxerr,logit_closure_max_absolute_error=maxclosure,actual_source_cases=32,actual_formal_relation_nodes_checked=formal_count,human_audit_status='not_required_this_internal_round',independent_precision_audit_passed=False,Student_retrained=False,G1_refitted=False)
 write(release/'validation/acceptance_report.json',result);assert result['passed'],result;return result
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--release',required=True);print(json.dumps(verify(a.parse_args().release),ensure_ascii=False,indent=2))
