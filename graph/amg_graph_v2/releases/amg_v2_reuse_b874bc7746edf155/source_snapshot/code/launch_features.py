"""Launch bounded CPU-only extraction on one shared-directory node."""
import argparse,os,subprocess,sys
from .common import *
def main(node):
 jobs=([('text',i,4) for i in range(4)]+[('audio',i,8) for i in range(4)]+[('visual',i,12) for i in range(4)]) if node=='A800' else ([('audio',i,8) for i in range(4,8)]+[('visual',i,12) for i in range(4,12)])
 d=ROOT/'jobs';d.mkdir(exist_ok=True);runs=[]
 for m,i,n in jobs:
  out=ROOT/f'features/{m}_{i:02d}.npz'
  if out.exists():continue
  log=d/f'{m}_{i:02d}.log';cmd=[sys.executable,'-B','-u','-m','amg_graph_v2.features','--modality',m,'--shard',str(i),'--shards',str(n),'--threads','4']
  env=dict(os.environ,PYTHONPATH=str(GRAPH),PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4')
  with log.open('ab',buffering=0) as f:r=subprocess.Popen(cmd,cwd=GRAPH,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  runs.append(dict(modality=m,shard=i,total_shards=n,pid=r.pid,log=str(log),command=cmd))
 write(d/f'feature_workers_{node}.json',dict(node=node,cpu_only=True,runs=runs));event('workers_launched',node=node,count=len(runs))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--node',required=True,choices=['A800','A100']);main(a.parse_args().node)
