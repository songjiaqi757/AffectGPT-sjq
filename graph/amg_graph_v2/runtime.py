"""Independent sample evidence runtime. Reads frozen parameters; fits nothing."""
import collections,json
from pathlib import Path
import numpy as np
from scipy.special import expit,logit,softmax
from .common import read
class SampleGraph:
 def __init__(self,release):
  self.root=Path(release);self.manifest=read(self.root/'release_manifest.json');self.release_id=self.manifest['release_id'];self.ontology=read(self.root/'ontology/index.json');self.cue_ids=self.ontology['cue_ids'];self.states=self.ontology['states'];self.emotion_ids=self.ontology['emotion_ids'];self.dims=self.ontology['dimensions'];self.dimcols=[np.flatnonzero(np.array(self.ontology['state_dim'])==d) for d in range(6)]
  self.model=dict(np.load(self.root/'learned_relations/G1.npz'));self.cal=read(self.root/'calibration/relation_calibration.json');self.cue_policy=read(self.root/'calibration/cue_policy.json');self.config=read(self.root/'config.json');self.edges=read(self.root/'learned_relations/admitted_edges.json');self.paths=[p for p in read(self.root/'paths/path_audit.json') if p['admission_status']=='admitted'];self.app_metadata=read(self.root/'ontology/appraisal_dimensions.json');self.emotion_names=self.ontology['emotion_names'];self.binding=read(self.root/'runtime/student_binding.json');self.prompt_policy=read(self.root/'runtime/prompt_policy.json');self.by_target={t:collections.defaultdict(list) for t in self.edges}
  for typ,edges in self.edges.items():
   for edge in edges:self.by_target[typ][edge['target_index']].append(edge)
 def build(self,sample_id,scores,availability=None,requested_mask=None,deferred_mask=None):
  if not isinstance(sample_id,str) or not sample_id:raise ValueError('sample_id must be nonempty')
  if len(scores)!=42:raise ValueError('Expected exactly 42 Cue scores in frozen ontology order')
  av=np.array([s is not None for s in scores],bool) if availability is None else np.asarray(availability)
  requested=np.ones(42,bool) if requested_mask is None else np.asarray(requested_mask)
  deferred=np.zeros(42,bool) if deferred_mask is None else np.asarray(deferred_mask)
  for name,mask in [('availability',av),('requested',requested),('deferred',deferred)]:
   if mask.shape!=(42,) or mask.dtype!=bool:raise ValueError(name+' mask must contain 42 booleans')
  q=np.zeros(42)
  for j,s in enumerate(scores):
   if av[j]:
    if s is None or isinstance(s,bool) or not np.isfinite(s) or not 0<=s<=1:raise ValueError('Available Cue scores must be finite in [0,1]')
    q[j]=float(s)
   elif s is not None:raise ValueError('Unavailable Cue scores must be null, not negative/zero labels')
  cp=self.cue_policy;cals=expit(logit(np.clip(q,1e-6,1-1e-6))*np.array(cp['calibration_slope'])+np.array(cp['calibration_intercept']));policy_deferred=np.array([not s.startswith('platt_') for s in cp['calibration_status']])|(np.array(cp['thresholds'])>1);deferred=deferred|policy_deferred
  nodes=[];edges=[];active={};cue_audit=[]
  for j,c in enumerate(self.cue_ids):
   status='unavailable' if not av[j] else 'not_requested' if not requested[j] else 'deferred' if deferred[j] else 'active' if cals[j]>=cp['thresholds'][j] else 'below_threshold'
   cue_audit.append(dict(cue_type_id=c,activation_status=status,availability='available' if av[j] else 'unavailable',raw_score=float(q[j]) if av[j] else None,calibrated_score=float(cals[j]) if av[j] and cp['calibration_status'][j].startswith('platt_') else None))
   if status=='active':
    iid=f'{sample_id}::cue::{c}';active[j]=iid;nodes.append(dict(instance_id=iid,node_type='CueEvidence',sample_id=sample_id,ontology_id=c,cue_type_id=c,modality='text' if j<15 else 'audio' if j<32 else 'visual',raw_score=float(q[j]),calibrated_score=float(cals[j]),score=float(cals[j]),score_semantics='internal_development_Platt_score',availability='available',activation_status='active',student_release_id=self.binding['runtime_release_id'],calibration_release_id=self.release_id+'::cue'))
    edges.append(dict(edge_id=iid+'::INSTANCE_OF',relation_type='INSTANCE_OF',source=iid,target=c,target_scope='ontology',sample_id=sample_id))
  # Probabilistic model uses available raw scores, exactly as fitted. Active/deferred
  # decisions gate evidence exposure, rather than altering the frozen score distribution.
  qm=np.where(av,q,0.)
  za=qm@self.model['CA']+self.model['CA_bias'];pa=np.zeros(16);pacal=np.zeros(16);app_instances={};app_audit=[]
  for d,cols in enumerate(self.dimcols):
   pa[cols]=softmax(za[cols]);pacal[cols]=softmax(za[cols]/self.cal['appraisal_temperature'][d]);rank=np.argsort(pacal[cols]);s=int(cols[rank[-1]]);prob=float(pacal[s]);margin=float(pacal[cols[rank[-1]]]-pacal[cols[rank[-2]]]);entropy=float(-(pacal[cols]*np.log(np.clip(pacal[cols],1e-8,1))).sum()/np.log(len(cols)));gate=self.cal['appraisal_gates'][d]
   available_edges=[e for e in self.by_target['CA'][s] if e['source_index'] in active];positive=sum(max(0,qm[e['source_index']]*e['weight']) for e in available_edges);den=float(np.dot(qm,np.maximum(self.model['CA'][:,s],0)));coverage=positive/max(1e-12,den);reasons=[]
   if prob<gate['threshold']:reasons.append('low_state_confidence')
   if margin<gate['margin'] or entropy>gate['max_normalized_entropy']:reasons.append('state_ambiguous')
   if self.app_metadata[d]['valid_training_samples']<self.config['appraisal_minimum_training_valid']:reasons.append('insufficient_dimension_supervision')
   if positive<=0 or coverage<.5:reasons.append('insufficient_active_stable_Cue_coverage')
   row=dict(dimension_id=self.dims[d],state_id=self.states[s] if not reasons else None,status='supported' if not reasons else 'unresolved',top_state_audit=self.states[s],state_probability=prob,margin=margin,normalized_entropy=entropy,evidence_coverage=coverage,reasons=reasons)
   app_audit.append(row)
   if not reasons:
    iid=f'{sample_id}::appraisal::{self.states[s]}';app_instances[s]=iid;nodes.append(dict(instance_id=iid,node_type='AppraisalEvidence',sample_id=sample_id,ontology_id=self.states[s],dimension_id=self.dims[d],state_id=self.states[s],state_probability=prob,raw_model_probability=float(pa[s]),score=prob,dimension_confidence=prob,evidence_coverage=coverage,status='supported',relation_model_release_id=self.release_id));edges.append(dict(edge_id=iid+'::INSTANCE_OF',relation_type='INSTANCE_OF',source=iid,target=self.states[s],target_scope='ontology',sample_id=sample_id))
    for e in available_edges:edges.append(self.local_edge(sample_id,e,active[e['source_index']],iid,qm[e['source_index']]*e['weight'],qm[e['source_index']],'SUPPORTS_APPRAISAL'))
  zce=qm@self.model['CE']+self.model['CE_bias'];zae=pa@self.model['AE']+self.model['AE_bias'];branches=self.cal['branches'];pce=expit(zce*np.array(branches['CE']['slope'])+np.array(branches['CE']['intercept']));pae=expit(zae*np.array(branches['AE']['slope'])+np.array(branches['AE']['intercept']));fc=branches['fusion'];zf=zce+fc['alpha']*zae+np.array(fc['bias']);pf=expit(zf*np.array(fc['slope'])+np.array(fc['intercept']));use_fused=self.cal['path_branch_enabled'];prob=pf if use_fused else pce;selected_spec=fc if use_fused else branches['CE'];threshold=np.array(selected_spec['thresholds']);emotion_audit=[]
  admitted_paths=collections.defaultdict(list)
  if use_fused:
   for p in self.paths:
    c=self.cue_ids.index(p['cue_id']);a=self.states.index(p['appraisal_state_id']);e=self.emotion_ids.index(p['emotion_id'])
    if c in active and a in app_instances and self.model['CA'][c,a]>0 and self.model['AE'][a,e]>0:admitted_paths[e].append(p)
  for e in np.argsort(prob)[::-1]:
   e=int(e);ce_edges=[r for r in self.by_target['CE'][e] if r['source_index'] in active] if self.cal['CE_branch_enabled'] else [];direct=sum(max(0,qm[r['source_index']]*r['weight']) for r in ce_edges);den=float(qm@np.maximum(self.model['CE'][:,e],0));ce_coverage=direct/max(den,1e-12);path_support=admitted_paths[e];reasons=[]
   if prob[e]<threshold[e]:reasons.append('below_emotion_threshold')
   if not selected_spec['status'][e].startswith('platt_'):reasons.append('uncalibrated_emotion_score')
   if (direct<=0 or ce_coverage<.5) and not path_support:reasons.append('no_active_validated_incoming_evidence')
   if not reasons:
    iid=f'{sample_id}::emotion::{self.emotion_ids[e]}';sc=[self.cue_ids[r['source_index']] for r in ce_edges if r['weight']>0];ap=sorted({p['appraisal_state_id'] for p in path_support});nodes.append(dict(instance_id=iid,node_type='EmotionEvidence',sample_id=sample_id,ontology_id=self.emotion_ids[e],emotion_id=self.emotion_ids[e],canonical_name=self.emotion_names[e],direct_score=float(pce[e]),appraisal_score=float(pae[e]),fused_score=float(pf[e]),score=float(prob[e]),score_semantics='internal_development_calibrated_candidate_score',supporting_cues=sc,supporting_appraisal_states=ap,evidence_coverage=ce_coverage,status='supported',model_release_id=self.release_id))
    edges.append(dict(edge_id=iid+'::INSTANCE_OF',relation_type='INSTANCE_OF',source=iid,target=self.emotion_ids[e],target_scope='ontology',sample_id=sample_id))
    for r in ce_edges:edges.append(self.local_edge(sample_id,r,active[r['source_index']],iid,qm[r['source_index']]*r['weight'],qm[r['source_index']],'PREDICTS_EMOTION'))
    for a in app_instances:
     if self.states[a] in ap:
      for r in self.by_target['AE'][e]:
       if r['source_index']==a:edges.append(self.local_edge(sample_id,r,app_instances[a],iid,pa[a]*r['weight'],pa[a],'APPRAISAL_TO_EMOTION'))
   if prob[e]>=min(1.,threshold[e]) or not reasons:emotion_audit.append(dict(emotion_id=self.emotion_ids[e],score=float(prob[e]),status='supported' if not reasons else 'unsupported',reasons=reasons))
  counts=collections.Counter(n['node_type'] for n in nodes);cue_count=counts['CueEvidence'];app_count=counts['AppraisalEvidence'];emo_count=counts['EmotionEvidence'];fallback=not cue_count or not(app_count or emo_count);reason='no_active_reliable_Cue' if not cue_count else 'no_validated_sample_relation' if fallback else None
  return dict(schema_version='amg_sample_graph_v2',sample_id=sample_id,graph_release_id=self.release_id,cue_release_id=self.binding['cue_release_id'],calibration_release_id=self.release_id+'::calibration',student_retrained=False,cue_training_predictions_oof=False,prompt_limits=self.prompt_policy,nodes=nodes,edges=edges,cue_audit=cue_audit,appraisal_audit=app_audit,candidate_audit=emotion_audit,coverage=dict(cue_count=cue_count,appraisal_supported_count=app_count,appraisal_unresolved_dimensions=6-app_count,emotion_candidate_count=emo_count,available_modalities={m:bool(av[a:b].all()) for m,a,b in [('text',0,15),('audio',15,32),('visual',32,42)]}),fallback=dict(required=fallback,reason=reason,target='original_affectgpt'),evidence_profile='internal_source_engineering',semantics='Conditional model associations; calibrated scores are internal-development estimates; no psychological causal or factual claim')
 def local_edge(self,sample_id,e,source,target,contribution,input_score,relation_type):
  return dict(edge_id=sample_id+'::'+e['edge_id'],global_edge_id=e['edge_id'],sample_id=sample_id,relation_type=relation_type,source=source,target=target,target_scope='sample',contribution=float(contribution),contribution_semantics='signed_conditional_logit_contribution_not_probability',input_score=float(input_score),sign=e['sign'],fold_sign_consistency=e['fold_sign_consistency'],bootstrap_interval=[e['bootstrap_lower'],e['bootstrap_upper']],model_release_id=self.release_id,entered_prompt=False)
 def build_from_old_cue(self,cue):
  if cue['cue_id_order']!=self.cue_ids:raise ValueError('Cue ontology order mismatch')
  if cue['runtime_release_id']!=self.binding['runtime_release_id']:raise ValueError('Cue Student release mismatch')
  for m,spec in self.binding['checkpoints'].items():
   if cue['model_versions'][m]['checkpoint_sha256']!=spec['sha256']:raise ValueError('Cue checkpoint mismatch')
  return self.build(cue['sample_id'],cue['scores'],cue['availability_mask'],cue.get('requested_mask'),cue.get('deferred_mask'))

