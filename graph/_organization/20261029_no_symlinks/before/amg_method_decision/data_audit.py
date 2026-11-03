"""Server-only data admission audit for the method decision program."""
import os,sys,csv,json,re,hashlib,collections,datetime,concurrent.futures
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import soundfile as sf
sys.path.insert(0,"/ai/sjq/AffectGPT-sjq")
from amg_d_graph_compare.common import ROOT,read,sha,canonical,atomic_json,now
ROOTDIR=ROOT/"amg_method_decision"
SOURCE=ROOT/"amg_188_path_noemotion/runs/path_noemotion_20261028_170538"
def rows(path):
 with Path(path).open() as f:return list(csv.DictReader(f))
def norm(t):return re.sub(r"[\W_]+","",(t or "").casefold(),flags=re.UNICODE)
def pcm_digest(path):
 x,sr=sf.read(path,dtype="int16",always_2d=True)
 h=hashlib.sha256();h.update(str((sr,x.shape)).encode());h.update(x.tobytes())
 return h.hexdigest(),len(x)/sr
def inspect(item):
 n,record=item
 try:
  p=Path(record["audio_path"]);digest,dur=pcm_digest(p)
  return n,dict(audio_sha256=sha(p),pcm_sha256=digest,audio_duration=dur,video_bytes=Path(record["video_path"]).stat().st_size,face_bytes=Path(record["face_path"]).stat().st_size)
 except Exception as e:return n,dict(error=repr(e))
