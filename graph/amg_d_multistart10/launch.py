"""Persistent server-only CPU preflight and training/inference/evaluation launcher."""
import argparse,os,subprocess,traceback
from .common import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);a=ap.parse_args();run=Path(a.run);p=plan(run);owner=locked(run/'bootstrap.lock');require(owner is not None,'Bootstrap already active');state=dict(phase='cpu_preflight',pid=os.getpid(),pgid=os.getpgrp(),plan_id=p['plan_id'],started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());atomic_json(run/'bootstrap_status.json',state)
 def execute(module,logname,cpu=False):
  env=environment()
  if cpu:env['CUDA_VISIBLE_DEVICES']=''
  with (run/logname).open('ab',buffering=0) as log:result=subprocess.run([str(PYTHON),'-u','-B','-m',module,'--run',str(run)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
  require(result.returncode==0,'Stage failed: '+module)
 try:
  update();execute('amg_d_multistart10.preflight','preflight.log',True);update(phase='training_pipeline');execute('amg_d_multistart10.controller','controller.log');update(phase='complete',finished_at_beijing=now())
 except BaseException as e:update(phase='failed',error=repr(e),traceback=traceback.format_exc());raise
 finally:owner.close()
if __name__=='__main__':main()
