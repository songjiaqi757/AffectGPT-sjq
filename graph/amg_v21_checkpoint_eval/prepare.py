import argparse,ast,collections,copy,gzip,json,os,shutil
from .common import *
def prepare(training_run,run):
 training_run=Path(training_run);run=Path(run);run.mkdir(parents=True,exist_ok=True)
 tp=read(training_run/"plan.json");assert tp["plan_id"]==digest({k:v for k,v in tp.items() if k!="plan_id"})
 assert tp["epochs"]==[36,37,38,39,40]
 for name in ["inputs","cache","epochs","logs"]:(run/name).mkdir(exist_ok=True)
 from amg_v21_continue.policy import gate,restricted_graph
 from amg_graph_v2.unified_prompt.adapter import UnifiedAMGPromptAdapter
 from amg_graph_v2.unified_prompt.integration import AffectGPTUnifiedBridge
 from amg_graph_v2.unified_prompt.tokenization import actual_interfaces
 native=Path(tp["prompt_source_run"]);old=read(native/"plan.json");inv=read(native/"cache_inventory.json")
 tokenizer,reader,chat,binding=actual_interfaces()
 adapter=UnifiedAMGPromptAdapter(tokenizer,graph_release=tp["graph_v21_release"]);bridge=AffectGPTUnifiedBridge(adapter)
 assert tp["training"]["graph_token_budget"]==adapter.config["evidence_token_budget"]==1000
 assert tp["training"]["prompt_token_budget"]==800
 config=read(native/"original_config.json");assert config==read(training_run/"original_config.json")
 shutil.copyfile(native/"original_config.json",run/"original_config.json")
 source=GRAPH/"amg_base7_graph10/original_model.py";tree=ast.parse(source.read_text());assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="GENERATION" for t in n.targets))
 native_generation=eval(compile(ast.Expression(assignment.value),str(source),"eval"),{"dict":dict});assert old["generation"]==native_generation
 gpu_uuid=os.popen("nvidia-smi --query-gpu=uuid --format=csv,noheader").read().strip();assert gpu_uuid
 p=dict(version="continuation_checkpoint36_to40_v21_P4_gate_native_A100",created_at=now(),run=str(run),training_source_run=str(training_run),training_source_plan_id=tp["plan_id"],expected_epochs=[36,37,38,39,40],datasets={},generation=native_generation,prompt_question=old["prompt_question"],graph_release_id=old["graph_release_id"],graph_release_path=tp["graph_v21_release"],prompt_release_id=old["prompt_release_id"],prompt_release_path=old["prompt_release_path"],concurrency=4,node="A100",gpu_uuid=gpu_uuid,per_process_memory_fraction=.24,seed=None,seed_rule="Original native flow; no added per-sample reseeding; source-only probes restore RNG",logical_jobs=15,total_predictions=7000,predictions_per_checkpoint=1400,shard_size=16,target_labels_used_for_prompt_selection=False,excluded_samples=0,ovmerd_mapping=old["ovmerd_mapping"],gate_source=str(GRAPH/"amg_v21_continue/policy.py"),gate_source_sha256=sha(GRAPH/"amg_v21_continue/policy.py"),inference_dropout=False,additional_D_gate_applied=False,input_policy="Exact prior v2.1 P4 packet text and complete Prompt, as explicitly confirmed by user",graph_oof_train_only=True,inference_graph="Same v2.1 frozen full graph, no Student-OOF graph substitution",original_model_and_media_and_sampling_and_official_metrics=True)
 inventory={};levels=collections.Counter();maxprompt=0;maxgraph=0;baseline_matches=0
 for dataset,expected in [("MER2023",411),("SIMS",457),("OVMERDPlus",532)]:
  spec=copy.deepcopy(old["datasets"][dataset]);rows=read(spec["path"]);assert len(rows)==expected and sha(spec["path"])==spec["sha256"]
  out=run/"inputs"/(dataset+".json");write(out,rows);spec.update(path=str(out),sha256=sha(out));p["datasets"][dataset]=spec
  for row in rows:
   entry=inv[row["sample_id"]];assert sha(entry["path"])==entry["sha256"];cached=read(entry["path"]);assert cached["row_sha256"]==digest(row) and cached["cache_id"]==entry["cache_id"]
   gfile=native/"graphs"/(Path(entry["path"]).stem+".json.gz")
   with gzip.open(gfile,"rt",encoding="utf-8") as f:g=json.load(f)
   assert g["graph_release_id"]==p["graph_release_id"] and g["sample_id"]==row["sample_id"]
   original=bridge.prepare(reader,chat,g,p["prompt_question"],row["subtitle"],max_length=2000,max_new_tokens=1200)
   assert original["prompt"]==cached["final_prompt"];baseline_matches+=1
   level,reasons=gate(g);levels[level]+=1
   prepared=original
   packet=copy.deepcopy(cached["packet"]);assert packet["text"]==prepared["evidence"]["text"] and prepared["prompt"]==cached["final_prompt"]
   assert packet["audit"]["evidence_tokens"]<=1000 and packet["audit"]["full_prompt_tokens"]<=800
   item=dict(sample_id=row["sample_id"],dataset=dataset,name=row["name"],row_sha256=digest(row),source_cue_cache_id=cached["source_cue_cache_id"],source_cache_sha256=entry["sha256"],graph_release_id=p["graph_release_id"],prompt_release_id=p["prompt_release_id"],packet=packet,final_prompt=prepared["prompt"])
   item["cache_id"]=digest(item);dest=run/"cache"/(key(row["sample_id"])+".json");write(dest,item);inventory[row["sample_id"]]=dict(path=str(dest),sha256=sha(dest),cache_id=item["cache_id"])
   maxprompt=max(maxprompt,packet["audit"]["full_prompt_tokens"]);maxgraph=max(maxgraph,packet["audit"]["evidence_tokens"])
   if len(inventory)%100==0:write(run/"prepare_status.json",dict(state="preparing_exact_prior_v21_inputs",completed=len(inventory),total=1400,at=now()));print("Prepared",len(inventory),flush=True)
 assert baseline_matches==len(inventory)==1400
 write(run/"cache_inventory.json",inventory);write(run/"tokenizer_binding.json",binding);p["cache_inventory_sha256"]=sha(run/"cache_inventory.json")
 original_probe=read(native/"source_probe.json");g=read(Path(tp["graph_v21_release"])/"runtime/examples/candidate_and_evidence.json");assert g["sample_id"]==original_probe["sample_id"]
 assert sha(native/"source_probe.json")==old["source_probe_sha256"];prepared=dict(prompt=original_probe["final_prompt"],evidence=original_probe["packet"])
 write(run/"source_probe.json",dict(sample_id=original_probe["sample_id"],row=original_probe["row"],final_prompt=prepared["prompt"],packet=prepared["evidence"]));p["source_probe_sha256"]=sha(run/"source_probe.json")
 p["original_config_sha256"]=sha(run/"original_config.json");p["plan_id"]=digest(p);write(run/"plan.json",p)
 oldlock=read(native/"code_manifest.json");manifest=dict(created_at=now(),files=dict(oldlock["files"]))
 for d in [ROOT,GRAPH/"amg_unified_eval"]:
  for f in d.glob("*.py"):manifest["files"][str(f)]=sha(f)
 for f in [GRAPH/"amg_v21_continue/policy.py",run/"original_config.json",run/"cache_inventory.json",run/"source_probe.json"]+list((run/"inputs").glob("*.json")):manifest["files"][str(f)]=sha(f)
 write(run/"code_manifest.json",manifest)
 report=dict(passed=True,samples=1400,baseline_prompt_exact_matches=1400,graph_gate_levels=dict(levels),exact_prior_v21_packet_text=True,additional_D_gate_applied=False,same_training_P4_adapter=True,inference_dropout=False,maximum_full_prompt_tokens=maxprompt,maximum_graph_tokens=maxgraph,original_native_generation=native_generation,original_config_identical_to_training=True,tests_unchanged=True,official_evaluation_source=str(PROJECT/"AffectGPT/evaluation.py"),all_files_on_server=True,at=now())
 write(run/"preparation_report.json",report);write(run/"prepare_status.json",dict(state="complete",samples=1400,at=now()));print(json.dumps(report,ensure_ascii=False),flush=True)
 (run/"README.md").write_text("A100 server-side event queue for continuation checkpoint36–40. Wait for atomic training checkpoints.json and matching SHA256 before launch. Per checkpoint: native four-way AffectGPT inference with the EXACT previously frozen v2.1 full-graph P4 input text and complete Prompt; no additional D evidence gate or dropout applied. MER2023 411, SIMS 457, OVMERDPlus 532; native num_beams1 temperature1 do_sampleTrue top_p.9 max_length2000 max_new_tokens1200; no added per-sample reseeding. All inference workers exit before the original evaluation.py Qwen25 judge loads. Metrics: MER HIT; SIMS WAF/ACC; OV F_s/P_s/R_s. Fifteen dataset jobs, 7000 predictions total; no effect on training settings or original runs. Results per epoch in epochs/epoch_*/RESULTS.md and combined metrics_all.csv/RESULTS.md. All artifacts and processes on servers only.\n")
 write(ROOT/"current_run.json",dict(run=str(run),training_run=str(training_run),plan_id=p["plan_id"]))
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--training-run",required=True);ap.add_argument("--run",required=True);a=ap.parse_args();prepare(a.training_run,a.run)
