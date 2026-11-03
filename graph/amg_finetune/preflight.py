"""Full current-run membership, cache provenance and both-task token-budget verification."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,concurrent.futures,csv,json,os,random,sys,time
from graph_paths import Path
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .common import ROOT,load_plan,now,bound_query,verify_code

def shard(run_string,index,count):
 run=Path(run_string);plan=load_plan(run)
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"))
 from omegaconf import OmegaConf
 from .dataset import GraphContinueDataset
 from .prompts import make_tokens
 cfg=OmegaConf.create(read(run/"original_config.json")["model"])
 cfg.max_length=plan["training"]["max_sequence_tokens"]
 records=read(run/"train_records.json")[index::count];dataset=GraphContinueDataset(run,cfg,subset_ids=[r["sample_id"] for r in records])
 expected={r["sample_id"]:r for r in read(Path(plan["cue_release_path"])/"members.json")}
 inventory=[];tokens=[];invalid={m:0 for m in ["text","audio","visual"]};fallbacks=0;truncated_answers=0;omitted=0
 start=time.time()
 for i,r in enumerate(records):
  sid=r["sample_id"];p=run/"cache"/(sid+".json");item=read(p)
  require(item["cache_id"]==canonical({k:v for k,v in item.items() if k!="cache_id"}),"Cache identity mismatch: "+sid)
  require(item["sample_id"]==sid and item["plan_id"]==plan["plan_id"],"Cache provenance mismatch")
  require(item["record_sha256"]==canonical({k:r[k] for k in ["sample_id","text","audio_path","video_path"]}),"Cache input mismatch")
  q=item["cue"];ev=item["evidence"]
  require(q["query_input_id"]==canonical({k:v for k,v in q.items() if k!="query_input_id"}),"Cue checksum changed")
  require(ev["query_input_id"]==q["query_input_id"] and ev["query_config_id"]==plan["query_config_id"],"Evidence binding mismatch")
  for m in invalid:invalid[m]+=int(not q["modality_present"][m])
  for m in ["audio","visual"]:
   require(q["input_fingerprints"][m]["sha256"]==expected[sid]["media_assets"][m]["sha256"],"Raw media does not match frozen source release")
  require(Path(r["face_path"]).is_file(),"Missing training face: "+sid)
  fallbacks+=int(ev["fallback"]["required"])
  cases={}
  for label_type in ["description","ovlabel"]:
   prompt,target,text,info=make_tokens(dataset,r,ev,label_type,plan["training"])
   require(len(prompt)+len(target)+2<=plan["training"]["max_sequence_tokens"],"Context overflow: "+sid)
   require(bool(target) and all(x>=0 for x in target),"Invalid supervision")
   require(text.endswith("###Assistant: "),"Assistant boundary lost")
   for token,n in [(dataset.MULTI_PATCH_TOKEN_ID,1),(dataset.AUDIO_PATCH_TOKEN_ID,1),(dataset.FACE_PATCH_TOKEN_ID,1),(dataset.IMAGE_PATCH_TOKEN_ID,0),(dataset.FRAME_PATCH_TOKEN_ID,0)]:
    require(prompt.count(token)==n,"Multimodal tokens corrupted")
   require(ev["fallback"]["required"] or ("not calibrated probabilities" in text and "[Graph-derived emotion candidates]" in text),"Graph uncertainty or candidates missing")
   truncated_answers+=int(info["answer_truncated"]);omitted+=info["omitted_evidence"];tokens.append(len(prompt)+len(target)+2)
   cases[label_type]=dict(prompt_id=canonical(prompt),target_id=canonical(target),**info)
  inventory.append(dict(sample_id=sid,cache_sha256=sha(p),cache_id=item["cache_id"],previous_role=r["previous_role"],tasks=cases))
  if (i+1)%100==0:
   atomic_json(run/f"preflight_shard_{index}_status.json",dict(state="running",completed=i+1,total=len(records),elapsed_seconds=time.time()-start))
 with (run/f"cache_inventory_{index}.jsonl").open("w") as stream:
  for r in inventory:stream.write(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n")
 report=dict(state="complete",index=index,samples=len(records),invalid_modality_counts=invalid,fallbacks=fallbacks,truncated_answer_cases=truncated_answers,omitted_evidence_entries=omitted,actual_sequence_tokens_min=min(tokens),actual_sequence_tokens_max=max(tokens),actual_sequence_tokens_mean=sum(tokens)/len(tokens),inventory_sha256=sha(run/f"cache_inventory_{index}.jsonl"),elapsed_seconds=time.time()-start)
 atomic_json(run/f"preflight_shard_{index}_status.json",report)
 return report
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);args=p.parse_args();run=Path(args.run);plan=load_plan(run);verify_code(run)
 for index in [0,1]:require(read(run/f"cache_worker_{index}_status.json")["state"]=="complete","Cache worker unfinished")
 rows=read(run/"train_records.json");audit=read(run/"human_audit_500.json");ids={r["sample_id"] for r in rows}
 require(len(ids)==30755 and not(ids&{r["sample_id"] for r in audit}),"Training/audit membership changed")
 require({p.stem for p in (run/"cache").glob("*.json")}==ids,"Cache membership differs from training")
 count=4
 with concurrent.futures.ProcessPoolExecutor(max_workers=count) as pool:reports=list(pool.map(shard,[str(run)]*count,range(count),[count]*count))
 require(sum(r["samples"] for r in reports)==30755,"Incomplete preflight")
 from amg_runtime.engine import GraphQueryEngine
 engine=GraphQueryEngine.from_release(plan["runtime_path"],config_path=plan["query_config_path"])
 proof=[]
 for i in [0,10251,20502,30754]:
  item=read(run/"cache"/(rows[i]["sample_id"]+".json"))
  require(bound_query(engine.query(item["cue"]),engine)==item["evidence"],"Saved evidence does not reproduce native query")
  proof.append(rows[i]["sample_id"])
 graph_before=read(Path(read(ROOT/"amg_validation/runs/current.json")["path"])/"graph_before.json")
 graph_path=Path(read(Path(plan["runtime_path"])/"inputs_p0.json")["graph"]["path"])
 for relative,digest in graph_before["artifact_sha256"].items():require(_graph_hash_matches(graph_path / relative, digest, sha(graph_path / relative)),"Frozen graph changed")
 inventory={}
 for index in range(count):
  with (run/f"cache_inventory_{index}.jsonl").open() as f:
   for line in f:
    r=json.loads(line);inventory[r["sample_id"]]=r
 with (run/"cache_inventory.jsonl").open("w") as f:
  for r in rows:f.write(json.dumps(inventory[r["sample_id"]],ensure_ascii=False,sort_keys=True)+"\n")
 manifest=dict(complete=True,completed_at_beijing=now(),plan_id=plan["plan_id"],samples=len(rows),human_audit_excluded=len(audit),training_ids_digest=plan["training_ids_digest"],query_config_id=plan["query_config_id"],cache_inventory_sha256=sha(run/"cache_inventory.jsonl"),cache_execution_sha256=sha(run/"cache_execution.json"),source_code_manifest_sha256=sha(run/"code_manifest.json"),native_query_replay_cases=proof,all_prompt_tasks_checked=61510,shards=reports,graph_artifact_hashes_unchanged=True,target_labels_used=False,independent_validation_available=False)
 manifest["cache_release_id"]=canonical(manifest);atomic_json(run/"cache_manifest.json",manifest);print(json.dumps(manifest,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
