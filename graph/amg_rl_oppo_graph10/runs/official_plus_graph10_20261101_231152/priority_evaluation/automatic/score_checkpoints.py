"""Filter jobs to explicitly requested checkpoints; official scorers are unchanged."""
import sys,argparse,zipfile
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
import amg_rl_oppo_graph10.scoring as scoring
def main():
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);a.add_argument('--phase',choices=['ov','other'],required=True);a.add_argument('--checkpoints',required=True);x=a.parse_args()
 run=Path(x.run);p=plan(run);targets=set(x.checkpoints.split(','))
 require(targets and targets<=set(p['models']['rl']['checkpoints']),'Unknown checkpoints')
 jobs=[read(run/'jobs'/(cid+'_'+d+'.json')) for cid in targets for d in DATASETS]
 require(all(j['state']=='complete' for j in jobs),'Requested checkpoint inference incomplete')
 for j in jobs:
  raw=Path(j['official_npz'])
  for suffix in ['-openset.npz','-openset-sentiment.npz']:
   cache=raw.with_name(raw.stem+suffix)
   if cache.exists():
    try:
     with zipfile.ZipFile(cache) as z:valid=z.testzip() is None
    except (OSError,zipfile.BadZipFile):valid=False
    if not valid:cache.rename(cache.with_suffix(cache.suffix+'.invalid'))
 original=scoring.pending
 scoring.pending=lambda run,role,only=None:[j for j in original(run,role,only) if j['checkpoint'] in targets]
 if x.phase=='ov':scoring.rl_ov(run)
 else:scoring.rl_other(run)
if __name__=='__main__':main()
