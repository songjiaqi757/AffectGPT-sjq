from graph_paths import hash_matches as _graph_hash_matches
import csv,datetime,json,re,subprocess
from graph_paths import Path
from zoneinfo import ZoneInfo
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .common import ROOT,now
def main():
 stamp=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S")
 run=ROOT/"amg_finetune/runs"/("graph_continue_"+stamp);run.mkdir(parents=True,exist_ok=False)
 cue=read(ROOT/"cue_student/artifacts/current_release.json");release=Path(cue["path"])
 manifest=read(release/"manifest.json");require(manifest["release_id"]==cue["release_id"],"Cue release mismatch")
 for name,digest in manifest["files"].items():require(_graph_hash_matches(release / name, digest, sha(release / name)),"Cue release artifact drift")
 members=read(release/"members.json")
 train=sorted([r for r in members if r["role"] in ["pseudo_train","pseudo_validation"]],key=lambda r:r["sample_id"])
 audit=sorted([r for r in members if r["role"] in ["gold_audit","diagnostic_reserved"]],key=lambda r:r["sample_id"])
 require(len(train)==30755 and len(audit)==500,"Unexpected role sizes")
 require(not ({r["sample_id"] for r in train}&{r["sample_id"] for r in audit}),"Training/audit ID overlap")
 require(not ({r["group_id"] for r in train}&{r["group_id"] for r in audit}),"Training/audit source group overlap")
 p4=read(ROOT/"amg_validation/runs/current.json");runtime=read(ROOT/"amg_runtime/releases/current.json")
 require(p4["runtime_release_id"]==runtime["release_id"],"Runtime mismatch")
 require(read(Path(p4["path"])/"verification_report.json")["passed"],"P4 not verified")
 require(_graph_hash_matches(p4['query_config'], read(Path(p4['path']) / 'selection_manifest.json')['config_sha256'], sha(p4['query_config'])),"Query config changed")
 atomic_json(run/"query_engine_config.json",read(p4["query_config"]))
 data=ROOT/"dataset/mer2025-dataset";label_files={};lookup={};train_ids={r["sample_id"] for r in train}
 for name,field in [("track2_train_mercaptionplus.csv","openset"),("track3_train_mercaptionplus.csv","reason")]:
  p=data/name;label_files[str(p)]=sha(p)
  with p.open() as f:
   rows=list(csv.DictReader(f));require(len({r["name"] for r in rows})==len(rows),"Duplicate original supervision IDs")
   lookup[field]={r["name"]:r[field] for r in rows if r["name"] in train_ids}
 records=[];neutral_fallback=0
 for row in train:
  sid=row["sample_id"];require(sid in lookup["openset"] and sid in lookup["reason"],"Missing original supervision")
  # Original MERCaptionPlus string_to_list normalizes empty sets to neutral.
  raw=lookup["openset"][sid]
  value=raw
  if value.startswith("["):value=value[1:]
  if value.endswith("]"):value=value[:-1]
  values=[v.strip() for v in re.split("['\",]",value) if v.strip() not in ["",","]]
  if not values:values=["neutral"];neutral_fallback+=1
  face=data/"openface_face"/sid/(sid+".npy")
  records.append(dict(sample_id=sid,role="affectgpt_train",previous_role=row["role"],group_id=row["group_id"],subtitle=row["text"].get("english") or "",description=lookup["reason"][sid],ovlabel=", ".join(values),audio_path=row["audio_path"],video_path=row["video_path"],face_path=str(face),text=row["text"],media_assets=row["media_assets"]))
 atomic_json(run/"train_records.json",records)
 safe=[{k:r[k] for k in ["sample_id","text","audio_path","video_path"]} for r in train]
 atomic_json(run/"train_inputs.json",safe)
 for w in [0,1]:atomic_json(run/("cache_inputs_"+str(w)+".json"),safe[w::2])
 audit_records=[dict(r,previous_role=r["role"],role="human_audit",human_annotation_status="not_inferred_from_Teacher_or_previous_role",appraisal_teacher_lookup="Existing appraisal_annotation records; original sample_id preserved",cue_teacher_lookup="Existing cue_annotation records; original sample_id preserved") for r in audit]
 atomic_json(run/"human_audit_500.json",audit_records)
 (run/"human_audit_500_ids.txt").write_text("".join(r["sample_id"]+"\n" for r in audit_records))
 with (run/"human_audit_500.csv").open("w",newline="") as f:
  fields=["sample_id","previous_role","role","group_id","chinese","english","audio_path","video_path","human_annotation_status"]
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in audit_records:w.writerow({k:r.get(k) for k in fields if k not in ["chinese","english"]}|{lang:r["text"].get(lang) or "" for lang in ["chinese","english"]})
 base=ROOT/"AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230"
 checkpoints=[]
 for epoch,gpu in [(30,0),(35,1),(40,0),(45,1),(50,0)]:
  p=next(base.glob(f"checkpoint_{epoch:06d}_*.pth"))
  checkpoints.append(dict(base_epoch=epoch,path=str(p),sha256=sha(p),gpu=gpu,output=str(run/("from_"+str(epoch))),epochs=list(range(epoch+1,epoch+6))))
 original_config_source=base/"log.txt";text=original_config_source.read_text();original_config=json.JSONDecoder().raw_decode(text)[0]
 atomic_json(run/"original_config.json",original_config)
 plan=dict(schema_version="amg_affectgpt_continue_v1",created_at_beijing=now(),purpose="User-requested graph-evidence fine-tuning; separate from frozen-checkpoint zero-shot main experiment",cue_release_path=cue["path"],cue_release_id=cue["release_id"],runtime_path=runtime["path"],runtime_release_id=runtime["release_id"],query_selection_id=p4["selection_release_id"],query_config_path=str(run/"query_engine_config.json"),query_config_id=p4["query_config_id"],graph_release_id=read(run/"query_engine_config.json")["graph_release_id"],cue_profile="engineering",training_count=len(train),audit_count=len(audit),training_ids_digest=canonical([r["sample_id"] for r in train]),audit_ids_digest=canonical([r["sample_id"] for r in audit]),split_policy="User authorized pseudo_train + pseudo_validation for AffectGPT continuation only; gold_audit + diagnostic_reserved become human_audit_500; historical frozen releases retained",independent_validation_available=False,selection_policy="Exactly five additional epochs; save all epochs; no validation/target-based hyperparameter or checkpoint selection",training=dict(additional_epochs=5,iters_per_epoch=5000,batch_size=3,learning_rate=1e-5,weight_decay=.05,seed=42,num_workers=4,max_sequence_tokens=2048,prompt_token_budget=1536,answer_token_budget=510,graph_token_budget=1000,subtitle_token_budget=256,amp="fp16 with restored GradScaler",restore_optimizer=True,restore_scaler=True,lr_schedule="constant continuation at original 1e-5; no new warmup",supervision="Original MERCaptionPlus hybird(description/ovlabel), 50/50 random tasks",original_empty_openset_neutral_fallback_count=neutral_fallback),cache=dict(batch_size=4,loader_workers=4,source="Frozen selected best Cue Students on current raw media only",shared_by_all_five_experiments=True),checkpoints=checkpoints,inputs=dict(train_records_sha256=sha(run/"train_records.json"),train_inputs_sha256=sha(run/"train_inputs.json"),audit_records_sha256=sha(run/"human_audit_500.json"),original_labels_sha256=label_files,query_config_sha256=sha(run/"query_engine_config.json"),original_config_sha256=sha(run/"original_config.json")),limitations=["No independent validation remains after merging; old P4 metrics are parameter-selection results","Original base AffectGPT checkpoints may already have seen historical holdout members; present split does not erase earlier exposure","Engineering Cue policy, human reliability and source/near-duplicate audits remain pending","Frozen graph includes original training co-label statistics; this is in-source graph-augmented training, not out-of-fold evidence"],final_target_evaluation_allowed=False)
 plan["plan_id"]=canonical(plan);atomic_json(run/"plan.json",plan)
 atomic_json(run/"status.json",dict(phase="preparing_graph_evidence",created_at_beijing=now(),plan_id=plan["plan_id"]))
 atomic_json(ROOT/"amg_finetune/runs/current.json",dict(path=str(run),plan_id=plan["plan_id"],training_count=len(train),audit_count=len(audit),status="preparing",final_target_evaluation_allowed=False))
 (run/"EXPERIMENT.md").write_text("# 用户授权的图证据续训实验\n\n30/35/40/45/50五个原始checkpoint分别追加5轮，每轮5000迭代，batch=3。每卡一个独立进程，GPU0依次30/40/50，GPU1依次35/45。\n\n本次训练成员30755条（原pseudo_train 27679 + pseudo_validation 3076）；人工核验500条（原gold_audit 300 + diagnostic_reserved 200），保留原角色与标注来源，不推断已完成任何人工标签。原Cue/图/P4的冻结版本不回写。\n\n无独立验证集；不使用原验证成员进行新参数选择或选模。原图、Cue模型、查询参数冻结。当前微调实验使用工程Cue策略，人工可靠性和来源审计仍未完成。原始AffectGPTcheckpoint的历史训练暴露需单独核验，本次划分不能消除过去暴露。\n\n训练恢复原checkpoint的模型、AdamW和GradScaler，学习率1e-5，不重启warmup。新增续训轮次严格为base+1至base+5。训练上下文上限2048，预留1536 prompt、510答案及BOS/EOS；图证据和字幕按固定预算压缩，不因答案长度改变输入。图分数为关联支持度，不能当概率、因果关系或最终标签。缺少证据时回退原始Prompt。\n\n所有文件仅保存在服务器。\n")
 print(json.dumps(dict(run=str(run),plan_id=plan["plan_id"],training_count=len(train),audit_count=len(audit)),ensure_ascii=False),flush=True)
if __name__=="__main__":main()
