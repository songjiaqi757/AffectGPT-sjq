import argparse,concurrent.futures,collections,copy,json,os,sys,time
import numpy as np
from .common import *
def part(task):
 run,kind,name,rows=task;run=Path(run)
 with lock(run/"preparation_locks"/(kind+"_"+str(name)+".lock"),True):
  manifest=run/("train_cache" if kind=="train" else "eval_cache")/(str(name)+".manifest.json")
  if manifest.exists():
   cached=read(manifest)
   if cached.get("plan_id")==load_plan(run)["plan_id"] and cached["samples"]==len(rows) and sha(cached["path"])==cached["sha256"]:return cached
  result=_part(task);result["plan_id"]=load_plan(run)["plan_id"];write(manifest,result);return result
def _part(task):
 run,kind,name,rows=task;run=Path(run);p=load_plan(run)
 os.chdir(PROJECT/"AffectGPT");sys.path.insert(0,str(PROJECT/"AffectGPT"))
 from amg_graph_v2.v21.runtime import SampleGraphV21
 from amg_graph_v2.unified_prompt.adapter import UnifiedAMGPromptAdapter
 from amg_graph_v2.unified_prompt.integration import AffectGPTUnifiedBridge
 from amg_graph_v2.unified_prompt.tokenization import actual_interfaces,extract
 tok,reader,chat,binding=actual_interfaces()
 # Exact original QA function without importing GPU/model modules.
 source=PROJECT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py"
 ns={};exec(compile(extract(source,"get_qa_pairs","BaseDataset"),str(source),"exec"),ns)
 qa_func=ns["get_qa_pairs"]
 import types
 for method in ["func_get_qa_description","func_get_qa_ovlabel"]:
  extra={};exec(compile(extract(source,method,"BaseDataset"),str(source),"exec"),extra)
  setattr(reader,method,types.MethodType(extra[method],reader))
 graph=SampleGraphV21(p["graph_v21_release"]);adapter=UnifiedAMGPromptAdapter(tok,graph_release=p["graph_v21_release"]);bridge=AffectGPTUnifiedBridge(adapter)
 if kind=="train":
  q=np.load(G/"amg_graph_v2/data/cue_scores.npz");z=np.load(G/"amg_graph_v2/data/labels.npz");where={s:i for i,s in enumerate(z["sample_ids"])}
 dest=run/("train_cache" if kind=="train" else "eval_cache")/(str(name)+".jsonl")
 counts=collections.Counter();maxseq=0;maxprompt=0;maxgraph=0;prior_matches=0
 existing=[]
 if kind=="train" and dest.with_suffix(".tmp").exists():
  with dest.with_suffix(".tmp").open() as priorfile:
   for line in priorfile:
    try:x=json.loads(line)
    except json.JSONDecodeError:break
    require(x["sample_id"]==rows[len(existing)]["sample_id"],"Partial cache membership changed")
    existing.append(x)
  for x in existing:
   for z in x["tasks"].values():
    a=z["info"];maxseq=max(maxseq,len(z["ids"])+len(z["target"])+2);maxprompt=max(maxprompt,a["prompt_tokens"]);maxgraph=max(maxgraph,a["graph_tokens"]);counts["fallback"]+=int(a["fallback"])
 prior=Path(p["prompt_source_run"]);inv=read(prior/"cache_inventory.json") if kind=="eval" else {}
 with dest.with_suffix(".tmp").open("w") as out:
  for x in existing:out.write(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n")
  for n,row in enumerate(rows):
   if n<len(existing):continue
   sid=row["sample_id"]
   if kind=="train":
    j=where[sid];scores=[float(q["scores"][j,h]) if q["available"][j,h] else None for h in range(42)]
    g=graph.build(sid,scores,q["available"][j].tolist())
   else:
    old=read(G/"amg_inference/runs/graph_225_20261022_174537/cache"/(canonical(sid)+".json"))
    require(old["input_id"]==canonical({k:row[k] for k in ["sample_id","text","audio_path","video_path"]}),"Cue input mismatch")
    require(old["cache_id"]==canonical({k:v for k,v in old.items() if k!="cache_id"}),"Cue cache changed")
    g=graph.build_from_old_cue(old["cue"])
   require(g["graph_release_id"]==p["graph_release_id"],"Graph release mismatch")
   original_blocks=adapter._blocks
   block_cache={}
   def cached_blocks(sg,cues,features):
    k=tuple(n["ontology_id"] for n in cues)
    if k not in block_cache:block_cache[k]=copy.deepcopy(original_blocks(sg,cues,features))
    return copy.deepcopy(block_cache[k])
   adapter._blocks=cached_blocks
   item=dict(sample_id=sid,tasks={}) if kind=="train" else None
   for label in (["description","ovlabel"] if kind=="train" else ["inference"]):
    qa=qa_func(reader,"MERCaptionPlus",label,row) if kind=="train" else dict(question=p["prompt_question"])
    b=bridge.prepare(reader,chat,g,qa["question"],row["subtitle"],max_length=2000,max_new_tokens=1200)
    packet=b["evidence"];a=packet["audit"];text=packet["text"]
    native=reader.get_prompt_for_multimodal("multiface_audio_face_text",row["subtitle"],qa["question"]+("\n\n"+text if text else ""))
    require(native==b["prompt"],"Native prompt mismatch")
    ids=tok.encode(chat.replace_token_for_multimodal(b["prompt"]),add_special_tokens=False)
    require(len(ids)==a["full_prompt_tokens"]<=800 and a["evidence_tokens"]<=1000,"Prompt budget")
    maxprompt=max(maxprompt,len(ids));maxgraph=max(maxgraph,a["evidence_tokens"]);counts["fallback"]+=int(not text)
    if kind=="train":
     from amg_finetune_nogc.prompts import clean_text
     end=tok.encode("###",add_special_tokens=False);raw=tok.encode(clean_text(qa["answer"]),add_special_tokens=False);target=raw[:p["training"]["answer_token_budget"]-len(end)]+end
     maxseq=max(maxseq,len(ids)+len(target)+2)
     info=dict(fallback=not bool(text),evidence_level=3 if text else 0,gate_reasons=["native_full_v21_no_extra_gate_no_dropout"],graph_tokens=a["evidence_tokens"],prompt_tokens=len(ids),answer_tokens=len(target),answer_truncated=len(raw)>len(target)-len(end),subtitle_truncated=False,label_type=label,fold=None,fold_graph_id=g["graph_release_id"],CA_edge_count=a.get("CA_edge_count",0),CE_edge_count=a.get("CE_edge_count",0),original_subtitle_preserved=True,prompt_sha256=canonical(b["prompt"]),graph_release_id=g["graph_release_id"])
     item["tasks"][label]=dict(ids=ids,target=target,info=info)
    else:
     if sid in inv:
      oldpacket=read(inv[sid]["path"]);require(oldpacket["final_prompt"]==b["prompt"] and oldpacket["packet"]["text"]==text,"Prior native v21 prompt differs");prior_matches+=1
     item=dict(sample_id=sid,row_sha256=canonical(row),final_prompt=b["prompt"],packet=packet)
     item["cache_id"]=canonical(item)
   adapter._blocks=original_blocks
   out.write(json.dumps(item,ensure_ascii=False,separators=(",",":"))+"\n")
   if (n+1)%100==0:status(run,"prepare_"+kind+"_"+str(name),state="preparing",completed=n+1,total=len(rows))
 dest.with_suffix(".tmp").replace(dest)
 require(maxseq<=p["training"]["certified_actual_max_tokens"],"Training sequence exceeds certified bound")
 result=dict(path=str(dest),sha256=sha(dest),samples=len(rows),kind=kind,name=name,maximum_sequence_tokens=maxseq,maximum_prompt_tokens=maxprompt,maximum_graph_tokens=maxgraph,prior_native_prompt_exact_matches=prior_matches,statistics=dict(counts))
 write(dest.with_suffix(".manifest.json"),result);status(run,"prepare_"+kind+"_"+str(name),state="complete",**{k:v for k,v in result.items() if k!="name"});return result
def main(run):
 run=Path(run);p=load_plan(run);verify_code(run);records=read(run/"train_records.json");tasks=[]
 for i in range(0,len(records),1000):tasks.append((str(run),"train",i//1000,records[i:i+1000]))
 for d,s in p["datasets"].items():tasks.append((str(run),"eval",d,read(s["path"])))
 results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
  futures=[pool.submit(part,t) for t in tasks]
  for f in concurrent.futures.as_completed(futures):
   results.append(f.result());status(run,"preparation",state="preparing",parts_complete=len(results),parts_total=len(tasks))
   train=[x for x in results if x["kind"]=="train"]
   if len(train)==(len(records)+999)//1000 and not (run/"cache_manifest.json").exists():
    require(sum(x["samples"] for x in train)==p["training_count"],"Training count")
    write(run/"cache_manifest.json",dict(complete=True,samples=p["training_count"],plan_id=p["plan_id"],parts=sorted(train,key=lambda x:x["name"]),graph_release_id=p["graph_release_id"],same_full_graph_and_P4_as_inference=True,extra_gate=False,dropout=False,OOF_substitution=False))
    write(run/"cpu_preflight.json",dict(passed=True,all_samples_checked=p["training_count"],all_QA_tasks_checked=2*p["training_count"],max_sequence=max(x["maximum_sequence_tokens"] for x in train),maximum_prompt_tokens=max(x["maximum_prompt_tokens"] for x in train),all_files_on_server=True))
 ev=[x for x in results if x["kind"]=="eval"];require(len(ev)==9 and sum(x["samples"] for x in ev)==12799,"Evaluation membership total")
 require(sum(x["prior_native_prompt_exact_matches"] for x in ev)==1400,"Existing inference prompt equivalence")
 write(run/"eval_cache_manifest.json",dict(complete=True,parts=ev,samples=sum(x["samples"] for x in ev),prior_1400_exact_matches=True))
 status(run,"preparation",state="complete",parts_complete=len(results),report=results)
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);main(a.parse_args().run)
