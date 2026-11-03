from graph_paths import resolve_path as _graph_resolve_path
import os,subprocess,time,traceback
from graph_paths import Path
from .common import *
def main():
 pkg=ROOT/'amg_d_graph_compare';owner=locked(pkg/'launch.lock');require(owner is not None,'Launcher already active');assets=Path(read(pkg/'assets/current.json')['path']);state=dict(phase='waiting_for_graph_oof',pid=os.getpid(),started_at_beijing=now(),new_graph_base_epoch=35)
 def update(**kw):state.update(kw,updated_at_beijing=now());atomic_json(pkg/'launch_status.json',state)
 def execute(module,args,log):
  with log.open('ab',buffering=0) as f:
   result=subprocess.run([str(PYTHON),'-u','-B','-m',module]+args,cwd=ROOT,env=environment(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  require(result.returncode==0,'Stage failed: '+module)
 try:
  update()
  while not (assets/'oof_manifest.json').exists():
   ss=read(assets/'oof_status.json');require(ss['phase']!='failed','New graph OOF preparation failed: '+ss.get('error',''))
   require(time.time()-os.stat(_graph_resolve_path(assets / 'oof_status.json')).st_mtime<300,'New graph OOF preparation stalled');time.sleep(10)
  require(read(assets/'oof_manifest.json')['complete'] and read(assets/'target_cache_manifest.json')['complete'],'Graph evidence incomplete')
  update(phase='creating_experiment_plans');execute('amg_d_graph_compare.setup',['--new-base','35'],pkg/'setup.log');run=Path(read(pkg/'runs/current.json')['path']);update(phase='cpu_preflight',run=str(run))
  execute('amg_d_graph_compare.preflight',['--run',str(run)],run/'preflight.log');update(phase='training_pipeline',run=str(run))
  execute('amg_d_graph_compare.controller',['--run',str(run)],run/'controller.log');update(phase='complete',finished_at_beijing=now())
 except BaseException as e:update(phase='failed',error=repr(e),traceback=traceback.format_exc());raise
 finally:owner.close()
if __name__=='__main__':main()
