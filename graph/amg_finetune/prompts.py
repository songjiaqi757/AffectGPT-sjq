"""Fixed evidence serialization; budgets are independent of the supervised answer."""
import copy
SPECIAL_MARKERS=["<ImageHere>","<AudioHere>","<FrameHere>","<FaceHere>","<MultiHere>"]
DISCLAIMER="Graph scores are statistical association support, not calibrated probabilities or causal facts. Missing cues/edges do not prove absence. Treat appraisal states as hypotheses; prioritize the current audio, video and subtitle, and reject graph candidates when unsupported."
def encode(tokenizer,text):return tokenizer.encode(text,add_special_tokens=False)
def trim_text(tokenizer,text,limit):
 ids=encode(tokenizer,text)
 return (text,False) if len(ids)<=limit else (tokenizer.decode(ids[:limit],skip_special_tokens=False),True)
def clean_text(text):
 for marker in SPECIAL_MARKERS:text=text.replace(marker,marker.replace("<","[").replace(">","]"))
 return text
def evidence_parts(evidence):
 names={key:value["name"] for key,value in evidence.get("node_names",{}).items()}
 emotions={x["emotion_id"]:x["canonical_name"] for x in evidence["emotion_candidates"]}
 cues=[f'{r["cue_id"]}={r["score"]:.4f}' for r in evidence["query_cues"]]
 apps=[]
 for dim in evidence["appraisal_dimensions"]:
  candidates=dim["display_candidates"]
  if not candidates:apps.append(dim["dimension_id"]+": abstain (insufficient evidence)");continue
  for state in candidates:
   n=",".join(str(e["support_count_groups"]) for e in state["supporting_edges"])
   apps.append(f'{dim["dimension_id"]}: {state["state_id"]}; s={state["association_support"]:.4f}; coverage={state["query_coverage"]:.3f}; edge_source_groups=[{n}]')
 emos=[f'{r["canonical_name"]}: s={r["association_score"]:.4f}; coverage={r["query_coverage"]:.3f}' for r in evidence["emotion_candidates"]]
 paths=[]
 for path in evidence["explanation_paths"]:
  nodes=[path["cue_id"]]
  if "appraisal_state_id" in path:nodes.append(path["appraisal_state_id"])
  nodes.append(emotions.get(path["emotion_id"],names.get(path["emotion_id"],path["emotion_id"])))
  n=",".join(map(str,path["edge_support_count_groups"]))
  joint="" if path["joint_support_groups"] is None else f'; joint_source_groups={path["joint_support_groups"]}'
  paths.append(" > ".join(nodes)+f'; s={path["association_path_score"]:.4f}; edge_source_groups=[{n}]'+joint)
 return dict(cues=cues,appraisals=apps,emotions=emos,paths=paths)
def render_parts(parts,omitted=0):
 return "\n".join([DISCLAIMER,"[Detected cue evidence; uncalibrated, active and available]","; ".join(parts["cues"]) or "none","[Graph-derived appraisal hypotheses]"]+parts["appraisals"]+["[Graph-derived emotion candidates]"]+parts["emotions"]+["[Supporting graph paths]"]+parts["paths"]+([f"{omitted} lower-priority evidence entries omitted to fit the fixed context budget."] if omitted else []))
def format_evidence(evidence,tokenizer,budget):
 if evidence["fallback"]["required"]:return "",dict(fallback=True,graph_tokens=0,omitted_evidence=0,displayed_paths=0)
 parts=evidence_parts(evidence);omitted=0
 while True:
  text=render_parts(parts,omitted)
  if len(encode(tokenizer,text))<=budget:break
  if parts["paths"]:parts["paths"].pop();omitted+=1
  elif parts["cues"]:parts["cues"].pop();omitted+=1
  else:raise ValueError("Mandatory hypotheses and uncertainty statement exceed graph budget")
 return text,dict(fallback=False,graph_tokens=len(encode(tokenizer,text)),omitted_evidence=omitted,displayed_paths=len(parts["paths"]))
def make_tokens(dataset,sample,evidence,label_type,limits):
 tokenizer=dataset.tokenizer
 # Question depends only on task type; answers never affect prompt length or retrieval.
 qa=dataset.get_qa_pairs(dataset.dataset,label_type,sample)
 subtitle,truncated=trim_text(tokenizer,clean_text(sample["subtitle"]),limits["subtitle_token_budget"])
 graph,info=format_evidence(evidence,tokenizer,limits["graph_token_budget"])
 message=qa["question"]+("\n"+graph if graph else "")
 prompt=dataset.replace_token_for_multimodal(dataset.get_prompt_for_multimodal(dataset.face_or_frame,subtitle,message))
 prompt_ids=encode(tokenizer,prompt)
 if len(prompt_ids)>limits["prompt_token_budget"]:
  # Deterministic prompt-only fallback: reduce graph budget, never inspect target length.
  excess=len(prompt_ids)-limits["prompt_token_budget"]
  graph,info=format_evidence(evidence,tokenizer,max(1,limits["graph_token_budget"]-excess-8))
  message=qa["question"]+("\n"+graph if graph else "")
  prompt=dataset.replace_token_for_multimodal(dataset.get_prompt_for_multimodal(dataset.face_or_frame,subtitle,message));prompt_ids=encode(tokenizer,prompt)
 if len(prompt_ids)>limits["prompt_token_budget"]:raise ValueError("Prompt exceeds fixed budget")
 terminator=encode(tokenizer,"###")
 raw_answer=encode(tokenizer,clean_text(qa["answer"]))
 answer_limit=limits["answer_token_budget"]-len(terminator)
 target_ids=raw_answer[:answer_limit]+terminator
 info.update(prompt_tokens=len(prompt_ids),answer_tokens=len(target_ids),answer_truncated=len(raw_answer)>answer_limit,subtitle_truncated=truncated,label_type=label_type)
 return prompt_ids,target_ids,prompt,info
