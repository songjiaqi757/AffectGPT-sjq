"""Run one checkpoint through the existing official scorers."""
import sys,argparse,zipfile
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
import amg_rl_oppo_graph10.scoring as scoring
def main():
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);a.add_argument('--phase',choices=['ov','other'],required=True);x=a.parse_args()
 run=Path(x.run);p=plan(run);target='rl_e010'
 jobs=[read(run/'jobs'/(target+'_'+d+'.json')) for d in DATASETS]
 require(all(j['state']=='complete' for j in jobs),'Checkpoint 10 incomplete')
 for j in jobs:
  raw=Path(j['official_npz'])
  for suffix in ['-openset.npz','-openset-sentiment.npz']:
   cache=raw.with_name(raw.stem+suffix)
   if cache.exists():
    try:
     with zipfile.ZipFile(cache) as z:valid=z.testzip() is None
    except (OSError,zipfile.BadZipFile):valid=False
    if not valid:cache.rename(cache.with_suffix(cache.suffix+'.invalid'))
 original_pending=scoring.pending
 def only_target(run,role,only=None):
  return [j for j in original_pending(run,role,only) if j['checkpoint']==target]
 scoring.pending=only_target
 if x.phase=='ov':scoring.rl_ov(run)
 else:scoring.rl_other(run)
if __name__=='__main__':main()
