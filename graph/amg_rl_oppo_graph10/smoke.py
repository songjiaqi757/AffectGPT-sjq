import argparse,time,traceback
from .common import *
def main():
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);a.add_argument('--role',required=True,choices=['rl','oppo']);x=a.parse_args()
 run=Path(x.run);p=plan(run);role=x.role;model=p['models'][role]
 try:
  if role=='rl':
   from .native_rl import Predictor
  else:
   from .native_oppo import Predictor
  predictor=Predictor();spec=next(iter(model['checkpoints'].values()));predictor.load(spec)
  inv=read(run/'cache_inventory.json');reports=[]
  import torch
  for d in ['OVMERDPlus','CMUMOSEI']:
   rows=read(model['datasets'][d]['path'])
   row=rows[0] if d=='OVMERDPlus' else max(rows,key=lambda r:len(r['subtitle']))
   b=graph_evidence(p,inv,d,row['name']);start=time.monotonic()
   response,info=predictor.predict(p,row,b['evidence'])
   report=dict(dataset=d,name=row['name'],response=response,info=info,elapsed=time.monotonic()-start,gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated(),gpu_peak_reserved_bytes=torch.cuda.max_memory_reserved())
   reports.append(report);dump(run/'validation'/('smoke_'+role+'.json'),dict(passed=False,state='running',reports=reports))
   print('SMOKE_SAMPLE',role,d,row['name'],'seconds',report['elapsed'],'peak_GiB',report['gpu_peak_reserved_bytes']/1024**3,repr(response[:500]),flush=True)
  if role=='rl':
   for spec in model['checkpoints'].values():predictor.load(spec)
  dump(run/'validation'/('smoke_'+role+'.json'),dict(passed=True,state='complete',reports=reports,all_checkpoint_loads_verified=True,time=now()))
  print('SMOKE_PASSED',role,flush=True)
 except BaseException as exc:
  dump(run/'validation'/('smoke_'+role+'.json'),dict(passed=False,state='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
