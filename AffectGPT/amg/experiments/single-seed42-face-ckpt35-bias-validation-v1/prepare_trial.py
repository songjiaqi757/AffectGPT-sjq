"""Prepare the bounded bias protocol and immutable input/source manifest on server."""
from pathlib import Path
import json
import os
import shutil
from datetime import datetime,timezone
import sys
sys.path.insert(0,"/ai/sjq/AffectGPT-sjq/AffectGPT")
os.environ["CUDA_VISIBLE_DEVICES"]=""
import torch
from amg.adapter_state import adapter_state_hashes,apply_value_last_bias_override,file_sha256
from amg.memory import MemoryAdapter
ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
OUT=ROOT/"amg/experiments/single-seed42-face-ckpt35-bias-validation-v1"
OLD=ROOT/"amg/experiments/single-seed42-face-ckpt35-v1"
INTER=ROOT/"amg/experiments/single-seed42-face-ckpt35-intervention-v1"
torch.set_num_threads(2)
def read(path):return json.loads(Path(path).read_text())
def write(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
p=read(OLD/"protocol.json")
p["schema"]="amg-bias-validation-protocol-v1"
p.pop("methods",None)
p["purpose"]="Bounded single-parameter mechanism intervention and fresh matched seed42 initialization trial"
p["stage"]="old learned-bias inference probe followed by one fresh matched training pair"
p["experiment_directory"]=str(OUT)
p["shared_init"]=str(OUT/"shared-adapter-init.pth")
p["shared_init_metadata"]=p["shared_init"]+".json"
p["shared_init_generator"]=str(OUT/"prepare_shared_init.py")
p["old_retrieval_checkpoint"]=str(OLD/"retrieval/checkpoint_001334.pth")
p["old_retrieval_checkpoint_sha256"]="7c7d254b30922099bdfb88693d6ef4056eae661afd98bdd714dace9576f1b929"
p["old_adapter_fingerprints"]=str(OUT/"old-adapter-fingerprints.json")
p["stages"]=[
 {"name":"A","kind":"inference_only","trained_checkpoint":p["old_retrieval_checkpoint"],
  "change":"Only zero learned memory_adapter.value_projection.2.bias after checkpoint restore",
  "gpu0_memory_mode":"retrieval","gpu1_memory_mode":"random",
  "reused_comparisons":"same-trained-checkpoint normal/off/random predictions; rescore with current evaluator",
  "interpretation":"Out-of-distribution mechanism probe, not evidence about fresh zero-bias training"},
 {"name":"B","kind":"one_matched_training_pair","mode":"retrieval",
  "arms":{"control":{"gpu":0,"value_last_bias_init":"preserve"},
          "zero_init":{"gpu":1,"value_last_bias_init":"zero"}},
  "common_start":"fresh CPU seed42 Adapter serialized once; all LoRA native float32 tensors identical to baseline35",
  "difference":"only value_projection.2.bias at initialization; it remains trainable in both arms",
  "other_training_settings":"exact original 4K budget; no temperature/LR/gate/retriever modifications",
  "after_each_training":["retrieval","off","random"],
  "inference_bias_override":"none; preserve learned final biases",
  "condition":"Always execute after technically valid Stage A, independent of Stage A metrics"}]
p["reference_predictions"]={}
for key,directory,trained,mode in (
    ("normal",OLD/"retrieval","retrieval","retrieval"),
    ("off",INTER/"off","retrieval","off"),
    ("random",INTER/"random","retrieval","random"),
    ("off_trained",OLD/"off","off","off")):
    meta=read(directory/"dev.meta.json")
    p["reference_predictions"][key]={"predictions":str(directory/"dev.jsonl"),
        "metadata":str(directory/"dev.meta.json"),"checkpoint_sha256":meta["amg_sha256"],
        "trained_mode":trained,"memory_mode":mode}
p["decision_rules"]={
 "primary_stage_b_comparison":"zero_init normal retrieval minus control normal retrieval",
 "min_practical_micro_f1_gain":.005,
 "threshold_definition":"preset exploratory +0.5 percentage point, not learned from the new trial results",
 "require_positive_paired_95ci":True,
 "require_content_dependence":"zero_init normal retrieval exceeds its own random and off settings with positive 95% CI",
 "no_prediction_failures":True,
 "same_start_and_actual_exposure_required":True,
 "negative_or_uncertain_result":"Do not expand graph complexity or 31K training on this evidence",
 "positive_result":"Review mechanism/quality and lock a next validation; never auto-expand",
 "formal_significance_claim":False,
 "bootstrap_resamples":1000,"bootstrap_seed":42,
 "multiple_comparisons":"exploratory intervals, no familywise correction"}
p["limitations"]=[
 "Single training seed only; paired bootstrap covers sample uncertainty, not cross-seed stability.",
 "Baseline35 was already supervised on all source31327, including source dev/holdout.",
 "Source normalized open-label microF1 is not the paper's nine-benchmark Emotion Wheel score.",
 "Stage A clears a learned bias at inference, an out-of-distribution intervention.",
 "Stage B uses a fresh CPU shared Adapter initialization; old unsaved initialization is not reconstructed.",
 "Initial zero bias is trainable and can become nonzero; this is not a permanently bias-free architecture.",
 "group_id currently clip ID; cross-clip near-duplicate separation is not claimed.",
 "The final protocol retains all31327 source clips, accepted99 overlaps, full532 OV+; no target scores here.",
 "No holdout, target, full-data, HGT/Situation, or multi-seed jobs are included."]
p["created_at"]=datetime.now(timezone.utc).isoformat()
for path in (OUT/"protocol.json",OUT/"READY.json",Path(p["old_adapter_fingerprints"])):
    if path.exists(): raise FileExistsError(path)
shared=read(p["shared_init_metadata"])
assert shared["tensor_count"]==19 and shared["baseline_lora_tensor_count"]==392
checkpoint=torch.load(p["old_retrieval_checkpoint"],map_location="cpu",weights_only=True,mmap=True)
state={name.removeprefix("memory_adapter."):value for name,value in checkpoint["model"].items()
       if name.startswith("memory_adapter.")}
adapter=MemoryAdapter(d_query=1792,d_value=1792,d_hidden=256,llm_dim=3584,num_tokens=4,num_heads=4)
adapter.load_state_dict(state,strict=True)
original=adapter_state_hashes(adapter)
override=apply_value_last_bias_override(adapter,"zero")
write(p["old_adapter_fingerprints"],{"checkpoint":p["old_retrieval_checkpoint"],
 "checkpoint_sha256":file_sha256(p["old_retrieval_checkpoint"]),
 "original":original,"zero":adapter_state_hashes(adapter),"intervention":override})
write(OUT/"protocol.json",p)
note="""# 单偏置有界验证

这轮只回答 Value MLP 最后一层公共偏置是否影响 Memory 内容的利用，不提前实现完整图。

A：使用原 retrieval 已训练 checkpoint，仅推理时清零 value_projection.2.bias，正常/随机 Memory 各500条双卡并行；与原正常/随机/关闭结果配对。旧预测重新计分，不改旧产物。该操作是训练分布之外的机制探针。

B：随后固定执行一次新的 seed42 训练对照。共享一份CPU seed42新建 Adapter 初值；control完整载入，zero_init只清零该偏置，二者偏置均保持可训练。所有 LoRA 都从第35号基线恢复并逐张量验证。其他参数初值、训练设置、4K曝光和长度预算必须一致。这不声称复现旧训练未保存的初始化。

每组1334 iteration、batch1、accum3，最大4002次实际曝光；只取最终 checkpoint。每组最终权重分别正常/关闭/随机推理各500条，生成后保留学到的偏置，不额外清零。自动检查首五步、实际覆盖、完整曝光一致性和初值差异，再执行配对bootstrap及报告。

预先设定 +0.005 microF1 为探索性的实际增益参考，并查看95%配对区间以及正常相对自身随机/关闭的差异；不据内部token敏感性判断任务改进。单seed、多项探索性比较、baseline已见source等限制保留。不会自动扩展31K/HGT或运行holdout/目标评分。

所有产物只在服务器。本任务启动后用户无需等待持续监测；最新状态见同目录 state.json，完成后 SUMMARY.md / summary.json，技术失败见 FAILURE.txt。
"""
(OUT/"PROTOCOL.md").write_text(note)
tests=(OUT/"unit_tests.log").read_text()
if "\nOK\n" not in tests or "FAILED (" in tests:
    raise RuntimeError("Full CPU test suite must pass before READY is written")
locked=set()
for root in (ROOT/"amg",ROOT/"amg/tests"):
    locked.update(root.glob("*.py"))
for key in ("baseline_checkpoint","config","memory_bank","evaluation_resource",
            "shared_init","shared_init_metadata","old_retrieval_checkpoint",
            "old_adapter_fingerprints","shared_init_generator"):
    locked.add(Path(p[key]))
locked.add(Path(p["memory_bank"]+".json"));locked.add(OUT/"protocol.json")
locked.add(OUT/"PROTOCOL.md");locked.add(OUT/"prepare_trial.py")
locked.add(OUT/"unit_tests.log");locked.add(OUT/"SOURCE_BEFORE.json")
for item in p["splits"].values():locked.add(Path(item["path"]))
for item in p["reference_predictions"].values():
    locked.add(Path(item["predictions"]));locked.add(Path(item["metadata"]))
for relative in ("config.py","my_affectgpt/models/affectgpt.py","my_affectgpt/models/encoder.py",
                 "my_affectgpt/datasets/datasets/base_dataset.py",
                 "my_affectgpt/datasets/datasets/mercaptionplus_dataset.py"):
    locked.add(ROOT/relative)
# Add the initialization's actual local LLM config and relevant preparation inputs.
for name in shared["sources"]:locked.add(Path(name))
for directory in (OLD,INTER):
    for name in ("state.json","protocol.json"):
        if (directory/name).is_file():locked.add(directory/name)
snapshot=OUT/"source_after";snapshot.mkdir()
for path in sorted(locked):
    if path.suffix==".py" and ROOT in path.parents:
        destination=snapshot/path.relative_to(ROOT)
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,destination)
write(OUT/"READY.json",{"schema":"amg-bias-validation-ready-v1",
  "created_at":datetime.now(timezone.utc).isoformat(),"all_artifacts_server_only":True,
  "locked_files":{str(path):file_sha256(path) for path in sorted(locked)}})
print(json.dumps({"protocol":str(OUT/"protocol.json"),"locked_files":len(locked),
                  "shared_adapter_sha256":shared["state_sha256"],
                  "old_adapter_sha256":original["state_sha256"]}))
