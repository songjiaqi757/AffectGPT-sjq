import copy,datetime
from graph_paths import Path
from .common import ROOT,SOURCE,OLD_INFER,read,canonical,atomic_json,now
from .policy import POLICY
def main():
 root=ROOT/"amg_bcd/runs";root.mkdir(exist_ok=True)
 run=root/("bcd_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S"));run.mkdir()
 old=read(SOURCE/"plan.json");ip=read(OLD_INFER/"plan.json");base=next(x for x in old["checkpoints"] if x["base_epoch"]==35)
 for f in ["original_config.json","train_records.json","train_inputs.json","human_audit_500.json","model_assets_manifest.json","training_execution.json","query_engine_config.json"]:(run/f).symlink_to(SOURCE/f)
 for d in ["jobs","predictions","scores","oof_cache","folds","evaluation_jobs"]:(run/d).mkdir()
 p=copy.deepcopy(old);p.update(schema_version="bcd_pipeline_v1",created_at_beijing=now(),purpose="B compact; C compact+gate; D compact+gate+Graph-OOF",
 source_training_run=str(SOURCE),pipeline_run=str(run),source_cache=str(Path(old["cache"]["source_directory"])),target_cache=str(OLD_INFER/"cache"),base_checkpoint=base,variants=["B","C","D"],epochs=[36,37,38,39,40],
 training_count=30755,audit_count=500,training_run=str(run),datasets={d:ip["datasets"][d] for d in ["MER2023","SIMS","OVMERDPlus"]},
 policy=POLICY,generation=ip["generation"],prompt_question=ip["prompt_question"],seed=42,gpu_training_queues={"0":["B","D"],"1":["C"]},inference_processes_per_gpu=4,logical_jobs=45,dataset_samples_total=1400,sample_predictions_total=21000,
 user_authorized_all_saved_epochs_target_evaluation=True,independent_validation_available=False,
 selection_policy="All 15 checkpoints on three authorized target sets; no target-driven gate/prompt tuning",
 oof_policy=dict(folds=5,seed=42,split_unit="existing source group and exact known media duplicates",fit_pool="original 27679 pseudo_train excluding held fold; original 3076 pseudo_validation already outside graph fitting",cue_models="frozen existing trio; graph-only OOF",emotion_ontology="original mapping; each fold activates only concepts observed outside held groups",inference_graph="same original frozen full graph as C"),
 limitations=old["limitations"]+["All epochs intentionally tested on three target sets by user request; exploratory results.","Gate settings fixed before new target generation; source grouping/near-duplicate and human audits incomplete."])
 p["training"]=copy.deepcopy(old["training"]);p["training"]["graph_token_budget"]=512;p["limits"]=copy.deepcopy(p["training"]);p.pop("plan_id",None);p["plan_id"]=canonical(p);atomic_json(run/"plan.json",p)
 for variant in p["variants"]:
  vp=copy.deepcopy(p);vp["active_variant"]=variant;vp["checkpoints"]=[dict(base,output=str(run/variant),epochs=p["epochs"])];vp.pop("plan_id");vp["plan_id"]=canonical(vp);folder=run/(variant+"_plan");folder.mkdir();atomic_json(folder/"plan.json",vp)
  for f in ["original_config.json","train_records.json","human_audit_500.json","model_assets_manifest.json","training_execution.json","query_engine_config.json"]:(folder/f).symlink_to(run/f)
  atomic_json(folder/"cache_manifest.json",dict(complete=True,samples=30755,plan_id=vp["plan_id"],source="accepted cache; D additionally awaits OOF complete"))
  atomic_json(folder/"preflight_basis.json",dict(cpu_preflight_required=True,basis="same architecture; shorter evidence; real update verification counted inside training"))
  for epoch in p["epochs"]:
   for d,spec in p["datasets"].items():
    jid=f"{variant}_epoch_{epoch}_{d}";atomic_json(run/"jobs"/(jid+".json"),dict(job_id=jid,variant=variant,base_epoch=35,epoch=epoch,dataset=d,samples=spec["samples"],state="pending",attempts=0,plan_id=p["plan_id"]));atomic_json(run/"evaluation_jobs"/(jid+".json"),dict(job_id=jid,state="pending",attempts=0,estimated_seconds=spec["samples"]*(2 if d=="SIMS" else 1)))
 (run/"README.md").write_text("B/C/D start independently from original checkpoint35. Each saves epochs36-40: 5000steps/epoch, batch3, lr1e-5, restored optimizer/scaler, no gradient checkpointing. 30755 train and 500 audit unchanged. GPU0 B then D; GPU1 C. Idle card starts four persistent inference workers; second card joins after training queue. 45 jobs, 21000 predictions; largest available jobs first. Only after all inference exits: one original judge per GPU. D uses graph-only grouped OOF, not full Cue OOF. No target-driven tuning. All files remain on server.\n")
 atomic_json(root/"current.json",dict(path=str(run),plan_id=p["plan_id"]));print(run)
if __name__=="__main__":main()
