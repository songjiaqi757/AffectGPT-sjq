import gzip,json,os,sys,collections
from pathlib import Path
from .common import *
from .prepare import reader_for
def main():
 run=Path(read(ROOT/"amg_v21_continue/current_run.json")["path"]);p=load_plan(run);reader=reader_for(run)
 from amg_graph_v2.unified_prompt.adapter import UnifiedAMGPromptAdapter
 from amg_graph_v2.unified_prompt.integration import AffectGPTUnifiedBridge
 from .policy import make_tokens
 from amg_finetune_nogc.prompts import encode
 native=Path(p["prompt_source_run"]);old=read(native/"plan.json");inv=read(native/"cache_inventory.json");adapter=UnifiedAMGPromptAdapter(reader.tokenizer,graph_release=p["graph_v21_release"]);bridge=AffectGPTUnifiedBridge(adapter)
 matches=collections.Counter();maxprompt=0;maxgraph=0
 for dataset,spec in old["datasets"].items():
  for row in read(spec["path"]):
   cached=read(inv[row["sample_id"]]["path"]);gfile=native/"graphs"/(Path(inv[row["sample_id"]]["path"]).stem+".json.gz")
   with gzip.open(gfile,"rt",encoding="utf-8") as f:graph=json.load(f)
   prepared=bridge.prepare(reader,reader,graph,old["prompt_question"],row["subtitle"],max_length=2000,max_new_tokens=1200)
   assert prepared["prompt"]==cached["final_prompt"],(dataset,row["sample_id"],"Full Prompt mismatch")
   assert prepared["evidence"]["text"]==cached["packet"]["text"],"P4 evidence mismatch"
   matches[dataset]+=1;maxprompt=max(maxprompt,prepared["evidence"]["audit"]["full_prompt_tokens"]);maxgraph=max(maxgraph,prepared["evidence"]["audit"]["evidence_tokens"])
  print("EXACT_PROMPT_MATCH",dataset,matches[dataset],flush=True)
 rows=read(run/"train_records.json");targets=collections.Counter();maxanswer=0
 for row in rows:
  for label,question in [("description",p["prompt_input_contract"]["description_question"]),("ovlabel",p["prompt_input_contract"]["ovlabel_question"])]:
   qa=reader.get_qa_pairs(reader.dataset,label,row);assert qa["question"]==question
   expected=row["description"] if label=="description" else "The character's emotional state is "+row["ovlabel"]+"."
   assert qa["answer"]==expected
   n=len(encode(reader.tokenizer,qa["answer"]));maxanswer=max(maxanswer,n)
   if n>p["training"]["answer_token_budget"]-len(encode(reader.tokenizer,"###")):targets[label]+=1
 row=rows[0];empty=dict(level=0,gate_reasons=["smoke"],fold=0,fold_graph_id="smoke",tasks={t:dict(levels={}) for t in ["description","ovlabel"]})
 for label in ["description","ovlabel"]:
  ids,target,prompt,info=make_tokens(reader,row,empty,label,p["training"])
  qa=reader.get_qa_pairs(reader.dataset,label,row)
  assert prompt==reader.replace_token_for_multimodal(reader.get_prompt_for_multimodal(reader.face_or_frame,row["subtitle"],qa["question"]))
  assert ids==encode(reader.tokenizer,prompt)
 result=dict(passed=True,plan_id=p["plan_id"],exact_prior_inference_prompt_matches=dict(matches),all_1400_exact=True,maximum_prior_prompt_tokens=maxprompt,maximum_prior_graph_tokens=maxgraph,original_paired_QA_samples=len(rows),hybrid_sampling="Original uniform random description/ovlabel, two paired questions",original_answer_text_before_context_cap=True,answer_context_cap_counts=dict(targets),maximum_untruncated_answer_tokens=maxanswer,target_labels_used_for_training=False,created_at_beijing=now())
 atomic_json(run/"native_P4_prompt_equivalence.json",result);print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
