"""CPU validation of priority dispatch, evaluation coverage and official metrics."""
from graph_paths import resolve_path as _graph_resolve_path
import argparse,os,sys,tempfile
from graph_paths import Path
from .common import ROOT,verify,read,sha,canonical,atomic_json,require,now
from .priority_score import phase_plan,resources,truth,inference_ready
def main():
 a=argparse.ArgumentParser();a.add_argument("--phase",required=True);args=a.parse_args();phase=Path(args.phase).resolve();ph=phase_plan(phase);ip=verify(ph["inference_run"]);resources(phase)
 require(len(ph["checkpoints"])==20 and len(ph["job_ids"])==60 and ph["sample_predictions"]==28000,"Priority cardinality mismatch")
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
 coverage={d:len(truth(d,ip,evaluation)) for d in ph["datasets"]}
 hit,_=evaluation.hitrate_metric_calculation(name2gt={"fixture":"happy"},name2pred={"fixture":["happy"]},inter_print=False)
 fs,precision,recall=evaluation.wheel_metric_calculation(name2gt={"fixture":"happy"},name2pred={"fixture":["happy"]},inter_print=False)
 require(all(abs(float(v)-1)<1e-9 for v in [hit,fs,precision,recall]),"Official exact-match metric fixture failed")
 import numpy as np
 with tempfile.TemporaryDirectory(dir=phase) as directory:
  raw=Path(directory)/"fixture.npz";names=["negative_sample","positive_sample","zero_sample"]
  np.savez_compressed(_graph_resolve_path(raw.with_name('fixture-openset.npz')), filenames=names, fileitems=['sad', 'happy', 'neutral'])
  np.savez_compressed(_graph_resolve_path(raw.with_name('fixture-openset-sentiment.npz')), filenames=names, fileitems=['negative', 'positive', 'neutral'])
  waf,acc=evaluation.calculate_dimension_zeroshot(str(raw),dict(zip(names,[-.5,.5,0])),None,None,None,False)
  require(abs(waf-1)<1e-9 and abs(acc-1)<1e-9,"Original SIMS sign/nonzero metric fixture failed")
 report=dict(passed=True,phase_id=ph["phase_id"],coverage=coverage,inference_tasks=60,source_checkpoint_count=20,sample_predictions=28000,evaluation_processes=1,official_metric_fixtures={"MER2023_HIT":float(hit),"SIMS_WAF":float(waf),"SIMS_ACC":float(acc),"OVMERDPlus_F_s":float(fs)},scoring_has_not_started=True,no_judge_or_cuda_model_loaded=True,time_beijing=now())
 atomic_json(phase/"preflight.json",report);print("PRIORITY_AND_EVALUATION_PREFLIGHT_PASSED",phase)
if __name__=="__main__":main()
