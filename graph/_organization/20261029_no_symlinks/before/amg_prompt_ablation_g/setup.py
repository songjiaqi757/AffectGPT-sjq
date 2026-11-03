"""CPU-only frozen G preparation with exact-prompt F reuse verification."""
import argparse,ast,copy,datetime,json,os,sys,types
from pathlib import Path
from .common import *
from .policy import make_prompt
from amg_prompt_ablation.setup import extracted_function

REFERENCE=ROOT/"amg_prompt_ablation/runs/prompt_ablation_20261027_215553"
def add_g(bundle,tokenizer):
 x=copy.deepcopy(bundle);oldid=x.pop("bundle_id",None)
 if oldid is not None:require(oldid==canonical(x),"Source bundle checksum changed")
 x["source_bundle_id"]=oldid
 f=x["texts"]["F"]
 lines=f.splitlines();removed=[v for v in lines if v.startswith("Tentative emotion alternatives, not confirmed labels:")]
 require(len(removed)<=1,"Unexpected F emotion format")
 g="\n".join(v for v in lines if not v.startswith("Tentative emotion alternatives, not confirmed labels:"))
 info=copy.deepcopy(x["infos"]["F"])
 info.update(ablation="G",ablation_description="Cue plus explicit-alternative Appraisal; no emotion candidates or paths",
  graph_tokens=len(tokenizer.encode(g,add_special_tokens=False)),emotion_candidates_displayed=0,graph_text_id=canonical(g))
 x["texts"]["G"]=g;x["infos"]["G"]=info
 require("Emotion hypotheses:" not in g and "Tentative emotion alternatives" not in g and info["displayed_paths"]==0,"G leaks removed fields")
 require(info["cues_displayed"]==x["infos"]["F"]["cues_displayed"] and info["appraisals_displayed"]==x["infos"]["F"]["appraisals_displayed"],"Changed retained fields")
 require(info["graph_tokens"]<=512,"G evidence exceeds budget")
 return x

