"""CPU contract and data-faithfulness checks; this does not claim paired model generation."""
import copy,inspect,itertools,json,re
import numpy as np
from .common import *
from .adapter import UnifiedAMGPromptAdapter,minimum_relation_subset,PromptAblations
from .integration import AffectGPTUnifiedBridge,OriginalInputOverBudget
from .tokenization import MARKERS

def validate(adapter,reader,chat,graphs,rows):
 from ..v21.runtime import SampleGraphV21
 checks={};bridge=AffectGPTUnifiedBridge(adapter);question="Please infer the person's emotional state and provide your reasoning process.";names=inspect.signature(adapter.build).parameters;checks['production_API_has_no_task_mode_condition']=not({'task','mode','condition'}&set(names));checks['fixed_instruction_80_to_110_words']=80<=len(adapter.instructions.split())<=110;checks['all_42_frozen_Cue_descriptions']=set(adapter.descriptions)==set(adapter.cue_ids);checks['AE_disabled']=adapter.config['AE_enabled'] is False
 examples=[g for g in graphs if any(n['node_type']=='CueEvidence' for n in g['nodes'])];g=examples[0];packet=adapter.build(g);checks['P4_transmits_calibrated_scores_and_descriptions']=all(('score='+format(s,'.2f')) in packet['text'] for s in packet['audit']['cue_source_calibrated_scores']) and all(adapter.descriptions[c] in packet['text'] for c in packet['audit']['cue_ids']);checks['P4_omits_raw_score_and_global_W']='raw_score=' not in packet['text'] and ' W=' not in packet['text'];checks['build_does_not_mutate_sample_graph']=digest(g)==packet['audit']['source_sample_graph_sha256'];checks['deterministic_production_text']=adapter.build(g)==adapter.build(g)
 subset=minimum_relation_subset(np.array([-.20,.45,.35]+[0.]*39),[0,1,2]);checks['minimal_subset_preserves_required_negative_contribution']=subset['minimum_edge_count']==3 and 0 in subset['indices'];checks['hidden_unselected_contributions_prevent_false_support']=minimum_relation_subset(np.array([.1,.9]+[0.]*40),[0]) is None;checks['zero_positive_mass_never_supports_hypothesis']=minimum_relation_subset(np.array([-.5,-.5]+[0.]*40),[0,1]) is None
 full_nodes=0;negative=0;different_from_calibrated_product=False;all_serialized_edges=0
 for graph in graphs:
  p=adapter.build(graph);pm=p['audit']['prompt_cue_mask'];formal={n['ontology_id'] for n in graph['nodes'] if n['node_type']=='CueEvidence'};visible=set(p['audit']['cue_ids']);assert visible<=formal and len(visible)<=8;tokens=set(re.findall(r'(?:TXT|AUD|VIS)_[A-Z_]+',p['text']));assert tokens==visible;assert not any(n['cue_type_id'] in visible for n in graph['candidate_cues']);assert p['audit']['candidate_cue_count']==0
  for b in p['audit']['blocks']:
   full_nodes+=1;typ=b['relation_type'];target=b['target_id'];k=adapter.states.index(target) if typ=='CA' else adapter.emotion_ids.index(target);mat=np.array(graph['relation_contributions'][typ]['contributions']);idx=[r['cue_index'] for r in b['relations']];assert all(pm[j] for j in idx);assert b['coverage']['absolute_coverage']>=.9-1e-12 and b['coverage']['positive_coverage']>=.9-1e-12
   assert b['coverage']['minimum_edge_count']==len(idx)
   for r in b['relations']:
    all_serialized_edges+=1;j=r['cue_index'];assert adapter.stable[typ][j,k] and r['global_edge_id']==adapter.edges[(typ,j,k)]['edge_id'];assert abs(r['contribution']-mat[j,k])<1e-12;assert abs(r['contribution']-graph['cue_signals'][j]['model_input']*adapter.model[typ][j,k])<1e-12;score=next(n['source_calibrated_score'] for n in graph['nodes'] if n.get('ontology_id')==r['cue_id']);different_from_calibrated_product|=abs(score*r['weight']-r['contribution'])>1e-6;negative+=int(r['contribution']<0);assert ('C='+format(r['contribution'],'+.4g')) in p['text']
  # Same AMG content across different task questions, with room for the full evidence.
  subtitle=rows[graph['sample_id']]['text']['english'];questions=[question,"Please recognize the character's most likely emotional state.","Please select the most likely sentiment label that can best describe the person's emotional state: positive, negative, neutral."]
  prepared=[bridge.prepare(reader,chat,graph,q,subtitle) for q in questions];assert len({p['evidence']['text'] for p in prepared})==1
  for q,prep in zip(questions,prepared):
   assert prep['question']==q+('\n\n'+prep['evidence']['text'] if prep['evidence']['text'] else '');assert '<Subtitle>'+subtitle+'</Subtitle>' in prep['prompt'];assert prep['evidence']['audit']['full_prompt_tokens']+512<=2048;assert not prep['evidence']['audit']['left_truncation_required'];assert all(prep['prompt'].count(m)==prep['baseline_prompt'].count(m) for m in MARKERS)
 checks.update(Candidate_Deferred_and_hidden_Cues_not_serialized=True,formal_Cue_top8_only=True,only_formal_evidence_supported_targets=True,actual_selected_edges_recheck_both_90_percent=True,ledger_C_exact_and_signed=True,raw_not_calibrated_score_used_for_C=different_from_calibrated_product,stable_global_edges_only=True,uniform_AMG_text_across_task_questions=True,original_questions_preserved=True,original_subtitles_preserved=True,multimodal_markers_unchanged=True,total_context_and_generation_budget_checked=True)
 # Direct CE structure is emitted equally for every task; no polarity/open-vocabulary branch.
 ce_graph=next((x for x in graphs if any(b['relation_type']=='CE' for b in adapter.build(x)['audit']['blocks'])),None);checks['CE_unified_for_all_tasks']=ce_graph is not None
 if ce_graph is not None:
  text=adapter.build(ce_graph)['text'];assert '\nCE: Cue → Emotion' in text
 cueonly=next(x for x in graphs if not any(n['node_type'] in ('AppraisalEvidence','EmotionEvidence') for n in x['nodes']));t=adapter.build(cueonly)['text'];checks['Cue_only_has_no_fake_empty_CA_CE_sections']='\nCA:' not in t and '\nCE:' not in t
 empty=SampleGraphV21(adapter.graph_release).build('empty_test',[None]*42);e=bridge.prepare(reader,chat,empty,question,'Original subtitle.');checks['no_formal_Cue_exact_original_fallback']=e['prompt']==e['baseline_prompt'] and e['evidence']['text']==''
 tiny=bridge.prepare(reader,chat,g,question,'Original subtitle.',evidence_token_budget=1);checks['too_small_AMG_budget_preserves_original']=tiny['prompt']==tiny['baseline_prompt'] and tiny['evidence']['audit']['fallback']
 try:bridge.prepare(reader,chat,g,question,'Unchanged subtitle. '*5000);checks['oversized_original_input_not_silently_truncated']=False
 except OriginalInputOverBudget:checks['oversized_original_input_not_silently_truncated']=True
 # Budget-driven Cue reduction must repeat support gating, never trim a relation fragment.
 limited=adapter.build(g,evidence_token_budget=max(1,packet['audit']['evidence_tokens']-50));checks['budget_output_always_complete_or_empty']=not limited['text'] or limited['text'].endswith('[END OF AMG EVIDENCE]')
 expanded=copy.copy(chat);expanded.num_video_query_token=8;expanded.num_audio_query_token=16;expanded.num_multi_query_token=32;prep=bridge.prepare(reader,expanded,g,question,'Original subtitle.');direct=len(chat.tokenizer.encode(expanded.replace_token_for_multimodal(prep['prompt']),add_special_tokens=False));checks['multimodal_expansion_counted_by_real_tokenizer']=direct==prep['evidence']['audit']['full_prompt_tokens'] and direct>len(chat.tokenizer.encode(prep['prompt'],add_special_tokens=False))
 class RecordingChat:
  def __init__(self,actual):self.tokenizer=actual.tokenizer;self.replace_token_for_multimodal=actual.replace_token_for_multimodal;self.call=None
  def answer_sample(self,prompt,img_list,**generation):self.call=(prompt,img_list,generation);return 'CONTRACT_TEST_ONLY_NO_MODEL_GENERATION'
 recorded=RecordingChat(chat);features={k:object() for k in ['audio','face','multi','frame','image']};generation=dict(max_length=2048,max_new_tokens=512,num_beams=1,temperature=1.,do_sample=False,top_p=.9);output,audit=bridge.generate_with_features(reader,recorded,g,question,'Original subtitle.',features,**generation);checks['actual_Chat_call_contract_preserves_features_and_generation']=recorded.call[1] is features and recorded.call[2]==generation and audit['original_multimodal_feature_objects_preserved']
 experimental=PromptAblations(adapter);p1=experimental.build(g,'P1');p2=experimental.build(g,'P2');p5=experimental.build(ce_graph or g,'P5');checks['ablations_are_separate_from_production']='score=' not in p1['text'] and 'score=' in p2['text'] and (' W=' in p5['text'] if p5['audit']['blocks'] else True)
 original_bad=copy.deepcopy(g);original_bad['graph_release_id']='wrong'
 try:adapter.build(original_bad);checks['wrong_release_rejected']=False
 except ValueError:checks['wrong_release_rejected']=True
 corrupt=copy.deepcopy(g);corrupt['relation_contributions']['CE']['contributions'][0][0]+=1.
 try:adapter.build(corrupt);checks['corrupted_contribution_rejected']=False
 except ValueError:checks['corrupted_contribution_rejected']=True
 checks['frozen_graph_release_unchanged']=all(sha(adapter.graph_release/name)==expected for name,expected in adapter.manifest['artifact_sha256'].items())
 result=dict(passed=all(checks.values()),checks=checks,real_source_cases=len(graphs),formal_targets_tested=full_nodes,selected_relations_tested=all_serialized_edges,negative_selected_contributions_tested=negative,actual_AffectGPT_generation_run=False,contract_test_uses_recording_chat=True,source_tokenizer_class=type(chat.tokenizer).__name__)
 assert result['passed'],result;return result