def prompt_evidence(sample_graph,task='open_vocabulary',cue_limit=None,emotion_limit=None):
 cue_limit=sample_graph['prompt_limits']['cue_top_k'] if cue_limit is None else cue_limit
 emotion_limit=sample_graph['prompt_limits']['emotion_top_k'] if emotion_limit is None else emotion_limit
 if task not in ('discrete_emotion','polarity','open_vocabulary'):raise ValueError('Unknown task protection profile')
 if sample_graph['fallback']['required']:return ''
 cues=sorted((n for n in sample_graph['nodes'] if n['node_type']=='CueEvidence'),key=lambda n:n['score'],reverse=True)[:cue_limit];apps=[n for n in sample_graph['nodes'] if n['node_type']=='AppraisalEvidence'];emos=sorted((n for n in sample_graph['nodes'] if n['node_type']=='EmotionEvidence'),key=lambda n:n['score'],reverse=True)[:emotion_limit]
 lines=['Optional model-detected evidence. Scores and relations are conditional estimates, not psychological facts. Use the original video and audio as primary evidence.']
 lines+=['Cue: '+n['ontology_id'] for n in cues];lines+=['Tentative appraisal: '+n['dimension_id']+' / '+n['state_id'] for n in apps]
 if task=='discrete_emotion':lines+=['Optional emotion candidate: '+n['canonical_name'] for n in emos]
 if task=='polarity':lines.append('Judge polarity directly from original evidence; discrete emotion candidates do not determine valence.')
 if task=='open_vocabulary':lines.append('Use unrestricted emotion vocabulary. The graph does not define the allowed answers; absent candidates do not imply absent emotions.')
 return '\n'.join(lines)