def main():
 stamp=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S")
 run=ROOTDIR/"runs"/("decision_"+stamp);run.mkdir(parents=True)
 for d in ["audit","data","cue_cache","prompt_cache","predictions","scores","analysis","workers"]:(run/d).mkdir()
 atomic_json(ROOTDIR/"current_run.json",dict(run=str(run),created_at_beijing=now()))
 protocol=dict(schema="finite_method_decision_v1",created_at_beijing=now(),project=str(ROOT),execution="Server only; two physical single-GPU hosts, four inference workers each; serialize A100 model/checkpoint loading",scheduling="Shared whole-sample task queue with exclusive locks; all arms for one sample stay on one GPU",phase0="Locate media, exclude all known base/Cue/graph/continuation sample IDs and nine inspected tests; audio exact+PCM, long-text duplicate checks; preserve source-unknown flag",checkpoints=["original_epoch40","fixed_graph45_to54"],seeds=[42,2026,2027],primary_conditions={"A":"No extra evidence","B":"Cue only","C":"Cue+original Appraisal, no Emotion/path","S":"Cue+donor-shuffled Appraisal matched in dimensionality/state-count/length; actual intervention audited","P":"Original complete frozen graph prompt"},development_max={"MER_track1":384,"MER_OV":128},confirmation_max={"MER_track1":384,"MER_OV":128},selection="Use new development only to freeze simplest candidate before opening confirmation outcomes. Never select by nine inspected tests or per-test checkpoint.",stop_rules=["If content intervention is mostly unchanged, report zero-treatment coverage and redesign before inference.","If Appraisal fails to beat Cue-only and shuffled Appraisal on new material/multiple seeds, do not expand it or retrain it.","If credible independent source grouping remains unavailable, label all confirmation as sample/media-disjoint provisional; do not assert source-independent generalization."],conditional_semantic_phase="Only if initial arms fail to establish a useful method: text-grounded subject/time/target/negation/only/contrast evidence with exact phrase support and abstention; independently verify before expansion",conditional_training="Only after usable separated development and reliable supervision plus a repeatable inference gain; matched no-graph control, separated valence objective, validated semantic evidence, 5000-step pilot; no automatic broad sweep",training_parallelism="Four lanes apply to inference. Training concurrency separately capacity-tested; never assume four full trainers fit.",final_deliverable="Adopt/reject/provisional method matrix, baseline harm, per-class HIT/M, WAF/recalls, OV P/R, uncertainty and data exposure limits")
 atomic_json(run/"protocol.json",protocol)
 (run/"PROTOCOL.md").write_text("# 方法收敛实验程序\n\n有限阶段：材料准入 → 原始Appraisal/匹配打乱对照（三个种子、两个统一研究权重）→ 冻结候选再看确认材料 → 仅在必要且数据准入后追加语义证据及5000步匹配训练对照。\n\nA/B/C/S/P五条件，H不再重复扫。八路共享整样本任务队列，A100构建与checkpoint加载串行，GPU推理四路。不得沿用3781/996静态分配。\n\n现五标准集1253条官方val媒体未找到。替代新材料必须标清训练暴露、精确/近重复及来源不明；不得将媒体/名称去重自动写成原始视频/说话者独立。\n\n详见protocol.json的条件性停止/扩展规则。研究目标是可复验净纠错与简化方案，不要求为消耗GPU而做无依据训练。\n")
 atomic_json(run/"status.json",dict(phase="data_audit",updated_at_beijing=now()))
 B=ROOT/"dataset/mer2025-dataset"
 plus={x["name"] for x in rows(B/"track2_train_mercaptionplus.csv")}
 p=read(SOURCE/"plan.json")
 oldrows=[x for di in p["datasets"].values() for x in read(di["path"])]
 test_names={x["name"] for x in oldrows}
 train=read(ROOT/"amg_d_multistart10/runs/d_multistart10_20261025_160152/train_records.json")
 texts={x["name"]:x for x in rows(B/"subtitle_chieng.csv")}
 known_paths={str((B/"audio"/(n+".wav")).resolve()) for n in plus if (B/"audio"/(n+".wav")).is_file()}
 known_paths.update(str(Path(x["audio_path"]).resolve()) for x in oldrows)
 known_raw=set();known_pcm=set();known_text=set()
 for n in plus:
  for lang in ["chinese","english"]:
   t=norm(texts.get(n,{}).get(lang))
   if len(t)>=16:known_text.add(t)
 for x in oldrows:
  for t in [x.get("subtitle"),x.get("text",{}).get("chinese"),x.get("text",{}).get("english")]:
   t=norm(t)
   if len(t)>=16:known_text.add(t)
 def known_digest(path):
  try:return sha(path),pcm_digest(path)[0]
  except Exception:return None,None
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for i,(a,b) in enumerate(pool.map(known_digest,sorted(known_paths))):
   if a:known_raw.add(a)
   if b:known_pcm.add(b)
   if i%2000==0:print("KNOWN_AUDIO",i,len(known_paths),flush=True)
 atomic_json(run/"audit/known_exposure_fingerprints.json",dict(sample_ids=sorted(plus|test_names),audio_sha256=sorted(known_raw),pcm_sha256=sorted(known_pcm),long_text_sha256=sorted(canonical(x) for x in known_text),limitations="Original source-video/speaker IDs unavailable; no claim of source independence. Known base source assumed MERCaptionPlus per existing configuration; other undocumented pretraining exposures remain unverified."))
 candidates={};labels={}
 for family,file in [("MER_track1","track1_train_disdim.csv"),("MER_OV","track2_test.csv")]:
  for x in rows(B/file):
   n=x["name"]
   if n in plus or n in test_names:continue
   t=texts.get(n,{})
   rec=dict(sample_id="NEW::"+n,name=n,family=family,text={k:t.get(k,"") for k in ["chinese","english"]},subtitle=t.get("english",""),audio_path=str((B/"audio"/(n+".wav")).resolve()),video_path=str((B/"video"/(n+".mp4")).resolve()),face_path=str((B/"openface_face"/n/(n+".npy")).resolve()),source_group_status="unknown",original_source_video_id=None,original_speaker_id=None)
   if n in candidates:
    candidates[n]["families"]=sorted(set(candidates[n].get("families",[candidates[n]["family"]])+[family]))
   else:candidates[n]=rec
   labels.setdefault(n,{})[family]={k:v for k,v in x.items() if k!="name"}
 inventory=[];eligible=[];flags=collections.Counter()
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for n,asset in pool.map(inspect,candidates.items()):
   rec=candidates[n];reasons=[]
   for key in ["audio_path","video_path","face_path"]:
    if not Path(rec[key]).is_file():reasons.append("missing_"+key)
   if not rec["subtitle"].strip():reasons.append("missing_english_subtitle")
   if "error" in asset:reasons.append("audio_decode_error")
   if asset.get("audio_sha256") in known_raw:reasons.append("known_exact_audio")
   if asset.get("pcm_sha256") in known_pcm:reasons.append("known_PCM_audio")
   if any(len(norm(t))>=16 and norm(t) in known_text for t in rec["text"].values()):reasons.append("known_long_text_duplicate")
   if not .2<=asset.get("audio_duration",0)<=30:reasons.append("duration_outside_preset")
   rec["media_audit"]=asset;rec["exclusion_reasons"]=reasons
   inventory.append(rec);flags.update(reasons)
   if not reasons:eligible.append(rec)
 print("CANDIDATES",len(candidates),"ELIGIBLE",len(eligible),"FLAGS",dict(flags),flush=True)
 atomic_json(run/"audit/candidate_inventory.json",inventory)
 # Duplicate audio and identical long English subtitles form conservative media clusters, not certified source-video groups.
 parent={x["name"]:x["name"] for x in eligible}
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:parent[max(a,b)]=min(a,b)
 by={}
 for x in eligible:
  keys=[("pcm",x["media_audit"]["pcm_sha256"])]
  if len(norm(x["subtitle"]))>=16:keys.append(("text",norm(x["subtitle"])))
  for k in keys:
   if k in by:union(x["name"],by[k])
   else:by[k]=x["name"]
 for x in eligible:x["media_cluster_id"]=find(x["name"]);x["source_independence_certified"]=False
 # Hash-based pre-assignment; no label or prediction used to choose development/confirmation.
 groups=collections.defaultdict(list)
 for x in eligible:groups[x["media_cluster_id"]].append(x)
 ordered=sorted(groups,key=lambda g:canonical("method-decision-v1::"+g))
 partitions={"development":[],"confirmation":[]};used=set();caps=protocol["development_max"]
 for phase in partitions:
  count=collections.Counter()
  for g in ordered:
   if g in used:continue
   block=groups[g]
   famcounts=collections.Counter(x["family"] for x in block)
   if any(count[f]+v>caps[f] for f,v in famcounts.items()):continue
   partitions[phase].extend(block);count.update(famcounts);used.add(g)
  print("PARTITION",phase,dict(count),flush=True)
 for phase,items in partitions.items():
  atomic_json(run/"data"/(phase+"_records.json"),items)
  atomic_json(run/"data"/(phase+"_labels.json"),{x["name"]:labels[x["name"]] for x in items})
 atomic_json(run/"audit/eligible_records.json",eligible)
 summary=dict(candidate_count=len(candidates),eligible_after_media_checks=len(eligible),flags=dict(flags),partitions={k:dict(collections.Counter(x["family"] for x in v)) for k,v in partitions.items()},all_selected_media_present=True,known_ID_exact_PCM_long_text_overlaps_removed=True,source_group_metadata_available=False,source_independence_certified=False,admission="Available for preregistered sample/media-disjoint provisional experiments; not certified source-independent confirmation.",near_video_duplicate_check="pending selected-media verification",next_phase="selected_media_near_duplicate_and_input_QC",updated_at_beijing=now())
 atomic_json(run/"audit/DATA_READINESS.json",summary);atomic_json(run/"status.json",dict(phase="selected_media_QC_pending",audit=summary,updated_at_beijing=now()))
 print(json.dumps(dict(run=str(run),summary=summary),ensure_ascii=False),flush=True)
if __name__=="__main__":main()
