"""Admission controls exposure only; complete signed CA/CE ledgers retain every model input."""
import copy,collections,math
import numpy as np
from scipy.special import softmax,expit
from ..runtime import SampleGraph as FrozenGraph
from .common import *
from .calibration import mapped
class SampleGraphV21(FrozenGraph):
 def __init__(self,release):
  super().__init__(BASELINE);self.release_root=Path(release);self.v21manifest=read(self.release_root/'release_manifest.json');self.release_id=self.v21manifest['release_id'];self.policy=read(self.release_root/'admission/cue_admission_policy.json');self.v21config=read(self.release_root/'config.json');self.prompt_policy=read(self.release_root/'runtime/prompt_policy.json');self._stable={}
  assert self.v21manifest['baseline_G1_sha256']==sha(BASELINE/'learned_relations/G1.npz')
  for typ in ['CA','CE']:
   mask=np.zeros_like(self.model[typ],bool)
   for e in self.edges[typ]:mask[e['source_index'],e['target_index']]=True
   self._stable[typ]=mask
 def build(self,sample_id,scores,availability=None,requested_mask=None,deferred_mask=None,modality_available=None,cue_prediction_success=None):
  if len(scores)!=42:raise ValueError('Expected 42 Cue scores')
  av=np.array([s is not None for s in scores],bool) if availability is None else np.asarray(availability);req=np.ones(42,bool) if requested_mask is None else np.asarray(requested_mask);deferred=np.zeros(42,bool) if deferred_mask is None else np.asarray(deferred_mask);success=np.ones(42,bool) if cue_prediction_success is None else np.asarray(cue_prediction_success)
  for mask in [av,req,deferred,success]:
   if mask.shape!=(42,) or mask.dtype!=bool:raise ValueError('Masks must contain 42 booleans')
  mod={m:bool(av[a:b].any()) for m,a,b in [('text',0,15),('audio',15,32),('visual',32,42)]} if modality_available is None else dict(modality_available)
  if set(mod)!={'text','audio','visual'} or any(type(v) is not bool for v in mod.values()):raise ValueError('modality_available needs three booleans')
  raw=np.zeros(42);valid=np.zeros(42,bool);available=av.copy();source_score=np.full(42,np.nan);candidate=np.zeros(42,bool);evidence=np.zeros(42,bool);audit=[]
  for j,(s,pol) in enumerate(zip(scores,self.policy['cues'])):
   modality='text' if j<15 else 'audio' if j<32 else 'visual';available[j]=av[j] and mod[modality]
   try:valid[j]=not isinstance(s,(bool,np.bool_)) and s is not None and bool(np.isfinite(s)) and 0<=float(s)<=1
   except (TypeError,ValueError):valid[j]=False
   valid[j]&=success[j]
   if valid[j]:raw[j]=float(s)
   model=pol['calibration'];tc=pol['candidate']['threshold'];te=pol['evidence']['threshold']
   if available[j] and valid[j] and model['method']!='deferred':source_score[j]=mapped(np.array([raw[j]]),model,self.v21config)[0]
   if not available[j]:status='unavailable'
   elif not req[j]:status='not_requested'
   elif not valid[j]:status='invalid_score'
   elif deferred[j] or model['method']=='deferred' or (tc is None and te is None):status='deferred'
   elif te is not None and source_score[j]>=te:status='evidence_active';evidence[j]=True;candidate[j]=True
   elif tc is not None and source_score[j]>=tc:status='candidate_only';candidate[j]=True
   else:status='below_candidate'
   audit.append(dict(cue_type_id=self.cue_ids[j],cue_index=j,modality=modality,modality_available=mod[modality],cue_available=bool(available[j]),cue_score_valid=bool(valid[j]),cue_prediction_success=bool(success[j]),cue_requested=bool(req[j]),raw_score=float(raw[j]) if valid[j] else None,source_calibrated_score=float(source_score[j]) if np.isfinite(source_score[j]) else None,calibration_status=model['method'],admission_status=status,evidence_policy_status=pol['evidence']['status'],candidate_threshold=tc,evidence_threshold=te,graph_exposed=bool(evidence[j]),entered_prompt=False))
  modelmask=available&valid;qm=np.where(modelmask,raw,0.)
  # Reuse the frozen v2 model and confidence gates with per-call evidence masks.
  # The temporary exposure thresholds are internal plumbing, never G1 inputs.
  proxy=copy.copy(self);proxy.cue_policy=dict(cue_ids=self.cue_ids,thresholds=[0. if e else 1.1 for e in evidence],calibration_slope=[1.]*42,calibration_intercept=[0.]*42,calibration_status=['platt_v21_exposure_mask']*42)
  g=FrozenGraph.build(proxy,sample_id,[float(raw[j]) if modelmask[j] else None for j in range(42)],modelmask.tolist(),req.tolist(),deferred.tolist());g['schema_version']='amg_sample_graph_v2_1';g['graph_release_id']=self.release_id
  contributions={t:qm[:,None]*self.model[t] for t in ['CA','CE']};provenance={}
  for typ in ['CA','CE']:
   mat=contributions[typ];visible=evidence[:,None]&self._stable[typ];absall=np.abs(mat).sum(0);posall=np.maximum(mat,0).sum(0);absvis=(np.abs(mat)*visible).sum(0);posvis=(np.maximum(mat,0)*visible).sum(0);frac=np.divide(absvis,absall,out=np.zeros_like(absvis),where=absall>0);posfrac=np.divide(posvis,posall,out=np.zeros_like(posvis),where=posall>0);status=[]
   for k in range(mat.shape[1]):
    status.append('evidence_supported' if frac[k]>=self.v21config['formal_relation_min_absolute_visible_fraction'] and posfrac[k]>=self.v21config['formal_relation_min_positive_visible_fraction'] and posvis[k]>0 else 'partially_supported' if frac[k]>=self.v21config['partial_relation_min_absolute_visible_fraction'] and posvis[k]>0 else 'model_only')
   provenance[typ]=dict(absolute_visible_fraction=frac.tolist(),positive_visible_fraction=posfrac.tolist(),hidden_absolute_fraction=(1-frac).tolist(),visible_signed_contribution=(mat*visible).sum(0).tolist(),hidden_signed_contribution=(mat*(~visible)).sum(0).tolist(),support_status=status,bias=self.model[typ+'_bias'].tolist(),scope='Stable admitted relations from formal CueEvidence versus ALL continuous Cue contributions; bias recorded separately')
  kept=[]
  for node in g['nodes']:
   if node['node_type']=='CueEvidence':
    j=self.cue_ids.index(node['ontology_id']);node.update(activation_status='evidence_active',admission_status='evidence_active',raw_score=float(raw[j]),source_calibrated_score=float(source_score[j]),calibrated_score=float(source_score[j]),score=float(source_score[j]),score_semantics='source_pseudolabel_calibrated_score_not_cross_domain_probability',entered_prompt=False);kept.append(node)
   else:
    typ='CA' if node['node_type']=='AppraisalEvidence' else 'CE';k=self.states.index(node['ontology_id']) if typ=='CA' else self.emotion_ids.index(node['ontology_id']);node.update(support_status=provenance[typ]['support_status'][k],absolute_visible_fraction=provenance[typ]['absolute_visible_fraction'][k],positive_visible_fraction=provenance[typ]['positive_visible_fraction'][k],entered_prompt=False)
    if node['support_status']=='evidence_supported':kept.append(node)
  g['nodes']=kept;instances={n['instance_id'] for n in kept};g['edges']=[e for e in g['edges'] if e['source'] in instances and (e.get('target_scope')=='ontology' or e['target'] in instances)]
  signals=[dict(**a,signal_id=f'{sample_id}::signal::{a["cue_type_id"]}',node_type='CueSignal',participates_in_model=bool(modelmask[j]),model_input=float(qm[j])) for j,a in enumerate(audit)]
  ledger={}
  for typ,targets in [('CA',self.states),('CE',self.emotion_ids)]:
   ledger[typ]=dict(relation_type=typ,cue_id_order=self.cue_ids,target_id_order=targets,contributions=contributions[typ].tolist(),bias=self.model[typ+'_bias'].tolist(),logits=(qm@self.model[typ]+self.model[typ+'_bias']).tolist(),stable_global_edge_mask=self._stable[typ].tolist(),sign_encoding='Sign is preserved in every numeric matrix cell; conditional logit contribution, not probability or causal effect',graph_cue_exposure_mask=evidence.tolist(),prompt_cue_exposure_mask=[False]*42,formal_output_mask=[any(n['ontology_id']==t for n in kept if n['node_type']!='CueEvidence') for t in targets],graph_relation_exposure_mask=(evidence[:,None]&self._stable[typ]&np.array([any(n['ontology_id']==t for n in kept if n['node_type']!='CueEvidence') for t in targets])[None,:]).tolist(),prompt_relation_exposure_mask=np.zeros_like(self._stable[typ],bool).tolist(),provenance=provenance[typ])
  za=np.array(ledger['CA']['logits']);app=[]
  for d,cols in enumerate(self.dimcols):
   probs=softmax(za[cols]/self.cal['appraisal_temperature'][d]);k=int(cols[probs.argmax()]);app.append(dict(dimension_id=self.dims[d],top_state_id=self.states[k],state_probability=float(probs.max()),support_status=provenance['CA']['support_status'][k],absolute_visible_fraction=provenance['CA']['absolute_visible_fraction'][k],positive_visible_fraction=provenance['CA']['positive_visible_fraction'][k],formal_output=any(n.get('state_id')==self.states[k] for n in kept)))
  zce=np.array(ledger['CE']['logits']);ce=self.cal['branches']['CE'];pce=expit(zce*np.array(ce['slope'])+np.array(ce['intercept']));emotion=[dict(emotion_id=self.emotion_ids[k],direct_score=float(pce[k]),above_frozen_emotion_threshold=bool(pce[k]>=ce['thresholds'][k]),support_status=provenance['CE']['support_status'][k],absolute_visible_fraction=provenance['CE']['absolute_visible_fraction'][k],positive_visible_fraction=provenance['CE']['positive_visible_fraction'][k],formal_output=any(n.get('emotion_id')==self.emotion_ids[k] for n in kept)) for k in range(188)]
  count=collections.Counter(n['node_type'] for n in kept);g.update(cue_audit=audit,cue_signals=signals,candidate_cues=[dict(a,node_type='CandidateCue') for a in audit if a['admission_status']=='candidate_only'],relation_contributions=ledger,relation_outputs=dict(appraisal=app,emotion=emotion),masks=dict(available=available.tolist(),score_valid=valid.tolist(),model=modelmask.tolist(),candidate=candidate.tolist(),evidence=evidence.tolist(),prompt=[False]*42),modality_available=mod,coverage=dict(cue_signal_count=int(modelmask.sum()),cue_count=count['CueEvidence'],candidate_only_count=sum(a['admission_status']=='candidate_only' for a in audit),appraisal_supported_count=count['AppraisalEvidence'],appraisal_unresolved_dimensions=6-count['AppraisalEvidence'],emotion_candidate_count=count['EmotionEvidence'],available_modalities=mod),fallback=dict(required=not bool(evidence.any()),reason='no_formal_CueEvidence' if not evidence.any() else None,target='original_affectgpt'),evidence_profile='source_pseudolabel_nested_CV_internal_v21',student_retrained=False,G1_refitted=False,cue_training_predictions_oof=False,calibration_oof=True,semantics='Candidate is internal only. All available valid raw continuous scores still feed frozen G1. Hidden, deferred and unrequested Cue contributions are recorded and never attributed to visible evidence.')
  return g
 def build_from_old_cue(self,cue):
  if cue['cue_id_order']!=self.cue_ids or cue['runtime_release_id']!=self.binding['runtime_release_id']:raise ValueError('Original Student release or ontology mismatch')
  for m,spec in self.binding['checkpoints'].items():
   if cue['model_versions'][m]['checkpoint_sha256']!=spec['sha256']:raise ValueError('Cue checkpoint mismatch')
  return self.build(cue['sample_id'],cue['scores'],cue['availability_mask'],cue.get('requested_mask'),cue.get('deferred_mask'),cue.get('modality_present'))
 def prompt(self,g,task='open_vocabulary',mode='relation_aware',cue_limit=None):
  if task not in ('discrete_emotion','polarity','open_vocabulary') or mode not in ('node_only','relation_aware'):raise ValueError('Unknown task or prompt mode')
  limit=self.prompt_policy['cue_top_k'] if cue_limit is None else cue_limit;pm=np.zeros(42,bool);entered=set();text=[]
  if not g['fallback']['required']:
   cues=sorted((n for n in g['nodes'] if n['node_type']=='CueEvidence' and n['admission_status']=='evidence_active'),key=lambda n:(-n['score'],n['ontology_id']))[:limit]
   for n in cues:j=self.cue_ids.index(n['ontology_id']);pm[j]=True;entered.add(n['instance_id'])
   text=['Optional source-calibrated observable Cue detections. Check the original multimodal input. Model scores are not psychological facts or target-domain probability guarantees. Candidate/deferred signals are audit-only; absent evidence does not prove absence.']+['Cue: '+n['ontology_id'] for n in cues]
  for typ in ['CA','CE']:
   row=g['relation_contributions'][typ];mat=np.array(row['contributions']);visible=pm[:,None]&self._stable[typ];absall=np.abs(mat).sum(0);posall=np.maximum(mat,0).sum(0);af=np.divide((np.abs(mat)*visible).sum(0),absall,out=np.zeros_like(absall),where=absall>0);pf=np.divide((np.maximum(mat,0)*visible).sum(0),posall,out=np.zeros_like(posall),where=posall>0);row['prompt_cue_exposure_mask']=pm.tolist();row['provenance']['prompt_absolute_visible_fraction']=af.tolist();row['provenance']['prompt_positive_visible_fraction']=pf.tolist()
   if mode=='relation_aware' and not g['fallback']['required']:
    for n in g['nodes']:
     if (typ=='CA' and n['node_type']!='AppraisalEvidence') or (typ=='CE' and n['node_type']!='EmotionEvidence'):continue
     if typ=='CE' and task!='discrete_emotion':continue
     k=self.states.index(n['ontology_id']) if typ=='CA' else self.emotion_ids.index(n['ontology_id'])
     if af[k]<self.v21config['formal_relation_min_absolute_visible_fraction'] or pf[k]<self.v21config['formal_relation_min_positive_visible_fraction']:continue
     text.append(('Tentative appraisal hypothesis: '+n['dimension_id']+' / '+n['state_id']) if typ=='CA' else 'Optional emotion candidate: '+n['canonical_name']);entered.add(n['instance_id'])
  if text:
   if task=='polarity':text.append('Judge polarity from the original evidence; discrete emotion names do not determine valence.')
   if task=='open_vocabulary':text.append('Use unrestricted emotion vocabulary. Graph candidates never restrict the allowed answer.')
  for n in g['nodes']:n['entered_prompt']=n['instance_id'] in entered
  for j,(a,s) in enumerate(zip(g['cue_audit'],g['cue_signals'])):a['entered_prompt']=bool(pm[j]);s['entered_prompt']=bool(pm[j])
  for e in g['edges']:e['entered_prompt']=e.get('target_scope')=='sample' and e['source'] in entered and e['target'] in entered
  for typ in ['CA','CE']:
   targets=self.states if typ=='CA' else self.emotion_ids;target_entered=np.array([any(n['ontology_id']==t and n['instance_id'] in entered for n in g['nodes'] if n['node_type']!='CueEvidence') for t in targets]);g['relation_contributions'][typ]['prompt_relation_exposure_mask']=(pm[:,None]&self._stable[typ]&target_entered[None,:]).tolist()
  g['masks']['prompt']=pm.tolist();g['prompt_audit']=dict(task=task,mode=mode,serialized_formal_cue_count=int(pm.sum()),candidate_serialized_count=0,serialized_instance_ids=sorted(entered),character_count=len('\n'.join(text)),downstream_validation='not_run_in_this_internal_release');return '\n'.join(text)
