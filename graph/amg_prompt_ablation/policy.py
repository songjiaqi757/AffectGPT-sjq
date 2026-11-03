"""Frozen prompt-field ablation. Native gate evaluated once; no graph reranking."""
import copy
from amg_runtime.common import canonical,require
from amg_d_graph_compare.policy import gate,readable
from amg_finetune_nogc.prompts import encode,clean_text,trim_text,SPECIAL_MARKERS

CONDITIONS={
 "A":"No extra evidence","B":"Cue only","C":"Cue plus Appraisal",
 "D":"Cue plus emotion candidates","E":"Cue plus Appraisal plus emotions",
 "F":"Same semantic fields as E; explicit alternatives and uncertainty"}
HEADER="Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them."

def freeze(evidence,tokenizer,budget=512):
 level,reasons=gate(evidence,"D_newgraph")
 cues=[c["cue_id"] for c in evidence.get("query_cues",[])] if level else []
 apps=[dict(dimension_id=d["dimension_id"],states=[s["state_id"] for s in d["display_candidates"]])
       for d in evidence.get("appraisal_dimensions",[]) if d["display_candidates"]] if level>=2 else []
 emotions=[dict(emotion_id=e["emotion_id"],canonical_name=e["canonical_name"]) for e in evidence.get("emotion_candidates",[])] if level>=3 else []
 original=copy.deepcopy(dict(cues=cues,apps=apps,emotions=emotions))
 mixed="mixed_text_affect_or_evaluation" in reasons
 def render(condition):
  if condition=="A" or not cues:return ""
  parts=[HEADER,"Observed cues: "+"; ".join(readable(c) for c in cues)]
  if condition in ("C","E") and apps:
   parts.append("Appraisal hypotheses: "+"; ".join(readable(a["dimension_id"])+": "+readable(s) for a in apps for s in a["states"]))
  if condition=="F" and apps:
   parts.append("Appraisal alternatives to check: "+"; ".join(readable(a["dimension_id"])+": "+
       " OR ".join(readable(s) for s in a["states"])+(" (unresolved)" if len(a["states"])>1 else " (tentative)") for a in apps))
  if condition in ("D","E") and emotions:
   parts.append("Emotion hypotheses: "+", ".join(e["canonical_name"] for e in emotions))
  if condition=="F" and emotions:
   parts.append("Tentative emotion alternatives, not confirmed labels: "+", ".join(e["canonical_name"] for e in emotions))
  if mixed:parts.append("Text contains mixed affect; overall polarity is unresolved.")
  return "\n".join(parts)
 removed=0
 while max(len(encode(tokenizer,render(c))) for c in CONDITIONS)>budget:
  multi=[a for a in apps if len(a["states"])>1]
  if multi:multi[-1]["states"].pop()
  elif emotions:emotions.pop()
  elif apps:apps.pop()
  elif cues:cues.pop()
  else:raise ValueError("Shared evidence budget cannot fit")
  removed+=1
 semantic=dict(cues=cues,apps=apps,emotions=emotions)
 texts={c:render(c) for c in CONDITIONS}
 infos={}
 for c,text in texts.items():
  infos[c]=dict(ablation=c,ablation_description=CONDITIONS[c],evidence_level=level,
   gate_reasons=reasons,gate_frozen=True,graph_tokens=len(encode(tokenizer,text)),
   omitted_evidence=removed,displayed_paths=0,fallback=not bool(text),
   cues_displayed=len(cues) if text else 0,
   appraisals_displayed=sum(len(a["states"]) for a in apps) if c in ("C","E","F") and text else 0,
   emotion_candidates_displayed=len(emotions) if c in ("D","E","F") and text else 0,
   shared_semantic_id=canonical(semantic),graph_text_id=canonical(text))
 require(infos["E"]["shared_semantic_id"]==infos["F"]["shared_semantic_id"],"Expression comparison changed content")
 return dict(sample_id=evidence["sample_id"],source_query_result_id=evidence["query_result_id"],
  source_graph_release_id=evidence["graph_release_id"],source_gate_level=level,
  original_fields=original,shared_fields=semantic,texts=texts,infos=infos)

def make_prompt(reader,chat,row,evidence,p):
 condition=p["ablation_by_variant"][p["variant"]]
 t=chat.tokenizer
 subtitle,truncated=trim_text(t,clean_text(row["subtitle"]),p["limits"]["subtitle_token_budget"])
 graph=evidence["texts"][condition];info=copy.deepcopy(evidence["infos"][condition])
 require(len(encode(t,graph))==info["graph_tokens"],"Tokenizer differs from frozen CPU prompts")
 prompt=reader.get_prompt_for_multimodal("multiface_audio_face_text",subtitle,p["prompt_question"]+("\n"+graph if graph else ""))
 ids=encode(t,chat.replace_token_for_multimodal(prompt))
 require(len(ids)<=p["limits"]["prompt_token_budget"],"Prompt would truncate")
 require(len(ids)+p["generation"]["max_new_tokens"]<=p["generation"]["max_length"],"Generation would truncate context")
 for marker,expected in zip(SPECIAL_MARKERS,[0,1,0,1,1]):
  require(prompt.count(marker)==expected,"Multimodal marker changed")
 info.update(prompt_tokens=len(ids),subtitle_truncated=truncated,prompt_id=canonical(prompt))
 if condition in evidence.get("expected_prompt_ids",{}):
  require(info["prompt_id"]==evidence["expected_prompt_ids"][condition],"GPU/CPU prompt construction mismatch")
 return prompt,info
