"""One production evidence format, task-independent; only immutable graph evidence is serialized."""
import itertools,math
import numpy as np
from .common import *
STATE_NAMES={'AGR_RELEVANT':'Relevant','AGR_IRRELEVANT':'Irrelevant','AGC_CONGRUENT':'Congruent','AGC_INCONGRUENT':'Incongruent','AGC_MIXED':'Mixed','AEX_EXPECTED':'Expected','AEX_UNEXPECTED':'Unexpected','AAG_SELF':'Self','AAG_OTHER':'Other','AAG_CIRCUMSTANCE':'Circumstance','AAG_SHARED':'Shared','ACT_CERTAIN':'Certain','ACT_UNCERTAIN':'Uncertain','ACP_HIGH':'High','ACP_LOW':'Low','ACP_MIXED':'Mixed'}
DIMENSION_NAMES={'APP_GOAL_RELEVANCE':'Goal Relevance','APP_GOAL_CONGRUENCE':'Goal Congruence','APP_EXPECTEDNESS':'Expectedness','APP_AGENCY':'Agency','APP_CERTAINTY':'Certainty','APP_COPING_POTENTIAL':'Coping Potential'}

def minimum_relation_subset(contributions,candidates,absolute_threshold=.9,positive_threshold=.9):
 values=np.asarray(contributions,float);den_abs=float(np.abs(values).sum());den_pos=float(np.maximum(values,0).sum());ordered=sorted(candidates,key=lambda j:(-abs(values[j]),j))
 if den_abs<=0 or den_pos<=0:return None
 for k in range(1,len(ordered)+1):
  for subset in itertools.combinations(ordered,k):
   a=float(np.abs(values[list(subset)]).sum());p=float(np.maximum(values[list(subset)],0).sum())
   if a/den_abs+1e-14>=absolute_threshold and p/den_pos+1e-14>=positive_threshold and p>0:return dict(indices=list(subset),minimum_edge_count=k,absolute_coverage=a/den_abs,positive_coverage=p/den_pos,total_absolute_contribution=den_abs,total_positive_contribution=den_pos,selected_absolute_contribution=a,selected_positive_contribution=p)
 return None

