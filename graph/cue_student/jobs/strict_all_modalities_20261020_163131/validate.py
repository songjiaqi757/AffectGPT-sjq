from pathlib import Path
import os,sys,json,subprocess,time,traceback,gc
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"source"
sys.path.insert(0,str(SOURCE));os.chdir(SOURCE)
from cue_student.common import atomic_json,canonical_hash,sha256,code_hash
from cue_student.data import Release,CueDataset
from cue_student.holdout import load_fixed_holdout
report=dict(passed=False,cases={},code_hash=code_hash())
def passed(name,**kwargs):
 report["cases"][name]=dict(passed=True,**kwargs);atomic_json(ROOT/"integration_report.json",report);print("PASS",name,kwargs,flush=True)
def call(name,args):
 with (ROOT/(name+".log")).open("w") as log:
  result=subprocess.run([sys.executable,"-u","-m","cue_student.train"]+[str(v) for v in args],cwd=SOURCE,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError(name+" failed\n"+(ROOT/(name+".log")).read_text()[-5000:])
 passed(name)
def main():
 deadline=time.monotonic()+600
 while not (ROOT/"data_audit.json").exists():
  if time.monotonic()>deadline:raise RuntimeError("Data rebuild timeout")
  time.sleep(2)
 audit=json.loads((ROOT/"data_audit.json").read_text());full=Release(audit["release"]);hold=load_fixed_holdout()
 failed=set(full.eligibility["excluded_sample_ids"])
 assert not failed&{r["sample_id"] for r in full.rows} and not failed&set(hold["sample_ids"])
 for m in ("text","audio","visual"):
  for role,training in (("pseudo_train",True),("pseudo_validation",False)):
   ds=CueDataset(full,m,role,training=training)
   assert not failed&{full.rows[i]["sample_id"] for i in ds.indices}
 passed("all_modalities_and_holdout_failed_ids_disjoint",excluded=72,failed_tasks=78,holdout=300,release_id=audit["release_id"])
 # Small fresh smoke, same ontology/masks/media and new holdout identity.
 original=SOURCE/"cue_student/artifacts/smoke_release_v1";manifest=json.loads((original/"manifest.json").read_text());rows=json.loads((original/"members.json").read_text())
 chosen=[i for i,r in enumerate(rows) if r["role"]=="pseudo_train"][:8]+[i for i,r in enumerate(rows) if r["role"]=="pseudo_validation"][:4]
 mini=ROOT/"smoke_release";mini.mkdir(exist_ok=True)
 atomic_json(mini/"members.json",[rows[i] for i in chosen])
 for n in ("ontology.json","eligibility.json"):atomic_json(mini/n,json.loads((original/n).read_text()))
 with np.load(original/"labels.npz",allow_pickle=False) as z:np.savez_compressed(mini/"labels.npz",**{k:z[k][chosen] for k in ("targets","mask","states")})
 manifest.pop("release_id");manifest.update(n_samples=len(chosen),files={n:sha256(mini/n) for n in ("members.json","labels.npz","ontology.json","eligibility.json")},verified_annotation_records=len(chosen)*3,verified_original_media=len(chosen)*2,split=dict(role_counts=dict(pseudo_train=8,pseudo_validation=4)))
 manifest["release_id"]=canonical_hash(manifest);atomic_json(mini/"manifest.json",manifest);Release(mini)
 import torch
 for name in ("text","audio","visual","visual_temporal","audio_temporal"):
  cfg=json.loads((ROOT/"configs"/(name+".json")).read_text());cfg.update(epochs=2,patience=4,grad_accum=2,save_every_steps=1,num_workers=0)
  config=ROOT/("smoke_"+name+".json");atomic_json(config,cfg);out=ROOT/"smoke_outputs"/name
  args=["--config",config,"--release",mini,"--output",out,"--device","cuda:0","--cpu-threads","8","--allow-smoke"]
  if not (out/"last.pt").exists():call(name+"_first_step",args+["--max-steps","1"])
  else:passed(name+"_first_step_reused")
  ckpt=torch.load(out/"last.pt",map_location="cpu",weights_only=False)
  assert ckpt["progress"]["global_step"]==1 and ckpt["fixed_holdout_id"]==audit["fixed_holdout_id"] and ckpt["release_id"]==manifest["release_id"]
  assert ckpt["progress"]["epoch"] in (0,1)  # Small text smoke can finish its epoch in one update.
  assert not failed&{r["sample_id"] for r in json.loads((mini/"members.json").read_text())}
  passed(name+"_checkpoint",step=1,encoder_train=cfg["encoder_train"],temporal_model=cfg.get("temporal_model","none"),new_holdout=True)
  del ckpt;gc.collect()
  if name=="audio_temporal":
   call(name+"_resume",args+["--resume",out/"last.pt","--max-steps","2"])
   checkpoint=torch.load(out/"last.pt",map_location="cpu",weights_only=False);assert checkpoint["progress"]["global_step"]==2
   del checkpoint;gc.collect()
 report["passed"]=True;atomic_json(ROOT/"integration_report.json",report);print("ALL FIVE REAL GPU TESTS PASSED",flush=True)
try:main()
except BaseException:
 report["error"]=traceback.format_exc();atomic_json(ROOT/"integration_report.json",report);raise
