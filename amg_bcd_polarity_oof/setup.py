"""Create source-frozen B/C/D polarity experiment, original checkpoint35."""
import copy,datetime
from pathlib import Path
from .common import *
from .policy import POLICY
VARIANTS={"B":dict(graph_probability=.5,polarity_loss_weight=0.0),"C":dict(graph_probability=1.0,polarity_loss_weight=.1),"D":dict(graph_probability=.5,polarity_loss_weight=.1)}
def main():
 root=ROOT/"amg_bcd_polarity_oof/runs";root.mkdir(exist_ok=True)
 run=root/("bcd_polarity_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S"));run.mkdir()
 old=read(SOURCE/"plan.json");ip=read(OLD_INFER/"plan.json");base=copy.deepcopy(next(x for x in old["checkpoints"] if x["base_epoch"]==35))
 polarity=Path(read(ROOT/"amg_polarity/current.json")["path"]);pr=read(polarity/"summary.json")
 require(pr["passed"] and pr["samples"]==30755 and pr["valid_for_polarity_loss"]==30688,"Polarity annotation incomplete")
 require(sha(polarity/"polarity_labels.json")==pr["files_sha256"]["polarity_labels.json"],"Polarity label checksum changed")
 for f in ["original_config.json","train_records.json","train_inputs.json","human_audit_500.json","model_assets_manifest.json","training_execution.json","query_engine_config.json"]:(run/f).symlink_to(SOURCE/f)
 (run/"cache").symlink_to(SOURCE/"cache");(run/"polarity_labels.json").symlink_to(polarity/"polarity_labels.json")
 for d in ["jobs","predictions","scores","evaluation_jobs","shards"]:(run/d).mkdir()
 p=copy.deepcopy(old);p.update(schema_version="bcd_polarity_oof_pipeline_v1",created_at_beijing=now(),purpose="B 50% graph/no polarity; C full graph+polarity; D 50% graph+polarity; independently continue original checkpoint35 for five epochs",
 source_training_run=str(SOURCE),pipeline_run=str(run),source_cache=str(Path(old["cache"]["source_directory"])),target_cache=str(OLD_INFER/"cache"),base_checkpoint=base,variants=["B","C","D"],variant_settings=VARIANTS,epochs=[36,37,38,39,40],training_run=str(run),datasets={d:ip["datasets"][d] for d in ["MER2023","SIMS","OVMERDPlus"]},
 polarity_run=str(polarity),polarity_plan_id=pr["plan_id"],polarity_labels_sha256=pr["files_sha256"]["polarity_labels.json"],polarity_label_mapping=pr["id_mapping"],polarity_valid_samples=30688,polarity_ignored_samples=67,
 polarity_method=dict(head="Linear(hidden_size,3), deterministic fresh initialization with isolated RNG seed4242",pooling="last unsupervised prompt token at final Qwen norm; causal prefix only",loss="unweighted cross-entropy mean over valid examples; zero when none valid",existing_optimizer="restore original two AdamW groups, add fresh third group only for head",head_checkpoint="saved separately from model; generation inference uses original AffectGPT and original metric functions"),
 graph_dropout=dict(probability=.5,variants=["B","D"],seed=42,method="deterministic Bernoulli hash(sample_id,worker-local sample visit); same mask stream for B and D; resampled on later visits",only_training=True,inference="full original frozen graph evidence; no dropout"),
 gpu_training_queues={"0":["C","D"],"1":["B"]},inference_processes_per_gpu=4,logical_jobs=45,dataset_samples_total=1400,sample_predictions_total=21000,generation=ip["generation"],prompt_question=ip["prompt_question"],limits=copy.deepcopy(old["training"]),seed=42,
 inference_schedule="shared exclusive shards of <=64 samples, largest dataset and shard first among saved checkpoints; free GPU starts four workers, other GPU joins after its queue; same per-sample seed across variants and epochs",
 user_authorized_all_saved_epochs_target_evaluation=True,selection_policy="All 15 saved weights x all three requested target sets; fixed graph ratio and auxiliary coefficient chosen before targets; no target-driven hyperparameter selection",independent_validation_available=False,
 limitations=old["limitations"]+["Source polarity labels are Qwen pseudo labels, not human gold;67 abstentions excluded only from auxiliary loss","These are exploratory target test comparisons; no independent validation added"])
 oof=ROOT/"amg_bcd/runs/bcd_20261024_161459";op=read(oof/"plan.json");om=read(oof/"oof_manifest.json")
 require(om["complete"] and om["samples"]==30755 and sha(oof/"train_records.json")==sha(SOURCE/"train_records.json"),"Old OOF cache has different source data")
 folds={}
 for fold in range(5):
  fm=read(oof/"folds"/str(fold)/"manifest.json");cfg=read(oof/"folds"/str(fold)/"query_config.json")
  folds[str(fold)]=dict(graph_id=fm["graph_release_id"],query_config_id=canonical(cfg),manifest_sha256=sha(oof/"folds"/str(fold)/"manifest.json"))
 p.update(oof_reference_run=str(oof),oof_reference_plan_id=op["plan_id"],oof_cache=str(oof/"oof_cache"),oof_manifest_sha256=sha(oof/"oof_manifest.json"),oof_assignment_sha256=sha(oof/"fold_assignment.json"),oof_folds=folds,oof_cache_inventory_path=str(run/"oof_cache_inventory.json"),oof_verification_path=str(run/"oof_reuse_verification.json"),oof_policy=op["oof_policy"],policy=POLICY,evidence_base="Previous D: compact evidence + confidence gate + grouped Graph-OOF for all B,C,D",old_training_dropout_replaced=True)
 p["training"]=copy.deepcopy(old["training"]);p["training"]["graph_token_budget"]=512;p["training"]["supervision"]+="; auxiliary polarity only for C,D"
 p["limits"]=copy.deepcopy(p["training"])
 p.pop("plan_id",None);p["plan_id"]=canonical(p);atomic_json(run/"plan.json",p)
 for variant in p["variants"]:
  vp=copy.deepcopy(p);vp["active_variant"]=variant;vp["checkpoints"]=[dict(base,output=str(run/variant),epochs=p["epochs"])]
  vp.pop("plan_id");vp["plan_id"]=canonical(vp);folder=run/(variant+"_plan");folder.mkdir();atomic_json(folder/"plan.json",vp)
  for f in ["original_config.json","train_records.json","human_audit_500.json","model_assets_manifest.json","training_execution.json","query_engine_config.json","polarity_labels.json"]:(folder/f).symlink_to(run/f)
  (folder/"cache").symlink_to(run/"cache")
  for name in ["oof_cache_inventory.json","oof_reuse_verification.json"]:(folder/name).symlink_to(run/name)
  atomic_json(folder/"cache_manifest.json",dict(complete=True,samples=30755,plan_id=vp["plan_id"],source="accepted grouped Graph-OOF cache; compact formatter plus confidence gate"))
  for epoch in p["epochs"]:
   for d,spec in p["datasets"].items():
    jid=f"{variant}_epoch_{epoch}_{d}";j=dict(job_id=jid,variant=variant,base_epoch=35,epoch=epoch,dataset=d,samples=spec["samples"],state="pending",attempts=0,plan_id=p["plan_id"],shards=[])
    for lo in range(0,j["samples"],64):
     name=jid+f"_{lo:04d}.json";j["shards"].append(name)
     atomic_json(run/"shards"/name,dict(job_id=jid,variant=variant,epoch=epoch,dataset=d,dataset_samples=j["samples"],start=lo,stop=min(lo+64,j["samples"]),samples=min(64,j["samples"]-lo),state="pending",attempts=0))
    atomic_json(run/"jobs"/(jid+".json"),j);atomic_json(run/"evaluation_jobs"/(jid+".json"),dict(job_id=jid,state="pending",attempts=0,estimated_seconds={"MER2023":14,"SIMS":22,"OVMERDPlus":19}[d]))
 (run/"README.md").write_text("# B/C/D 图证据混用与极性损失实验\n\nB=训练50%概率加图、无极性损失；C=全量加图、有极性损失；D=训练50%概率加图、有极性损失。C/D固定 lambda=0.1，未使用目标测试结果调参。复用旧D的紧凑图格式与门控，三组训练均用其Graph-OOF证据；原始音视频字幕、数据、学习率、每轮步数保持此前设置，不使用梯度检查点。三组各从最原始 checkpoint35 独立开始，每组5轮（36–40），共15权重。\n\n训练集30755条，500条人工核验排除。源域极性伪标签30688条有效，67条待核验只跳过极性损失；原始生成训练仍使用全部样本。极性头读取Qwen最后一个提示词位置的隐藏表示，因果注意力不读取答案；分类头独立存储，推理仍用原始生成接口。\n\nGPU0先C再D，GPU1训练B；每卡训练时只有一个进程。GPU1先结束后自动四路推理，GPU0训练队列结束后加入四路推理。15权重×MER2023(411)、SIMS(457)、OVMERDPlus(532)，45项、21000样本预测。按数据量降序，任务拆成至多64样本的互斥共享分片，尽量平衡两卡；所有推理均使用完整源图（不使用目标数据建图），并沿用相同紧凑格式与门控。旧D的随机20%整图/20%情绪丢弃由本次50%或100%保留设置替代，不重复叠加。\n\n全部45项推理完成、所有推理进程退出、两卡显存释放后，自动启动每卡一个原版Qwen25测评进程。主指标MER2023 HIT、SIMS WAF/ACC、OVMERDPlus F_s/P_s/R_s。输出metrics_all.csv、per_checkpoint_summary.csv和RESULTS.md。\n\n所有源代码、权重、日志及结果仅保存在服务器；不改写历史实验。\n")
 atomic_json(root/"current.json",dict(path=str(run),plan_id=p["plan_id"]));print(run)
if __name__=="__main__":main()
