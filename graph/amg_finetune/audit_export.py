"""Human-audit worksheet: union of the previous 300 and 200 members; no invented labels."""
import csv,random
from graph_paths import Path
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .common import ROOT,now
def main():
 run=Path(read(ROOT/"amg_finetune/runs/current.json")["path"]);members=read(run/"human_audit_500.json");plan=read(run/"plan.json")
 original=read(Path(plan["cue_release_path"])/"manifest.json")["split"].get("double_annotation_sample_ids",[])
 ids={r["sample_id"] for r in members};chosen=[sid for sid in original if sid in ids]
 remaining=sorted(ids-set(chosen));random.Random(43).shuffle(remaining);chosen+=remaining[:max(0,150-len(chosen))]
 require(len(set(chosen))>=150,"Double-annotation recommendation incomplete")
 dimensions=["APP_GOAL_RELEVANCE","APP_GOAL_CONGRUENCE","APP_EXPECTEDNESS","APP_AGENCY","APP_CERTAINTY","APP_COPING_POTENTIAL"]
 fields=["sample_id","previous_role","double_annotation_required","audio_path","video_path","chinese","english","rater_a","rater_b"]+[f"{d}_{suffix}" for d in dimensions for suffix in ["a","a_evidence","b","b_evidence","adjudicated","unknown_reason"]]+["cue_labels_a_json","cue_labels_b_json","adjudication_notes"]
 with (run/"human_audit_500_annotation_template.csv").open("w",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for r in members:
   writer.writerow(dict(sample_id=r["sample_id"],previous_role=r["previous_role"],double_annotation_required=r["sample_id"] in set(chosen),audio_path=r["audio_path"],video_path=r["video_path"],chinese=r["text"].get("chinese") or "",english=r["text"].get("english") or ""))
 atomic_json(run/"human_audit_protocol.json",dict(created_at_beijing=now(),members=500,source_roles=dict(gold_audit=300,diagnostic_reserved=200),training_excluded=True,sample_ids_digest=plan["audit_ids_digest"],human_labels_populated=False,independent_annotation_required=True,preserve_pre_adjudication_labels=True,minimum_double_annotation=150,double_annotation_sample_ids=chosen,seed=43,prior_double_annotation_members_preserved=original,worksheet_sha256=sha(run/"human_audit_500_annotation_template.csv"),historical_checkpoint_exposure="Original base checkpoints may have seen these members; this union is excluded from new continuation only"))
 print("EXPORTED human_audit_500_annotation_template.csv",flush=True)
if __name__=="__main__":main()