def main():
 require(os.environ.get("CUDA_VISIBLE_DEVICES")=="","Setup must be CPU-only")
 old=plan(REFERENCE);verify_code(REFERENCE)
 require(read(REFERENCE/"status.json")["phase"]=="complete","Parent experiment incomplete")
 proposal=read(ROOT/"analysis_reports/next_experiment_G_20261028/plan.json")
 require(proposal["source_plan_id"]==old["plan_id"],"Prepared proposal no longer matches")
 stamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
 run=ROOT/"amg_prompt_ablation_g/runs"/("g_soft_appraisal_"+stamp);run.mkdir(parents=True,exist_ok=False)
 for name in ["jobs","shards","evaluation_jobs","predictions","scores","prompt_cache"]:(run/name).mkdir()
 p=copy.deepcopy(old)
 for key in ["plan_id","prompt_cache_manifest_id"]:p.pop(key,None)
 p.update(schema_version="fixed_prompt_G_extension_v1",created_at_beijing=now(),purpose="G only: same F Appraisal uncertainty wording, remove Emotion candidates",
  reference_run=str(REFERENCE),reference_plan_id=old["plan_id"],proposal_path=str(ROOT/"analysis_reports/next_experiment_G_20261028/plan.json"),
  training_run=str(run),conditions=["G"],condition_descriptions={"G":"Cue + explicit-alternative Appraisal; no Emotion candidates or paths"},
  variants=[],variant_epochs={},variant_bases={},checkpoint_by_variant={},weight_by_variant={},ablation_by_variant={},
  logical_jobs=6,sample_predictions_total=2800,new_predictions=1082,reused_predictions=1718)
 p["experiment_policy"]=dict(p["experiment_policy"],new_condition="G removes only F emotion line",scoring="Existing unified original pipeline unchanged",reuse="Exact full-prompt,checkpoint,seed,media binding and decode configuration match")
 for weight,spec in p["weights"].items():
  require(sha(spec["path"])==spec["sha256"],"Checkpoint changed")
  v=weight+"_G";p["variants"].append(v);p["variant_epochs"][v]=[spec["epoch"]];p["variant_bases"][v]=35
  p["checkpoint_by_variant"][v]=spec;p["weight_by_variant"][v]=weight;p["ablation_by_variant"][v]="G"
 for name in ["original_config.json","evaluation_resources.json","train_records.json"]:
  (run/name).write_bytes((REFERENCE/name).read_bytes())
 for path,digest in read(run/"evaluation_resources.json")["files"].items():require(sha(path)==digest,"Unified evaluation resources changed")
 os.chdir(ROOT/"AffectGPT")
 import importlib.util
 cfgspec=importlib.util.spec_from_file_location("g_frozen_config",ROOT/"AffectGPT/config.py")
 cfg=importlib.util.module_from_spec(cfgspec);cfgspec.loader.exec_module(cfg)
 from transformers import AutoTokenizer
 ns=dict(AutoTokenizer=AutoTokenizer,config=cfg)
 exec(extracted_function(ROOT/"AffectGPT/my_affectgpt/models/tokenizer.py","load_tokenizer_from_LLM"),ns)
 tokenizer=ns["load_tokenizer_from_LLM"]("Qwen25")
 scope={};exec(extracted_function(ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py","get_prompt_for_multimodal"),scope)
 reader=types.SimpleNamespace();reader.get_prompt_for_multimodal=types.MethodType(scope["get_prompt_for_multimodal"],reader)
 chat=types.SimpleNamespace(tokenizer=tokenizer,replace_token_for_multimodal=lambda s:s)
 rows_by={};bundle_ids={};full_prompts={};source_files={};maxgraph=0;maxprompt=0
 source_started=datetime.datetime.fromisoformat(read(REFERENCE/"status.json")["started_at_beijing"]).timestamp()
 for d,ds in p["datasets"].items():
  require(sha(ds["path"])==ds["sha256"],"Frozen dataset changed");rows=read(ds["path"]);rows_by[d]=rows
  for row in rows:
   sid=row["sample_id"];path=REFERENCE/"prompt_cache"/(sid_key(sid)+".json")
   b=add_g(read(path),tokenizer)
   for modality in ["audio_path","face_path"]:
    st=Path(row[modality]).stat();require(st.st_mtime<source_started,"Media changed since parent generation: "+row[modality])
   prompt,info=make_prompt(reader,chat,row,b,dict(p,variant="base35_G"))
   b["expected_prompt_ids"]["G"]=info["prompt_id"]
   b["full_prompt_G"]=prompt
   b["bundle_id"]=canonical(b);atomic_json(run/"prompt_cache"/path.name,b)
   full_prompts[sid]=dict(G=info,oldF_id=b["expected_prompt_ids"]["F"],same_as_F=b["texts"]["G"]==b["texts"]["F"])
   if full_prompts[sid]["same_as_F"]:require(info["prompt_id"]==b["expected_prompt_ids"]["F"],"G/F full-prompt mismatch")
   bundle_ids[sid]=b["bundle_id"];source_files[str(path)]=sha(path)
   maxgraph=max(maxgraph,info["graph_tokens"]);maxprompt=max(maxprompt,info["prompt_tokens"])
  print("Frozen G prompts",d,len(rows),flush=True)
 probe=add_g(read(REFERENCE/"source_probe_bundle.json"),tokenizer)
 probe["expected_prompt_ids"].pop("G",None)
 probe_row=read(run/"train_records.json")[0]
 _,info=make_prompt(reader,chat,probe_row,probe,dict(p,variant="base35_G"))
 probe["expected_prompt_ids"]["G"]=info["prompt_id"];atomic_json(run/"source_probe_bundle.json",probe)
 p["prompt_cache_manifest_id"]=canonical(bundle_ids);p["reuse_source_manifest_id"]=canonical(source_files)
 p["plan_id"]=canonical(p);atomic_json(run/"plan.json",p)
 reused={};fresh=0;media_count=0
 for weight,spec in p["weights"].items():
  variant=weight+"_G"
  for d,rows in rows_by.items():
   epoch=spec["epoch"];jid=f"{variant}_epoch_{epoch}_{d}";out=run/"predictions"/jid;out.mkdir()
   sourcejob=read(REFERENCE/"jobs"/f"{weight}_F_epoch_{epoch}_{d}.json")
   source_score=read(REFERENCE/"scores"/f"{weight}_F_epoch_{epoch}_{d}.json")
   require(sha(source_score["raw_path"])==source_score["raw_sha256"],"Source F answers changed")
   source_files[sourcejob["prediction_path"]]=sha(sourcejob["prediction_path"])
   with Path(sourcejob["prediction_path"]).open() as f:oldrows={x["sample_id"]:x for x in map(json.loads,f)}
   require(len(oldrows)==len(rows),"Source F coverage differs")
   binding=canonical(dict(plan_id=p["plan_id"],variant=variant,checkpoint=spec["sha256"],input_sha=p["datasets"][d]["sha256"]))
   for row in rows:
    sid=row["sample_id"];meta=full_prompts[sid]
    if not meta["same_as_F"]:fresh+=1;continue
    previous=oldrows[sid];seed=(42+int(canonical(sid)[:8],16))%2**32
    require(previous["checkpoint"]["sha256"]==spec["sha256"] and previous["seed"]==seed,"Reuse weight/seed differs")
    require(previous["plan_id"]==old["plan_id"] and previous["prompt_info"]["prompt_id"]==meta["G"]["prompt_id"],"Reuse prompt/provenance differs")
    require(previous["dataset"]==d and previous["name"]==row["name"],"Reuse sample differs")
    expected=canonical(dict(plan_id=old["plan_id"],variant=weight+"_F",checkpoint=spec["sha256"],input_sha=old["datasets"][d]["sha256"]))
    require(previous["binding"]==expected and p["generation"]==old["generation"],"Reuse media/data/decode binding differs")
    x=dict(previous,variant=variant,plan_id=p["plan_id"],binding=binding,prompt_info=meta["G"],created_at_beijing=now(),
      reused=True,source_prediction_path=sourcejob["prediction_path"],source_prediction_record_sha256=canonical(previous),
      source_plan_id=old["plan_id"],source_variant=weight+"_F")
    atomic_json(out/(sid_key(sid)+".json"),x)
    reused[variant+"::"+sid]=dict(source_record_sha256=canonical(previous),prompt_id=meta["G"]["prompt_id"],checkpoint_sha256=spec["sha256"],seed=seed)
   names=[]
   for start in range(0,len(rows),64):
    stop=min(start+64,len(rows));name=f"{jid}_{start:04d}.json";names.append(name)
    atomic_json(run/"shards"/name,dict(job_id=jid,variant=variant,epoch=epoch,dataset=d,dataset_samples=len(rows),start=start,stop=stop,samples=stop-start,state="pending",attempts=0))
   atomic_json(run/"jobs"/(jid+".json"),dict(job_id=jid,variant=variant,epoch=epoch,dataset=d,samples=len(rows),shards=names,state="pending"))
   atomic_json(run/"evaluation_jobs"/(jid+".json"),dict(job_id=jid,state="pending",attempts=0,estimated_seconds=len(rows)*(2 if d=="SIMS" else 1)))
 require(len(reused)==1718 and fresh==1082,"Unexpected G reuse/fresh budget")
 atomic_json(run/"reuse_manifest.json",dict(reused_predictions=1718,new_predictions=1082,records=reused))
 atomic_json(run/"reference_input_hashes.json",source_files)
 paths=list((ROOT/"amg_prompt_ablation_g").glob("*.py"))+[ROOT/name for name in read(REFERENCE/"code_manifest.json")["files"]]
 for f in paths:ast.parse(f.read_text())
 atomic_json(run/"code_manifest.json",dict(files={str(f.relative_to(ROOT)):sha(f) for f in paths}))
 preflight=dict(passed=True,jobs=6,total_predictions=2800,new_predictions=1082,reused_predictions=1718,
  prompt_samples=1400,full_prompt_identity_verified=True,checkpoint_hashes_verified=True,
  media_paths_and_unmodified_since_parent=True,decoder_and_seed_identity_verified=True,
  graph_and_gate_unchanged=True,unified_original_evaluation_resources_verified=True,
  max_graph_tokens=maxgraph,max_prompt_tokens=maxprompt,checked_at_beijing=now())
 atomic_json(run/"cpu_preflight.json",preflight)
 (run/"EXPERIMENT.md").write_text("# G extension\n\nOnly G is new: Cue plus F-style alternative Appraisal, no Emotion candidates or paths.\nTwo fixed weights and three datasets, 6 scored jobs / 2800 merged answers,1718 exact-prompt F answers reused and1082 fresh.\nSame per-sample seed,media,graph,gate,decode and unified evaluator.\nTwo A800 GPUs,4 inference processes per GPU,exclusive64-sample shards;all inference exits before one judge per GPU.\nNo training; source A-F records are read-only references.\n")
 atomic_json(ROOT/"amg_prompt_ablation_g/current_run.json",dict(run=str(run),plan_id=p["plan_id"],created_at_beijing=now()))
 print(json.dumps(dict(run=str(run),preflight=preflight),ensure_ascii=False),flush=True)
if __name__=="__main__":main()
