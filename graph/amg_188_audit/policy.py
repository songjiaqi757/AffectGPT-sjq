
import copy
from .common import CONDITIONS,canonical,require
from amg_d_multistart10.policy import gate,readable,format_evidence as original_format
from amg_finetune_nogc.prompts import encode,clean_text,trim_text,SPECIAL_MARKERS
def freeze(evidence,tokenizer):
 original,original_info=original_format(evidence,tokenizer,512,"D")
 require(original_info["omitted_evidence"]==0,"Unexpected original pruning: cannot isolate field deletion")
 level=original_info["evidence_level"];reasons=original_info["gate_reasons"]
 cues=[readable(c["cue_id"]) for c in evidence["query_cues"]] if level else []
 apps=[readable(d["dimension_id"])+": "+readable(s["state_id"]) for d in evidence["appraisal_dimensions"] for s in d["display_candidates"]] if level>=2 else []
 emos=[e["canonical_name"] for e in evidence["emotion_candidates"]] if level>=3 else []
 texts={};infos={}
 for c in CONDITIONS:
  lines=[]
  if c!="A" and cues:
   lines=["Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.","Observed cues: "+"; ".join(cues)]
   if c in ["C","E"] and apps:lines.append("Appraisal hypotheses: "+"; ".join(apps))
   if c in ["D","E"] and emos:lines.append("Emotion hypotheses: "+", ".join(emos))
   if "mixed_text_affect_or_evaluation" in reasons:lines.append("Text contains mixed affect; overall polarity is unresolved.")
  text=original if c=="P" else "\n".join(lines)
  require(len(encode(tokenizer,text))<=512,"Evidence exceeds budget")
  info=copy.deepcopy(original_info)
  info.update(ablation=c,ablation_description=CONDITIONS[c],gate_frozen=True,fallback=not bool(text),graph_tokens=len(encode(tokenizer,text)),displayed_paths=original_info["displayed_paths"] if c=="P" else 0,
    cues_displayed=len(cues) if text else 0,appraisals_displayed=len(apps) if c in ["C","E","P"] and text else 0,emotion_candidates_displayed=len(emos) if c in ["D","E","P"] and text else 0,graph_text_id=canonical(text))
  texts[c]=text;infos[c]=info
 return dict(sample_id=evidence["sample_id"],source_graph_release_id=evidence["graph_release_id"],source_query_result_id=evidence["query_result_id"],source_gate_level=level,texts=texts,infos=infos)
def make_prompt(reader,chat,row,evidence,p):
 c=p["ablation_by_variant"][p["variant"]];t=chat.tokenizer
 subtitle,truncated=trim_text(t,clean_text(row["subtitle"]),p["limits"]["subtitle_token_budget"])
 text=evidence["texts"][c];info=copy.deepcopy(evidence["infos"][c])
 prompt=reader.get_prompt_for_multimodal("multiface_audio_face_text",subtitle,p["prompt_question"]+("\n"+text if text else ""))
 ids=encode(t,chat.replace_token_for_multimodal(prompt))
 require(len(ids)<=p["limits"]["prompt_token_budget"],"Prompt truncation")
 require(len(ids)+p["generation"]["max_new_tokens"]<=p["generation"]["max_length"],"Context truncation")
 for marker,expected in zip(SPECIAL_MARKERS,[0,1,0,1,1]):require(prompt.count(marker)==expected,"Media marker drift")
 info.update(prompt_tokens=len(ids),subtitle_truncated=truncated,prompt_id=canonical(prompt))
 if c in evidence.get("expected_prompt_ids",{}):require(info["prompt_id"]==evidence["expected_prompt_ids"][c],"CPU/GPU prompt mismatch")
 return prompt,info
