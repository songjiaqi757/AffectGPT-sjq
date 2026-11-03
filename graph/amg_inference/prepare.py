"""Freeze the nine official test memberships without using their labels as model inputs."""
import csv,sys,io,pickle,zipfile
from graph_paths import Path
import numpy as np
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .common import ROOT,DATASETS,now
TRAIN=ROOT/"amg_finetune/runs/graph_continue_no_gc_20261022_164836"
class NumpyOnly(pickle.Unpickler):
 def find_class(self,module,name):
  allowed={("numpy","ndarray"):np.ndarray,("numpy","dtype"):np.dtype,
   ("numpy.core.multiarray","_reconstruct"):np.core.multiarray._reconstruct,
   ("numpy.core.multiarray","scalar"):np.core.multiarray.scalar,
   ("numpy._core.multiarray","_reconstruct"):np.core.multiarray._reconstruct,
   ("numpy._core.multiarray","scalar"):np.core.multiarray.scalar}
  if (module,name) not in allowed:raise pickle.UnpicklingError("Blocked global "+module+"."+name)
  return allowed[module,name]
def members(path,member):
 with zipfile.ZipFile(path) as z:
  with z.open(member+".npy") as f:
   version=np.lib.format.read_magic(f)
   shape,fortran,dtype=np.lib.format._read_array_header(f,version)
   require(dtype.hasobject and shape==(),"Unexpected corpus representation")
   corpus=NumpyOnly(f).load().item()
   require(isinstance(corpus,dict) and all(isinstance(k,str) for k in corpus),"Invalid membership keys")
   return list(corpus) # Values never reach prompts, Cue, cache, prediction or selection.
def main():
 sys.path.insert(0,str(ROOT/"AffectGPT"));import config
 run=ROOT/"amg_inference/runs"/("graph_225_"+now()[:19].replace("-","").replace(":","").replace("T","_"))
 run.mkdir(parents=True,exist_ok=False);(run/"jobs").mkdir();(run/"cache").mkdir();(run/"inputs").mkdir()
 tp=read(TRAIN/"plan.json");datasets={}
 p=dict(schema_version="amg_prediction_queue_v1",created_at_beijing=now(),training_run=str(TRAIN),
  training_plan_id=tp["plan_id"],training_plan_sha256=sha(TRAIN/"plan.json"),
  runtime_path=tp["runtime_path"],runtime_release_id=tp["runtime_release_id"],cue_profile=tp["cue_profile"],
  query_config_path=tp["query_config_path"],query_config_id=tp["query_config_id"],
  query_selection_id=tp["query_selection_id"],graph_release_id=tp["graph_release_id"],
  limits=tp["training"],datasets=datasets,concurrency_per_gpu=3,seed=42,
  generation=dict(num_beams=1,temperature=1.0,do_sample=True,top_p=.9,max_new_tokens=1200,max_length=2736),
  prompt_question="Please recognize all possible emotional states of the character.",
  protocol="Original zero-shot open-vocabulary question; original face/audio/subtitle plus identical frozen graph formatter. Original generation settings, context extended from 2000 to 2736 to retain the complete <=1536 token multimodal prompt plus <=1200 output tokens. Per-sample deterministic seed fixed before any target generation.",
  policy="All 25 epochs x all nine test sets; no target-driven prompt/threshold/checkpoint selection. Predictions only, no target label scoring. Cue cache is native single-record engineering profile. Human reliability and overlap audits remain pending.",
  gpu_policy={"0":[30,40,50],"1":[35,45]},capacity_policy="After its complete training queue releases the GPU lock, run three concurrent source-only full-window generation probes before three inference workers. Fail closed on capacity or probe error.")
 atomic_json(run/"protocol_before_membership.json",p)
 for d,expected in DATASETS.items():
  sub=(ROOT/"AffectGPT"/config.PATH_TO_TRANSCRIPTIONS[d]).resolve()
  with sub.open(newline="") as f:table={r["name"]:r for r in csv.DictReader(f)}
  label=(ROOT/"AffectGPT"/config.PATH_TO_LABEL[d]).resolve()
  if d=="OVMERDPlus":names=list(table);member="subtitle CSV membership"
  else:
   member="whole_corpus" if d=="IEMOCAPFour" else "test1_corpus" if d in ["MER2023","MER2024"] else "test_corpus"
   names=members(label,member)
   if d=="IEMOCAPFour":names=[n for n in names if n[4]=="5"]
  require(len(names)==expected and len(set(names))==expected,f"Official split count mismatch: {d}: {len(names)}")
  rows=[];missing={"audio":0,"face":0,"video":0}
  for n in names:
   require(n in table,"Subtitle membership absent: "+d+" "+n);s=table[n]
   subtitle=s.get("sentence","") if d=="OVMERDPlus" else s.get("chinese","") if d=="MER2024" else s.get("english","")
   audio=(ROOT/"AffectGPT"/config.PATH_TO_RAW_AUDIO[d]/(n+".wav")).resolve()
   face=(ROOT/"AffectGPT"/config.PATH_TO_RAW_FACE[d]/(n+".npy")).resolve()
   video=(ROOT/"AffectGPT"/config.PATH_TO_RAW_VIDEO[d]/(n+(".avi" if d=="IEMOCAPFour" else ".mp4"))).resolve()
   if d in ["MER2023","MER2024"] and not video.exists():video=video.with_suffix(".avi")
   for k,path in [("audio",audio),("face",face),("video",video)]:missing[k]+=int(not path.is_file())
   text={"chinese":s.get("chinese",""),"english":s.get("english",s.get("sentence",""))}
   rows.append(dict(sample_id=d+"::"+n,name=n,dataset=d,subtitle=subtitle,text=text,audio_path=str(audio),face_path=str(face),video_path=str(video)))
  # Missing raw video may yield unavailable visual Cues; AffectGPT requires face + audio here.
  require(not missing["audio"] and not missing["face"],"Required AffectGPT media absent: "+d+" "+repr(missing))
  target=run/"inputs"/(d+".json");atomic_json(target,rows)
  datasets[d]=dict(path=str(target),sha256=sha(target),samples=len(rows),membership_source=str(sub if d=="OVMERDPlus" else label),membership_member=member,subtitle_sha256=sha(sub),missing=missing)
 p["dataset_samples_total"]=sum(x["samples"] for x in datasets.values());p["logical_jobs"]=225;p["sample_predictions_total"]=25*p["dataset_samples_total"]
 p["plan_id"]=canonical(p);atomic_json(run/"plan.json",p)
 for spec in tp["checkpoints"]:
  for epoch in spec["epochs"]:
   for d in DATASETS:
    jid=f"from_{spec['base_epoch']:02d}_epoch_{epoch:02d}_{d}"
    atomic_json(run/"jobs"/(jid+".json"),dict(job_id=jid,base_epoch=spec["base_epoch"],epoch=epoch,dataset=d,state="pending",attempts=0,plan_id=p["plan_id"]))
 source=read(TRAIN/"train_records.json")[0]
 atomic_json(run/"source_probe.json",dict(record=source,cache_path=str(TRAIN/"cache"/(source["sample_id"]+".json"))))
 atomic_json(ROOT/"amg_inference/runs/current.json",dict(path=str(run),plan_id=p["plan_id"]))
 print(run)
if __name__=="__main__":main()
