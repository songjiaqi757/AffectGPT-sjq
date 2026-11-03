from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path

import ast,copy,collections,importlib.util,runpy,types
from .common import *
from .policy import freeze,make_prompt
def extracted(path,name):
 text=Path(path).read_text();return next(ast.get_source_segment(text,n) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name==name)
def main():
 require(os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU setup only")
 source=ROOT/"amg_d_multistart10/runs/d_multistart10_20261025_160152";old=read(source/"plan.json")
 stamp=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S");run=ROOT/PACKAGE/"runs"/("winner188_"+stamp);run.mkdir(parents=True,exist_ok=False)
 for n in ["jobs","shards","predictions","scores","prompt_cache","generation_cache","judge_cache/openset","judge_cache/sentiment"]:(run/n).mkdir(parents=True)
 p=dict(schema_version="winner188_field_intervention_v1",created_at_beijing=now(),purpose="Diagnose online evidence effects for exact 75.4334 per-dataset winner weights; no training or graph rebuilding",source_run=str(source),graph_release_id=old["graph_release_id"],query_config_id=old["query_config_id"],cue_release_id=old["cue_release_id"],runtime_release_id=old["runtime_release_id"],target_cache=old["target_cache"],source_cache=old["source_cache"],training_run=str(run),training_plan_id=old["plan_id"],datasets=old["datasets"],generation=old["generation"],limits=old["limits"],prompt_question=old["prompt_question"],conditions=list(CONDITIONS),condition_descriptions=CONDITIONS,variants=[],variant_epochs={},variant_bases={},checkpoint_by_variant={},ablation_by_variant={},dataset_by_variant={},historical_anchors={},max_inference_seconds=43200,max_judge_stage_seconds=21600,
  protocol=dict(scope="Exploratory tests already inspected; no tuning or independent generalization claims",gate="Original 188-class native gate frozen before interventions",paths="None A-E; exact retained original paths P",paired_seed="(42+int(canonical(sample_id)[:8],16)) % 2**32",inference_reuse="Only exact within-run checkpoint/sample/media/prompt/seed/config matches; no historical responses reused",scoring="Original repository metric functions/lexicon/judge prompts and temperatures; per-content judge seed plus global cache, labeled new paired protocol",automatic_training=False))
 jp=dict(name="content_seeded_global_cache_v1",model="Qwen25",temperature=.7,top_p=.8,repetition_penalty=1.05,max_tokens=512,batch_size=8,seed="(20261028+int(hash(protocol,stage,exact_input)[:8],16)) % 2**32")
 p["judge_protocol"]=jp;p["judge_protocol_id"]=canonical(jp)
 (run/"original_config.json").write_bytes((source/"original_config.json").read_bytes());atomic_json(run/"evaluation_resources.json",read(source/"evaluation_resources.json"))
 scores=[read(f) for f in (source/"scores").glob("*.json")];winner={}
 for d in p["datasets"]:
  winner[d]=max([x for x in scores if x["dataset"]==d],key=lambda x:x["main_score"]);w=winner[d];p["historical_anchors"][d]=w
  for c in CONDITIONS:
   v="winner_"+d+"_"+c;p["variants"].append(v);p["variant_epochs"][v]=[w["epoch"]];p["variant_bases"][v]=w["base_epoch"];p["checkpoint_by_variant"][v]=w["checkpoint"];p["ablation_by_variant"][v]=c;p["dataset_by_variant"][v]=d
 for path,spec in {v["path"]:v for v in p["checkpoint_by_variant"].values()}.items():require(_graph_hash_matches(path, spec['sha256'], sha(path)),"Checkpoint hash mismatch")
 cfg=read(run/"original_config.json");require(all(cfg["model"][k]==1 for k in ["num_audio_query_token","num_video_query_token","num_multi_query_token","num_image_query_token"]),"Token expansion assumption changed")
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));config=types.SimpleNamespace(**runpy.run_path("config.py"))
 from transformers import AutoTokenizer
 scope=dict(AutoTokenizer=AutoTokenizer,config=config);exec(extracted(ROOT/"AffectGPT/my_affectgpt/models/tokenizer.py","load_tokenizer_from_LLM"),scope)
 tokenizer=scope["load_tokenizer_from_LLM"]("Qwen25");scope={};exec(extracted(ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py","get_prompt_for_multimodal"),scope)
 reader=types.SimpleNamespace();reader.get_prompt_for_multimodal=types.MethodType(scope["get_prompt_for_multimodal"],reader)
 chat=types.SimpleNamespace(tokenizer=tokenizer,replace_token_for_multimodal=lambda x:x)
 logical=0;unique=set();levels=collections.Counter();source_hashes={};input_assets={};examples=[];max_tokens=0;anchors_checked=0
 rows_by_dataset={}
 for d,di in p["datasets"].items():
  require(_graph_hash_matches(di['path'], di['sha256'], sha(di['path'])),"Dataset drift");rows=read(di["path"]);rows_by_dataset[d]=rows;w=winner[d];oldjob=read(source/"jobs"/(w["job_id"]+".json"))
  previous={x["name"]:x for x in (json.loads(l) for l in open(_graph_resolve_path(oldjob['prediction_path'])))}
  require(len(previous)==len(rows)==di["samples"],"Anchor membership mismatch")
  require(_graph_hash_matches(w['raw_path'], w['raw_sha256'], sha(w['raw_path'])),"Historical raw changed")
  for row in rows:
   for k in ["audio_path","face_path"]:
    f=Path(row[k]);st=f.stat();input_assets[str(f)]=dict(bytes=st.st_size,mtime_ns=st.st_mtime_ns)
   cp=Path(p["target_cache"])/(sid_key(row["sample_id"])+".json");cached=read(cp)
   require(cached["cache_id"]==canonical({k:v for k,v in cached.items() if k!="cache_id"}),"Native cache identity drift")
   e=cached["evidence"];require(e["graph_release_id"]==p["graph_release_id"] and e["query_config_id"]==p["query_config_id"],"Wrong graph/query cache")
   bundle=freeze(e,tokenizer);bundle["expected_prompt_ids"]={}
   for c in CONDITIONS:
    v="winner_"+d+"_"+c;prompt,info=make_prompt(reader,chat,row,bundle,dict(p,variant=v))
    bundle["expected_prompt_ids"][c]=info["prompt_id"];max_tokens=max(max_tokens,info["prompt_tokens"])
    key=canonical(dict(checkpoint=w["checkpoint"]["sha256"],sample_id=row["sample_id"],prompt_id=info["prompt_id"],seed=(42+int(canonical(row["sample_id"])[:8],16))%2**32,generation=p["generation"],dataset_input=di["sha256"]))
    unique.add(key)
    require((c in ["C","E","P"] or info["appraisals_displayed"]==0) and (c in ["D","E","P"] or info["emotion_candidates_displayed"]==0),"Hidden field leakage")
    if c=="P":
     require(info["prompt_id"]==previous[row["name"]]["prompt_info"]["prompt_id"],"P prompt is not exact historical prompt")
     require(previous[row["name"]]["seed"]==(42+int(canonical(row["sample_id"])[:8],16))%2**32,"Historical seed mismatch")
     anchors_checked+=1
   bundle["bundle_id"]=canonical(bundle);atomic_json(run/"prompt_cache"/(sid_key(row["sample_id"])+".json"),bundle)
   source_hashes[str(cp)]=sha(cp);levels[str(bundle["source_gate_level"])]+=1
   if not any(x["dataset"]==d for x in examples):examples.append(dict(dataset=d,sample_id=row["sample_id"],texts=bundle["texts"]))
  logical+=len(rows)*len(CONDITIONS);print("FROZEN",d,len(rows),flush=True)
 source_row=read(source/"train_records.json")[0];atomic_json(run/"train_records.json",[source_row])
 probe=freeze(read(Path(p["source_cache"])/(source_row["sample_id"]+".json"))["evidence"],tokenizer)
 probe["expected_prompt_ids"]={}
 for c in CONDITIONS:probe["expected_prompt_ids"][c]=make_prompt(reader,chat,source_row,probe,dict(p,variant=p["variants"][list(CONDITIONS).index(c)]))[1]["prompt_id"]
 atomic_json(run/"source_probe_bundle.json",probe);atomic_json(run/"prompt_examples.json",examples);atomic_json(run/"native_cache_fingerprints.json",source_hashes);atomic_json(run/"input_assets.json",input_assets)
 p.update(logical_jobs=len(p["variants"]),dataset_samples_total=sum(x["samples"] for x in p["datasets"].values()),sample_predictions_total=logical,unique_generation_inputs=len(unique),inference_processes_per_gpu=4,gpus=[0,1],unique_checkpoints=len({x["sha256"] for x in p["checkpoint_by_variant"].values()}))
 p["plan_id"]=canonical(p);atomic_json(run/"plan.json",p)
 for v in p["variants"]:
  d=p["dataset_by_variant"][v];rows=rows_by_dataset[d];epoch=p["checkpoint_by_variant"][v]["epoch"];jid=v;shards=[];(run/"predictions"/jid).mkdir()
  for start in range(0,len(rows),64):
   stop=min(start+64,len(rows));fn=f"{jid}_{start:04d}.json";shards.append(fn);atomic_json(run/"shards"/fn,dict(job_id=jid,variant=v,epoch=epoch,dataset=d,dataset_samples=len(rows),start=start,stop=stop,samples=stop-start,state="pending",attempts=0))
  atomic_json(run/"jobs"/(jid+".json"),dict(job_id=jid,variant=v,epoch=epoch,dataset=d,samples=len(rows),shards=shards,state="pending"))
 # Reference labels are isolated from inference records/prompt bundles.
 helpers=runpy.run_path(str(ROOT/"analysis_reports/sample_audit_75_43_20261028/common.py"));atomic_json(run/"references.json",helpers["refs"])
 # Inventory official validation candidates. No claim that initial/base pretraining did not see these media.
 import numpy as np
 train=read(source/"train_records.json");trainids={x["sample_id"] for x in train};testnames={r["name"] for rs in rows_by_dataset.values() for r in rs}
 dev={}
 for d in ["MELD","CMUMOSI","CMUMOSEI","SIMS","SIMSv2"]:
  label=(ROOT/"AffectGPT"/config.PATH_TO_LABEL[d]).resolve();z=np.load(_graph_resolve_path(label), allow_pickle=True);cor=z["val_corpus"].item();names=sorted(cor)
  eligible=[n for n in names if n not in trainids and n not in testnames]
  ordered=sorted(eligible,key=lambda n:canonical("candidate-dev-v1::"+d+"::"+n));selected=ordered[:256]
  dev[d]=dict(label_path=str(label),label_sha256=sha(label),split="val_corpus",official_count=len(names),name_disjoint_candidates=len(eligible),candidate_names=selected,candidate_count=len(selected),status="candidate_only_not_admitted",requires=["exact-media overlap with source training and nine tests","video/speaker/group overlap and base/Cue pretraining exposure audit","input quality and labels checked before fitting or selection"])
 atomic_json(run/"dev_inventory.json",dev)
 atomic_json(run/"research_program.json",dict(stage1=dict(status="prepared",run=str(run),purpose="188-class evidence intervention, diagnostic only"),stage2=dict(status="gated_by_dev_admission",candidate_count=sum(x["candidate_count"] for x in dev.values()),arms=["no extra evidence","Cue only","Cue plus grounded speaker/time/target/negation/scope evidence"],scope="At most two fixed strong checkpoints; identical media/random streams; no test-label evidence; no automatic training"),stage3=dict(status="gated_by_stage2",base="one preregistered strong original checkpoint",arms=["T0 matched no-graph continuation","T1 explicit overall sentiment task separated from emotion","T2 T1 + validated semantic evidence","T3 validity Appraisal only if incremental value demonstrated"],budget="pilot5000 optimizer steps/arm with same data order, resume policy and batch; expand to3 seeds only after dev net benefit; LR candidates2e-6/1e-5 require preregistration before fitting",forbidden=["training on238 inspected test cases then reporting original-test gain","automatic graph rebuild/checkpoint sweep"])))
 paths=list((ROOT/PACKAGE).glob("*.py"))+[ROOT/"amg_inference/model.py",ROOT/"amg_d_multistart10/policy.py",ROOT/"amg_finetune_nogc/prompts.py",ROOT/"AffectGPT/my_affectgpt/conversation/conversation_video.py",ROOT/"AffectGPT/my_affectgpt/models/tokenizer.py",ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py",ROOT/"AffectGPT/toolkit/utils/qwen.py",ROOT/"AffectGPT/my_affectgpt/evaluation/ew_metric.py",ROOT/"AffectGPT/evaluation.py",ROOT/"analysis_reports/sample_audit_75_43_20261028/common.py"]
 for f in paths:ast.parse(f.read_text())
 atomic_json(run/"code_manifest.json",dict(files={str(f.relative_to(ROOT)):sha(f) for f in paths}))
 require(len(jobs(run))==54 and logical==76794 and anchors_checked==12799,"Cardinality mismatch")
 pre=dict(passed=True,jobs=54,logical_predictions=logical,unique_generation_inputs=len(unique),eliminated_identical_prompt_generations=logical-len(unique),historical_P_prompt_seed_matches=anchors_checked,max_prompt_tokens=max_tokens,gate_levels=dict(levels),unique_checkpoints=p["unique_checkpoints"],dev_candidate_count=sum(x["candidate_count"] for x in dev.values()),CUDA_initialized=__import__("torch").cuda.is_initialized(),time_beijing=now())
 atomic_json(run/"cpu_preflight.json",pre);atomic_json(ROOT/PACKAGE/"current_run.json",dict(run=str(run),plan_id=p["plan_id"]))
 print(json.dumps(dict(run=str(run),preflight=pre),ensure_ascii=False),flush=True)
if __name__=="__main__":main()