class UnifiedAMGPromptAdapter:
 def __init__(self,tokenizer,graph_release=GRAPH_RELEASE,policy_dir=ROOT):
  self.tokenizer=tokenizer;self.graph_release=Path(graph_release);self.policy_dir=Path(policy_dir);self.config=read(self.policy_dir/'config.json');self.instructions=(self.policy_dir/'instructions.txt').read_text().strip();self.descriptions=read(self.policy_dir/'cue_descriptions.json')['descriptions'];self.manifest=read(self.graph_release/'release_manifest.json');self.ontology=read(self.graph_release/'ontology/index.json');self.model=dict(np.load(self.graph_release/'learned_relations/G1.npz'));self.admission=read(self.graph_release/'admission/cue_admission_policy.json');self.cue_ids=self.ontology['cue_ids'];self.emotion_ids=self.ontology['emotion_ids'];self.states=self.ontology['states'];self.emotion_names=dict(zip(self.emotion_ids,self.ontology['emotion_names']));self.state_dims={n['id']:n['dimension_id'] for n in read(self.graph_release/'ontology/appraisal_states.json')};self.stable={};self.edges={}
  if self.manifest['release_id']!=self.config['graph_release_id']:raise ValueError('Wrong frozen graph release')
  if set(self.descriptions)!=set(self.cue_ids):raise ValueError('Descriptions must cover exactly the frozen 42 Cue IDs')
  for typ,cols in [('CA',16),('CE',188)]:
   self.stable[typ]=np.zeros((42,cols),bool)
  for e in read(self.graph_release/'graph.json')['edges']:
   if e['relation_type'] in self.stable:
    typ=e['relation_type'];self.stable[typ][e['source_index'],e['target_index']]=True;self.edges[(typ,e['source_index'],e['target_index'])]=e
 def tokens(self,text):return len(self.tokenizer.encode(text,add_special_tokens=False))
 def _validate(self,g):
  if g['schema_version']!='amg_sample_graph_v2_1' or g['graph_release_id']!=self.manifest['release_id']:raise ValueError('Sample graph schema/release mismatch')
  signals=g['cue_signals']
  if [s['cue_type_id'] for s in signals]!=self.cue_ids:raise ValueError('CueSignal order mismatch')
  q=np.array([s['model_input'] for s in signals],float)
  if not np.isfinite(q).all():raise ValueError('Non-finite model input')
  for typ,targets in [('CA',self.states),('CE',self.emotion_ids)]:
   ledger=g['relation_contributions'][typ];mat=np.array(ledger['contributions'],float)
   if ledger['cue_id_order']!=self.cue_ids or ledger['target_id_order']!=targets or mat.shape!=(42,len(targets)):raise ValueError('Contribution axes mismatch')
   if not np.array_equal(np.array(ledger['stable_global_edge_mask'],bool),self.stable[typ]):raise ValueError('Stable relation mask mismatch')
   if not np.allclose(mat,q[:,None]*self.model[typ],atol=1e-12,rtol=1e-12):raise ValueError('Contributions do not equal raw model input times frozen W')
   if not np.allclose(mat.sum(0)+self.model[typ+'_bias'],ledger['logits'],atol=1e-10,rtol=1e-12):raise ValueError('Contribution logit closure failed')
  formal=[n for n in g['nodes'] if n['node_type']=='CueEvidence'];seen=set()
  for n in formal:
   cue=n['ontology_id'];j=self.cue_ids.index(cue);score=n.get('source_calibrated_score');te=self.admission['cues'][j]['evidence']['threshold']
   if cue in seen or n.get('admission_status')!='evidence_active' or g['cue_audit'][j]['admission_status']!='evidence_active' or not g['masks']['evidence'][j]:raise ValueError('Only unique formal Evidence Cue nodes are allowed')
   if score is None or not np.isfinite(score) or not 0<=score<=1 or te is None or score+1e-12<te:raise ValueError('Invalid calibrated Evidence score')
   if not math.isclose(n['raw_score'],q[j],abs_tol=1e-12):raise ValueError('Raw Cue/model input mismatch')
   seen.add(cue)
  dimensions=[n['dimension_id'] for n in g['nodes'] if n['node_type']=='AppraisalEvidence']
  if len(dimensions)!=len(set(dimensions)):raise ValueError('Conflicting formal states in one appraisal dimension')
  return formal
 def _blocks(self,g,cues,features):
  if not features['nodes']:return [],[]
  selected={self.cue_ids.index(n['ontology_id']) for n in cues};blocks=[];rejected=[];targets=[n for n in g['nodes'] if n['node_type']=='AppraisalEvidence'];emotion=sorted((n for n in g['nodes'] if n['node_type']=='EmotionEvidence'),key=lambda n:(-n['score'],n['ontology_id']))[:self.config['emotion_limit']];targets+=emotion;local={e['global_edge_id']:e for e in g['edges'] if 'global_edge_id' in e}
  for n in targets:
   typ='CA' if n['node_type']=='AppraisalEvidence' else 'CE';target=n['ontology_id'];k=self.states.index(target) if typ=='CA' else self.emotion_ids.index(target)
   if n.get('support_status')!='evidence_supported':rejected.append(dict(target_id=target,reason='not_formal_evidence_supported'));continue
   values=np.array(g['relation_contributions'][typ]['contributions'])[:,k];possible=[]
   for j in sorted(selected):
    key=(typ,j,k)
    if key not in self.edges:continue
    edge=self.edges[key];le=local.get(edge['edge_id'])
    if le is None or le['target']!=n['instance_id']:continue
    if not math.isclose(le['contribution'],values[j],rel_tol=1e-12,abs_tol=1e-12):raise ValueError('Sample edge and contribution ledger disagree')
    if abs(values[j])>1e-15:possible.append(j)
   subset=minimum_relation_subset(values,possible,self.config['minimum_absolute_coverage'],self.config['minimum_positive_coverage'])
   if subset is None:rejected.append(dict(target_id=target,relation_type=typ,reason='actual_Prompt_Cue_and_stable_edges_cannot_cover_90_percent'));continue
   relations=[]
   for j in subset['indices']:
    edge=self.edges[(typ,j,k)];relations.append(dict(cue_id=self.cue_ids[j],cue_index=j,target_id=target,relation_type=typ,global_edge_id=edge['edge_id'],contribution=float(values[j]),weight=float(edge['weight']),raw_score=float(g['cue_signals'][j]['model_input']),sample_edge_id=local[edge['edge_id']]['edge_id']))
   label=DIMENSION_NAMES[self.state_dims[target]]+' / '+STATE_NAMES[target] if typ=='CA' else self.emotion_names[target]
   blocks.append(dict(relation_type=typ,target_id=target,target_instance_id=n['instance_id'],label=label,relations=relations,coverage=subset,priority=sum(abs(r['contribution']) for r in relations)))
  blocks.sort(key=lambda b:(b['relation_type'],b['target_id']));return blocks,rejected
 def _render(self,cues,blocks,features):
  if not cues:return ''
  lines=[self.instructions,'','[AMG EVIDENCE — AUXILIARY]','Cue scores (source-domain calibrated detector scores):' if features['score'] else 'Observable Cue evidence:']
  for n in cues:
   cue=n['ontology_id'];line='- ['+n['modality'].title()+'] '+cue
   if features['score']:line+=' | score='+format(n['source_calibrated_score'],'.'+str(self.config['score_decimals'])+'f')
   if features['description']:line+=' | '+self.descriptions[cue]
   lines.append(line)
  for typ,heading in [('CA','CA: Cue → Appraisal'),('CE','CE: Cue → Emotion')]:
   portion=[b for b in blocks if b['relation_type']==typ]
   if not portion:continue
   lines+=['',heading]
   for b in portion:
    lines.append('- Hypothesis: '+b['label'])
    if features['contribution'] or features['weight']:
     for r in b['relations']:
      line='  - '+r['cue_id']+':'
      if features['contribution']:line+=' C='+format(r['contribution'],'+.'+str(self.config['contribution_significant_digits'])+'g')
      if features['weight']:line+=' W='+format(r['weight'],'+.'+str(self.config['contribution_significant_digits'])+'g')
      lines.append(line)
  lines+=['','[END OF AMG EVIDENCE]'];return '\n'.join(lines)
 def _build(self,g,features,evidence_token_budget=None,full_prompt_counter=None,prompt_token_budget=None):
  formal=self._validate(g);ranked=sorted(formal,key=lambda n:(-n['source_calibrated_score'],n['ontology_id']));budget=self.config['evidence_token_budget'] if evidence_token_budget is None else int(evidence_token_budget);attempts=[];rejections=[];initial_targets=[]
  if full_prompt_counter is not None and prompt_token_budget is not None and full_prompt_counter('')>prompt_token_budget:raise ValueError('Original input already exceeds context budget; original input was not truncated')
  for k in range(min(len(ranked),self.config['cue_limit']),0,-1):
   cues=ranked[:k];blocks,rejected=self._blocks(g,cues,features);rejections+=rejected
   if not initial_targets:initial_targets=[b['target_id'] for b in blocks]
   while True:
    text=self._render(cues,blocks,features);nt=self.tokens(text);fulltokens=full_prompt_counter(text) if full_prompt_counter else None;fits=nt<=budget and (fulltokens is None or prompt_token_budget is None or fulltokens<=prompt_token_budget);attempts.append(dict(cue_count=k,targets=[b['target_id'] for b in blocks],evidence_tokens=nt,full_prompt_tokens=fulltokens,fits=fits))
    if fits:return self._packet(g,text,cues,blocks,features,attempts,rejections,initial_targets,nt,fulltokens,None)
    if blocks:
     dropped=min(blocks,key=lambda b:(b['priority'],b['relation_type'],b['target_id']));blocks=[b for b in blocks if b is not dropped];rejections.append(dict(target_id=dropped['target_id'],reason='complete_hypothesis_block_dropped_to_preserve_Cue_fields_and_context'))
    else:break
  reason='no_formal_CueEvidence' if not ranked else 'AMG_budget_too_small_original_input_preserved';return self._packet(g,'',[],[],features,attempts,rejections,initial_targets,0,full_prompt_counter('') if full_prompt_counter else None,reason)
 def _packet(self,g,text,cues,blocks,features,attempts,rejections,initial_targets,nt,fulltokens,reason):
  pm=[c in {n['ontology_id'] for n in cues} for c in self.cue_ids];return dict(schema_version='amg_unified_prompt_packet_v1',sample_id=g['sample_id'],graph_release_id=g['graph_release_id'],text=text,audit=dict(task_independent=True,default_condition='P4',features=features,source_sample_graph_sha256=digest(g),fixed_instruction_sha256=digest(self.instructions),description_mapping_sha256=digest(self.descriptions),cue_ids=[n['ontology_id'] for n in cues],cue_instance_ids=[n['instance_id'] for n in cues],cue_source_calibrated_scores=[float(n['source_calibrated_score']) for n in cues],source_score_semantics='source-domain calibrated detector score, not emotion probability',blocks=blocks,rejected_or_dropped_targets=rejections,prompt_cue_mask=pm,selected_global_edge_ids=[r['global_edge_id'] for b in blocks for r in b['relations']] if features['contribution'] or features['weight'] else [],relation_support_edge_ids=[r['global_edge_id'] for b in blocks for r in b['relations']],selected_target_instance_ids=[b['target_instance_id'] for b in blocks],CA_edge_count=sum(len(b['relations']) for b in blocks if b['relation_type']=='CA') if features['contribution'] or features['weight'] else 0,CE_edge_count=sum(len(b['relations']) for b in blocks if b['relation_type']=='CE') if features['contribution'] or features['weight'] else 0,evidence_tokens=nt,full_prompt_tokens=fulltokens,budget_attempts=attempts,fallback=reason is not None,fallback_reason=reason,candidate_cue_count=0,deferred_cue_count=0,AE_edge_count=0,contribution_source='Frozen ledger raw_score times global_weight; source_calibrated_score is never multiplied by W',contribution_coverage_scope='All Cue contribution terms, excluding bias; selected relation subset must cover both absolute and positive mass',Student_changed=False,G1_changed=False,calibration_changed=False,threshold_changed=False))
 def build(self,sample_graph,*,evidence_token_budget=None,full_prompt_counter=None,prompt_token_budget=None):
  return self._build(sample_graph,dict(description=True,score=True,nodes=True,contribution=True,weight=False),evidence_token_budget,full_prompt_counter,prompt_token_budget)

class PromptAblations:
 """Offline experiment helper; production build() has no task/mode/condition branch."""
 FEATURES={'P1':dict(description=True,score=False,nodes=False,contribution=False,weight=False),'P2':dict(description=True,score=True,nodes=False,contribution=False,weight=False),'P3':dict(description=True,score=True,nodes=True,contribution=False,weight=False),'P4':dict(description=True,score=True,nodes=True,contribution=True,weight=False),'P5':dict(description=True,score=True,nodes=True,contribution=True,weight=True),'Score-A':dict(description=False,score=False,nodes=False,contribution=False,weight=False),'Score-B':dict(description=False,score=True,nodes=False,contribution=False,weight=False),'Score-C':dict(description=True,score=True,nodes=False,contribution=False,weight=False),'W-only':dict(description=True,score=True,nodes=True,contribution=False,weight=True)}
 def __init__(self,adapter):self.adapter=adapter
 def build(self,sample_graph,condition,**budget):
  if condition not in self.FEATURES:raise ValueError('Unknown offline ablation condition')
  packet=self.adapter._build(sample_graph,self.FEATURES[condition],**budget);packet['audit']['experimental_condition']=condition;return packet
