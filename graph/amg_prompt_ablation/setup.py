"""Freeze the authorized 36-job experiment using existing server checkpoints/caches."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import ast,collections,copy,datetime,importlib.util,json,os,sys,types
from graph_paths import Path
from zoneinfo import ZoneInfo
from .common import *
from .policy import CONDITIONS,freeze,make_prompt

OLD=ROOT/"amg_d_graph_compare/runs/d_compare_20261025_111800"
def extracted_function(path,name):
 text=Path(path).read_text();tree=ast.parse(text)
 return next(ast.get_source_segment(text,n) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
def main():
 require(os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU setup requires empty CUDA_VISIBLE_DEVICES")
 old=read(OLD/"plan.json");graphplan=read(OLD/"D_newgraph_plan/plan.json")
 stamp=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S")
 run=ROOT/"amg_prompt_ablation/runs"/("prompt_ablation_"+stamp)
 run.mkdir(parents=True,exist_ok=False)
 for name in ["jobs","shards","evaluation_jobs","predictions","scores","prompt_cache"]:
  (run/name).mkdir()
 original=copy.deepcopy(old["base_checkpoint"])
 base=dict(path=original["path"],sha256=original["sha256"],epoch=35)
 graph=next(x for x in read(OLD/"D_newgraph/checkpoints.json") if x["epoch"]==40)
 weights=dict(base35=base,graph40=graph)
 for name,spec in weights.items():
  require(_graph_hash_matches(spec['path'], spec['sha256'], sha(spec['path'])),"Checkpoint fingerprint changed")
 import torch
 checkpoint_reports={}
 for name,spec in weights.items():
  x=torch.load(_graph_resolve_path(spec['path']), map_location='cpu', weights_only=True)
  require(x["epoch"]==spec["epoch"] and len(x["model"])==412,"Checkpoint metadata/architecture differs")
  if name=="graph40":require(x["amg_finetune"]["plan_id"]==graphplan["plan_id"] and x["amg_finetune"]["base_epoch"]==35,"Wrong graph continuation")
  checkpoint_reports[name]=dict(epoch=x["epoch"],saved_trainable_tensors=len(x["model"]),amg_finetune=x.get("amg_finetune"))
  del x
 require(not torch.cuda.is_initialized(),"CPU setup initialized CUDA")
 p=dict(schema_version="fixed_prompt_ablation_v1",created_at_beijing=now(),
  purpose="Two fixed weights, six frozen prompt-field ablations, three requested datasets; inference only",
  source_plan=str(OLD/"plan.json"),source_plan_id=old["plan_id"],
  graph_release_id=graphplan["graph_release_id"],query_config_id=graphplan["query_config_id"],
  cue_release_id=old["cue_release_id"],runtime_release_id=old["runtime_release_id"],
  target_cache=graphplan["target_cache"],source_cache=old["source_cache"],
  training_run=str(run),training_plan_id=graphplan["plan_id"],
  datasets={d:old["datasets"][d] for d in ["MER2023","SIMS","OVMERDPlus"]},
  weights=weights,conditions=list(CONDITIONS),condition_descriptions=CONDITIONS,
  variants=[],variant_epochs={},variant_bases={},checkpoint_by_variant={},weight_by_variant={},ablation_by_variant={},
  generation=old["generation"],limits=old["limits"],prompt_question=old["prompt_question"],seed=42,
  inference_processes_per_gpu=4,gpus=[0,1],shard_max_samples=64,logical_jobs=36,
  dataset_samples_total=1400,sample_predictions_total=16800,
  schedule="Two GPUs x four processes; shared file-locked <=64-sample shards; larger dataset/shard first; full source-only 1536+1200 concurrent probes before target inference; after all inference exits, two single-judge evaluators",
  experiment_policy=dict(training=False,new_scoring=False,new_graph=False,gate="original D gate evaluated once before field ablation; unchanged across conditions/weights",paths="omitted in all conditions",expression_control="E/F same retained Cue/state/emotion fields; F groups alternative states and states uncertainty",
   common_budget="All six settings share any field deletions necessary for the longest wording to fit 512 graph tokens",per_sample_seed="(42 + int(canonical(sample_id)[:8],16)) % 2**32",target_tuning=False),
  limitations=["Exploratory target test comparison; not independent hyperparameter selection","Weights have different training histories; causal inference uses within-weight prompt contrasts","Sampling retained from historical experiments; one paired random stream is not a multi-seed estimate","Historical confidence gate may mask emotion/Appraisal in some records; no field is forced past gate"])
 for weight,spec in weights.items():
  for c in CONDITIONS:
   v=weight+"_"+c;p["variants"].append(v);p["variant_epochs"][v]=[spec["epoch"]];p["variant_bases"][v]=35
   p["checkpoint_by_variant"][v]=spec;p["weight_by_variant"][v]=weight;p["ablation_by_variant"][v]=c
 (run/"original_config.json").write_bytes((OLD/"original_config.json").read_bytes())
 atomic_json(run/"evaluation_resources.json",read(OLD/"evaluation_resources.json"))
 cfg=read(run/"original_config.json")
 require(all(cfg["model"][k]==1 for k in ["num_audio_query_token","num_video_query_token","num_multi_query_token","num_image_query_token"]),"CPU identity token-expansion assumption invalid")
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'))
 spec=importlib.util.spec_from_file_location("frozen_eval_config",ROOT/"AffectGPT/config.py");config=importlib.util.module_from_spec(spec);spec.loader.exec_module(config)
 from transformers import AutoTokenizer
 namespace=dict(AutoTokenizer=AutoTokenizer,config=config)
 exec(extracted_function(ROOT/"AffectGPT/my_affectgpt/models/tokenizer.py","load_tokenizer_from_LLM"),namespace)
 tokenizer=namespace["load_tokenizer_from_LLM"]("Qwen25")
 scope={}
 exec(extracted_function(ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py","get_prompt_for_multimodal"),scope)
 reader=types.SimpleNamespace()
 reader.get_prompt_for_multimodal=types.MethodType(scope["get_prompt_for_multimodal"],reader)
 chat=types.SimpleNamespace(tokenizer=tokenizer,replace_token_for_multimodal=lambda value:value)
 rows_by_dataset={};levels=collections.Counter();maxgraph=collections.Counter();maxprompt=collections.Counter()
 trimcount=0;source_hashes={};bundle_hashes={};examples=[]
 for d,info in p["datasets"].items():
  require(_graph_hash_matches(info['path'], info['sha256'], sha(info['path'])),"Dataset membership/subtitles changed")
  rows=read(info["path"]);require(len(rows)==info["samples"],"Wrong dataset size")
  rows_by_dataset[d]=rows
  require(len({r["sample_id"] for r in rows})==len(rows),"Duplicate sample")
  for i,row in enumerate(rows):
   for modality in ["audio_path","face_path"]:require(Path(row[modality]).is_file(),"Missing input "+row[modality])
   path=Path(p["target_cache"])/(sid_key(row["sample_id"])+".json");cached=read(path)
   require(cached["sample_id"]==row["sample_id"] and cached["cache_id"]==canonical({k:v for k,v in cached.items() if k!="cache_id"}),"Native cache checksum differs")
   e=cached["evidence"]
   require(e["graph_release_id"]==p["graph_release_id"] and e["query_config_id"]==p["query_config_id"],"Cache graph/config differs")
   expected=canonical({k:row[k] for k in ["sample_id","text","audio_path","video_path"]})
   require(cached["input_record_id"]==expected,"Cache/media binding differs")
   bundle=freeze(e,tokenizer,512);bundle["source_native_cache_sha256"]=sha(path)
   bundle["expected_prompt_ids"]={}
   for c in CONDITIONS:
    pcfg=dict(p,variant="base35_"+c)
    prompt,pi=make_prompt(reader,chat,row,bundle,pcfg)
    bundle["expected_prompt_ids"][c]=pi["prompt_id"]
    maxgraph[c]=max(maxgraph[c],pi["graph_tokens"]);maxprompt[c]=max(maxprompt[c],pi["prompt_tokens"])
    require((c in ["C","E","F"] or pi["appraisals_displayed"]==0) and (c in ["D","E","F"] or pi["emotion_candidates_displayed"]==0),"Ablation leaked hidden fields")
   require(bundle["texts"]["A"]=="","Baseline has evidence")
   require(bundle["infos"]["E"]["shared_semantic_id"]==bundle["infos"]["F"]["shared_semantic_id"],"E/F content mismatch")
   bundle["bundle_id"]=canonical(bundle);atomic_json(run/"prompt_cache"/(sid_key(row["sample_id"])+".json"),bundle)
   bundle_hashes[row["sample_id"]]=bundle["bundle_id"];source_hashes[str(path)]=bundle["source_native_cache_sha256"]
   levels[str(bundle["source_gate_level"])]+=1;trimcount+=int(bundle["infos"]["E"]["omitted_evidence"]>0)
   if i==0:examples.append(dict(dataset=d,sample_id=row["sample_id"],texts=bundle["texts"],infos=bundle["infos"]))
  print("Frozen dataset",d,len(rows),flush=True)
 require(sum(len(v) for v in rows_by_dataset.values())==1400,"Wrong aggregate membership")
 source=read(OLD/"train_records.json")[0]
 require("::" not in source["sample_id"],"Capacity source probe must not use a target sample")
 atomic_json(run/"train_records.json",[source])
 source_evidence=read(source_cache(p,source["sample_id"]))["evidence"]
 probe=freeze(source_evidence,tokenizer,512)
 probe["expected_prompt_ids"]={}
 for c in CONDITIONS:
  prompt,pi=make_prompt(reader,chat,source,probe,dict(p,variant="base35_"+c))
  probe["expected_prompt_ids"][c]=pi["prompt_id"]
 atomic_json(run/"source_probe_bundle.json",probe)
 atomic_json(run/"prompt_examples.json",examples)
 atomic_json(run/"native_cache_fingerprints.json",source_hashes)
 p["prompt_cache_manifest_id"]=canonical(bundle_hashes)
 p["checkpoint_reports"]=checkpoint_reports
 p["plan_id"]=canonical(p)
 atomic_json(run/"plan.json",p)
 for v in p["variants"]:
  for d,rows in rows_by_dataset.items():
   epoch=p["checkpoint_by_variant"][v]["epoch"];jid=f"{v}_epoch_{epoch}_{d}";shards=[]
   (run/"predictions"/jid).mkdir()
   for start in range(0,len(rows),64):
    stop=min(start+64,len(rows));filename=f"{jid}_{start:04d}.json";shards.append(filename)
    atomic_json(run/"shards"/filename,dict(job_id=jid,variant=v,epoch=epoch,dataset=d,dataset_samples=len(rows),start=start,stop=stop,samples=stop-start,state="pending",attempts=0))
   job=dict(job_id=jid,variant=v,epoch=epoch,dataset=d,samples=len(rows),shards=shards,state="pending")
   atomic_json(run/"jobs"/(jid+".json"),job)
   atomic_json(run/"evaluation_jobs"/(jid+".json"),dict(job_id=jid,state="pending",attempts=0,estimated_seconds=len(rows)*(2 if d=="SIMS" else 1)))
 codepaths=list((ROOT/"amg_prompt_ablation").glob("*.py"))+[ROOT/"amg_inference/model.py",ROOT/"amg_d_graph_compare/common.py",ROOT/"amg_d_graph_compare/policy.py",ROOT/"amg_finetune_nogc/prompts.py",ROOT/"AffectGPT/my_affectgpt/models/tokenizer.py",ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py",ROOT/"AffectGPT/my_affectgpt/conversation/conversation_video.py"]
 atomic_json(run/"code_manifest.json",dict(files={str(path.relative_to(ROOT)):sha(path) for path in codepaths}))
 for path in codepaths:ast.parse(path.read_text())
 require(len(jobs(run))==36,"Job count differs")
 require(sum(read(f)["samples"] for f in (run/"shards").glob("*.json"))==16800,"Shards do not cover all predictions")
 preflight=dict(passed=True,checkpoints=checkpoint_reports,samples=1400,prompts_checked=8400,jobs=36,shards=len(list((run/"shards").glob("*.json"))),predictions=16800,
  gate_levels=dict(levels),shared_budget_trimmed_samples=trimcount,max_graph_tokens=dict(maxgraph),max_prompt_tokens=dict(maxprompt),
  source_only_capacity_sample_id=source["sample_id"],CUDA_initialized=torch.cuda.is_initialized(),checked_at_beijing=now())
 atomic_json(run/"cpu_preflight.json",preflight)
 atomic_json(ROOT/"amg_prompt_ablation/current_run.json",dict(run=str(run),plan_id=p["plan_id"],created_at_beijing=now()))
 print(json.dumps(dict(run=str(run),preflight=preflight),ensure_ascii=False),flush=True)
if __name__=="__main__":main()
