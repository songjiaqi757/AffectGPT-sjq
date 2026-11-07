import copy,collections
import numpy as np
from amg_runtime.common import canonical,require
from amg_finetune_nogc.prompts import encode,clean_text
POLICY=dict(version="v21_P4_compact_gate_graph_oof_v1",graph_token_budget=512,min_selected_cues=2,min_candidate_coverage=.35,min_relative_candidate_gap=.10,min_candidate_support_cues=2,dropout_none=.20,dropout_no_emotions=.20,threshold_selection="Fixed historical D settings, no target tuning")
def gate(g):
 cues=[n for n in g["nodes"] if n["node_type"]=="CueEvidence"];apps=[n for n in g["nodes"] if n["node_type"]=="AppraisalEvidence"];emos=sorted([n for n in g["nodes"] if n["node_type"]=="EmotionEvidence"],key=lambda n:-n["score"])
 if not cues:return 0,["no_formal_v21_CueEvidence"]
 if len(cues)<2 or not emos:return 1,["weak_or_absent_graph_support"]
 first=emos[0];s1=first["score"];s2=emos[1]["score"] if len(emos)>1 else 0
 level=3;reasons=[]
 if first["evidence_coverage"]<.35 or (s1-s2)/max(abs(s1),1e-12)<.10 or len(set(first["supporting_cues"]))<2:level=2;reasons.append("emotion_support_not_separated")
 active={n["ontology_id"] for n in cues}
 if any({a,b}<=active for a,b in [("TXT_EVALUATION_POSITIVE","TXT_EVALUATION_NEGATIVE"),("TXT_AFFECT_WORD_POSITIVE","TXT_AFFECT_WORD_NEGATIVE")]):level=min(level,2);reasons.append("mixed_text_affect_or_evaluation")
 if level==2 and not apps:level=1;reasons.append("no_supported_appraisal")
 return level,reasons or ["supported_full_evidence"]
def restricted_graph(g,level):
 x=dict(g);x["nodes"]=[n for n in g["nodes"] if n["node_type"]=="CueEvidence" or (level>=2 and n["node_type"]=="AppraisalEvidence") or (level>=3 and n["node_type"]=="EmotionEvidence")]
 keep={n["instance_id"] for n in x["nodes"]};x["edges"]=[e for e in g["edges"] if e["source"] in keep and (e.get("target_scope")=="ontology" or e["target"] in keep)]
 return x
def make_tokens(dataset,sample,item,label_type,limits,dropout=None):
 qa=dataset.get_qa_pairs(dataset.dataset,label_type,sample)
 level=item["level"];reasons=list(item["gate_reasons"])
 if dropout is not None:
  if dropout<.20:level=0;reasons.append("training_evidence_dropout")
  elif dropout<.40:level=min(level,2);reasons.append("training_emotion_dropout")
 choice=item["levels"].get(str(level),dict(text="",graph_tokens=0,fallback=True,CA_edge_count=0,CE_edge_count=0))
 text=choice["text"];subtitle=clean_text(sample["subtitle"])
 prompt=dataset.replace_token_for_multimodal(dataset.get_prompt_for_multimodal(dataset.face_or_frame,subtitle,qa["question"]+("\n\n"+text if text else "")))
 ids=encode(dataset.tokenizer,prompt);require(len(ids)<=limits["prompt_token_budget"],"Original input/P4 exceeds fixed context")
 end=encode(dataset.tokenizer,"###");raw=encode(dataset.tokenizer,clean_text(qa["answer"]));limit=limits["answer_token_budget"]-len(end);target=raw[:limit]+end
 info=dict(fallback=not bool(text),evidence_level=level if text else 0,gate_reasons=reasons,graph_tokens=choice["graph_tokens"],prompt_tokens=len(ids),answer_tokens=len(target),answer_truncated=len(raw)>limit,subtitle_truncated=False,label_type=label_type,fold=item["fold"],fold_graph_id=item["fold_graph_id"],CA_edge_count=choice["CA_edge_count"],CE_edge_count=choice["CE_edge_count"],original_subtitle_preserved=True)
 return ids,target,prompt,info
