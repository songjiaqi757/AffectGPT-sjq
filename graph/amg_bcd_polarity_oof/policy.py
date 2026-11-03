"""Frozen, task-agnostic evidence levels. No target labels or model answers."""
import copy,re
from amg_runtime.common import canonical,require
from amg_finetune_nogc.prompts import encode,clean_text,trim_text,SPECIAL_MARKERS
POLICY=dict(version="bcd_polarity_oof_evidence_v1",graph_token_budget=512,target_tokens=384,max_paths=2,
 min_selected_cues=2,min_candidate_coverage=.35,min_relative_candidate_gap=.10,
 min_candidate_support_cues=2,dropout_none=.50,dropout_no_emotions=.0,
 scores_are_calibrated_probabilities=False,threshold_selection="fixed engineering preset; no target tuning")
def readable(value):
 return value.replace("TXT_","Text: ").replace("AUD_","Audio: ").replace("VIS_","Visual: ").replace("APP_","").replace("_"," ").lower()
def gate(evidence,variant,dropout=None):
 cues=evidence.get("query_cues",[]);emotions=evidence.get("emotion_candidates",[])
 reason=[];level=3
 if not cues:return 0,["no_available_selected_cues"]
 if len(cues)<POLICY["min_selected_cues"] or not emotions:level=1;reason.append("weak_or_absent_graph_support")
 else:
  first=emotions[0];s1=first["association_score"];s2=emotions[1]["association_score"] if len(emotions)>1 else 0
  gap=(s1-s2)/max(abs(s1),1e-12)
  supporters={r["cue_id"] for r in evidence.get("explanation_paths",[]) if r["emotion_id"]==first["emotion_id"]}
  if first["query_coverage"]<POLICY["min_candidate_coverage"] or gap<POLICY["min_relative_candidate_gap"] or len(supporters)<POLICY["min_candidate_support_cues"]:
   level=2;reason.append("emotion_support_not_separated")
  selected={c["cue_id"] for c in cues}
  if any(a in selected and b in selected for a,b in [("TXT_EVALUATION_POSITIVE","TXT_EVALUATION_NEGATIVE"),("TXT_AFFECT_WORD_POSITIVE","TXT_AFFECT_WORD_NEGATIVE")]):
   level=min(level,2);reason.append("mixed_text_affect_or_evaluation")
  if not any(d["display_candidates"] for d in evidence.get("appraisal_dimensions",[])) and level==2:
   level=1;reason.append("no_supported_appraisal")
 if dropout is not None:
  if dropout<POLICY["dropout_none"]:level=0;reason.append("training_evidence_dropout")
  elif dropout<POLICY["dropout_none"]+POLICY["dropout_no_emotions"]:
   level=min(level,2);reason.append("training_emotion_dropout")
 return level,reason or ["supported_full_evidence"]
def format_evidence(evidence,tokenizer,budget,variant="B",dropout=None):
 level,reasons=gate(evidence,variant,dropout)
 info=dict(fallback=level==0,evidence_level=level,gate_reasons=reasons,policy_id=canonical(POLICY),graph_tokens=0,omitted_evidence=0,displayed_paths=0)
 if level==0:return "",info
 budget=min(budget,POLICY["graph_token_budget"])
 cues=[readable(c["cue_id"]) for c in evidence["query_cues"]]
 apps=[]
 if level>=2:
  for d in evidence["appraisal_dimensions"]:
   for s in d["display_candidates"]:
    apps.append(readable(d["dimension_id"])+": "+readable(s["state_id"]))
 emos=[x["canonical_name"] for x in evidence["emotion_candidates"]] if level>=3 else []
 names={x["emotion_id"]:x["canonical_name"] for x in evidence["emotion_candidates"]}
 paths=[]
 if level>=3:
  for p in evidence["explanation_paths"][:POLICY["max_paths"]]:
   seq=[readable(p["cue_id"])]
   if "appraisal_state_id" in p:seq.append(readable(p["appraisal_state_id"]))
   seq.append(names[p["emotion_id"]]);paths.append(" -> ".join(seq))
 def render():
  parts=["Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them."]
  if cues:parts+=["Observed cues: "+"; ".join(cues)]
  if apps:parts+=["Appraisal hypotheses: "+"; ".join(apps)]
  if emos:parts+=["Emotion hypotheses: "+", ".join(emos)]
  if paths:parts+=["Supporting links: "+"; ".join(paths)]
  if "mixed_text_affect_or_evaluation" in reasons:parts+=["Text contains mixed affect; overall polarity is unresolved."]
  return "\n".join(parts)
 text=render()
 # Remove redundant paths first; preserve cues rather than unsupported conclusions.
 while len(encode(tokenizer,text))>budget:
  if paths:paths.pop()
  elif len(apps)>6:apps.pop()
  elif emos:emos.pop()
  elif apps:apps.pop()
  elif cues:cues.pop()
  else:raise ValueError("Evidence budget too small")
  info["omitted_evidence"]+=1;text=render()
 info.update(graph_tokens=len(encode(tokenizer,text)),displayed_paths=len(paths),emotion_candidates_displayed=len(emos),cues_displayed=len(cues),appraisals_displayed=len(apps))
 return text,info
def make_tokens(dataset,sample,evidence,label_type,limits,variant,dropout=None):
 t=dataset.tokenizer;qa=dataset.get_qa_pairs(dataset.dataset,label_type,sample)
 subtitle,truncated=trim_text(t,clean_text(sample["subtitle"]),limits["subtitle_token_budget"])
 graph,info=format_evidence(evidence,t,limits["graph_token_budget"],variant,dropout)
 prompt=dataset.replace_token_for_multimodal(dataset.get_prompt_for_multimodal(dataset.face_or_frame,subtitle,qa["question"]+("\n"+graph if graph else "")))
 prompt_ids=encode(t,prompt);require(len(prompt_ids)<=limits["prompt_token_budget"],"Compact prompt budget exceeded")
 end=encode(t,"###");raw=encode(t,clean_text(qa["answer"]));limit=limits["answer_token_budget"]-len(end);target=raw[:limit]+end
 info.update(prompt_tokens=len(prompt_ids),answer_tokens=len(target),answer_truncated=len(raw)>limit,subtitle_truncated=truncated,label_type=label_type)
 return prompt_ids,target,prompt,info
def make_prompt(reader,chat,row,evidence,p):
 t=chat.tokenizer;limits=p["limits"]
 subtitle,truncated=trim_text(t,clean_text(row["subtitle"]),limits["subtitle_token_budget"])
 graph,info=format_evidence(evidence,t,limits["graph_token_budget"],p["variant"])
 prompt=reader.get_prompt_for_multimodal("multiface_audio_face_text",subtitle,p["prompt_question"]+("\n"+graph if graph else ""))
 ids=encode(t,chat.replace_token_for_multimodal(prompt))
 require(len(ids)<=limits["prompt_token_budget"],"Inference compact prompt exceeds fixed budget")
 require(len(ids)+p["generation"]["max_new_tokens"]<=p["generation"]["max_length"],"Context would be truncated")
 for marker,expected in zip(SPECIAL_MARKERS,[0,1,0,1,1]):require(prompt.count(marker)==expected,"Multimodal marker changed")
 info.update(prompt_tokens=len(ids),subtitle_truncated=truncated,prompt_id=canonical(prompt));return prompt,info
