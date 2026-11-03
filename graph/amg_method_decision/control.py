"""Durable two-host sequence: development -> frozen choice -> confirmation -> report."""
from graph_paths import hash_matches as _graph_hash_matches
import os,sys,time,subprocess,signal,traceback,json,argparse
from graph_paths import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq/graph');sys.path.insert(0,str(ROOT))
from amg_method_decision.pipeline import read,dump,canonical,sha,now,environment,PYTHON,locked
from amg_method_decision.generate import verify
def controller(run,index):
 def stop(*unused):raise KeyboardInterrupt('Experiment controller interrupted')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 node=['A800','A100'][index];status=run/f'method_node_{node}.json';children=[];ownership=locked(run/f'method_node_{node}.lock')
 if ownership is None:raise RuntimeError('Controller already running')
 def update(phase,**kw):
  dump(status,dict(node=node,pid=os.getpid(),phase=phase,time_beijing=now(),**kw))
  if index==0:dump(run/'status.json',dict(phase=phase,time_beijing=now(),**kw))
 def check():
  if (run/'failure.json').exists():raise RuntimeError('Peer failure: '+str(read(run/'failure.json')))
 def waitfor(test,seconds,label):
  end=time.monotonic()+seconds
  while not test():
   check()
   if time.monotonic()>end:raise TimeoutError(label)
   time.sleep(4)
 def launch(module,args,log,cpu=False):
  env=environment(0)
  if cpu:env['CUDA_VISIBLE_DEVICES']=''
  f=(run/log).open('ab',buffering=0);z=subprocess.Popen([PYTHON,'-u','-B','-m','amg_method_decision.'+module]+args,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close();children.append(z);return z
 def finish(z,seconds,label):
  waitfor(lambda:z.poll() is not None,seconds,label)
  if z.returncode:raise RuntimeError(label+' returned '+str(z.returncode))
 def used():return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
 try:
  p=verify(run)
  manifest=read(run/'experiment_code_manifest.json')
  for rel,h in manifest['files'].items():
   if not _graph_hash_matches(ROOT / rel, h, sha(ROOT / rel)):raise ValueError('Experiment code changed: '+rel)
  for part in ['development','confirmation']:
   if part=='development' and (run/'development_selection_complete.json').exists() and (run/'evaluation/development/metrics_verified.json').exists():
    update('development_completed_reused')
    continue
   if part=='confirmation':
    waitfor(lambda:(run/'development_selection_complete.json').exists(),172800,'Development selection')
    frozen=read(run/'frozen_selection.json')
    if frozen['plan_id']!=p['plan_id']:raise ValueError('Wrong selection plan')
   update(part+'_generation')
   logfile=f'generation_controller_{part}_{node}_resumed.log'
   z=launch('generate',['node','--run',str(run),'--part',part,'--index',str(index)],logfile)
   finish(z,172800,part+' generation')
   waitfor(lambda:used()<256,180,'Generation GPU release')
   dump(run/f'gen_released_{part}_{node}.json',dict(passed=True,used_mib=used(),time_beijing=now()))
   waitfor(lambda:all((run/f'gen_released_{part}_{n}.json').exists() for n in ['A800','A100']),172800,'Both-node generation release')
   e=run/'evaluation'/part;e.mkdir(parents=True,exist_ok=True)
   if index==0:
    update(part+'_materializing');z=launch('evaluate',['materialize','--run',str(run),'--part',part],f'{part}_materialize.log',cpu=True);finish(z,1800,'Materializing')
   waitfor(lambda:(e/'evaluation_barrier.json').exists(),1800,'Evaluation inputs')
   for stage in ['openset','sentiment']:
    ready=e/f'{stage}_ready.json'
    if index==0:
     z=launch('evaluate',['prepare','--run',str(run),'--part',part,'--stage',stage],f'{part}_prepare_{stage}.log',cpu=True);finish(z,1800,'Preparing '+stage);dump(ready,dict(ready=True,time_beijing=now()))
    waitfor(ready.exists,1800,'Judge ready '+stage);update(part+'_judge_'+stage)
    z=launch('evaluate',['judge','--run',str(run),'--part',part,'--stage',stage,'--index',str(index)],f'{part}_judge_{stage}_{node}.log');finish(z,21600,'Judge '+stage)
    waitfor(lambda:used()<256,180,'Judge GPU release');dump(e/f'{stage}_done_{node}.json',dict(complete=True,time_beijing=now()))
    waitfor(lambda:all((e/f'{stage}_done_{n}.json').exists() for n in ['A800','A100']),21600,'Both-node judge '+stage)
   if index==0:
    update(part+'_metrics');z=launch('evaluate',['metrics','--run',str(run),'--part',part],f'{part}_metrics.log',cpu=True);finish(z,3600,'Official metrics')
    z=launch('analyze',[str(run),part],f'{part}_analysis.log',cpu=True);finish(z,7200,'Paired analysis')
    if part=='development':dump(run/'development_selection_complete.json',dict(passed=True,selection_id=read(run/'frozen_selection.json')['selection_id'],time_beijing=now()))
    else:
     report(run);dump(run/'final_verification.json',dict(passed=True,development=read(run/'evaluation/development/metrics_verified.json'),confirmation=read(run/'evaluation/confirmation/metrics_verified.json'),frozen_selection_id=read(run/'frozen_selection.json')['selection_id'],decision=read(run/'method_decision.json'),code_manifest_sha256=sha(run/'experiment_code_manifest.json'),source_independence_certified=False,training_executed=False,time_beijing=now()))
   else:
    target=run/('development_selection_complete.json' if part=='development' else 'final_verification.json');waitfor(target.exists,10800,'CPU decision')
  update('complete_provisional_method_decision',result=str(run/'analysis/METHOD_DECISION.md'))
 except BaseException as ex:
  failure=dict(node=node,phase='controller_failure',error=repr(ex),traceback=traceback.format_exc(),time_beijing=now())
  if not (run/'failure.json').exists():dump(run/'failure.json',failure)
  update('failed',error=repr(ex))
  for z in children:
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:ownership.close()
def report(run):
 p=verify(run);frozen=read(run/'frozen_selection.json');decision=read(run/'method_decision.json');d=read(run/'evaluation/development/three_seed_summary.json');c=read(run/'evaluation/confirmation/three_seed_summary.json');audit=read(run/'audit/shuffle_intervention_audit.json');parts=read(run/'audit/selected_media_QC.json')['remaining']
 meanings={'A':'无额外证据','B':'Cue','C':'Cue+原始Appraisal，无Emotion列表/路径','S':'Cue+格式及状态数量匹配的打乱Appraisal','P':'原始完整图提示'}
 adopted=decision['adopt_provisionally'];lines=['# 方法决策：新样本开发与冻结确认','',f"暂定使用：{adopted['checkpoint']}，{adopted['condition']}（{meanings[adopted['condition']]}）。",f"开发阶段预先冻结候选：{frozen['checkpoint']} / {frozen['condition']}；确认通过：{decision['confirmation_passed']}；Appraisal内容收益得到本轮确认：{decision['Appraisal_validated']}。",'','## 实验范围','',f"开发集与确认集各为：{parts}。使用两套统一权重 original_epoch40、fixed_graph45_to54；各三个生成种子42/2026/2027。同一样本全部条件和两套权重绑定同一物理GPU。",f"原始C和打乱S在有效Appraisal样本中的状态集合实际变化比例：{100*audit['semantic_change_fraction_among_active']:.2f}%。语义未变的对照不能作为独立内容干预。",'','|阶段|权重|组|HIT|M|极性WAF|ACC|OV F|OV P|OV R|','|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
 for part,rows in [('开发',d),('确认',c)]:
  for x in rows:
   a=x['tasks'];values=[a['MER_track1_discrete'][k] for k in ['HIT','M']]+[a['MER_track1_polarity'][k] for k in ['WAF','ACC']]+[a['MER_OV'][k] for k in ['F_s','P_s','R_s']]
   lines.append('|'+part+'|'+x['checkpoint']+'|'+x['condition']+'|'+'|'.join(f'{v:.3f}' for v in values)+'|')
 lines+=['','## 方法取舍','', 'C只有同时优于Cue基线B与打乱对照S，且正负极性没有超过预设阈值的伤害，才视为Appraisal的内容证据得到支持。S是机制对照，不能成为待采用方法。开发集选择在确认集评分前写入frozen_selection.json，确认失败时退回原始40轮无证据基线，不改选第二名。','若C未通过，本轮不支持继续扩充或训练当前Appraisal表示；这也不等于证明所有Appraisal方法无效。若C通过，结论仍仅为当前数据条件下的推理候选，需要来源隔离材料才能升级。','之前H（只删Emotion列表、逐字保留路径）的九集补测未显示稳定收益，因此不把H继续作为主候选。原始P完整图与无证据基线均保留。','', '## 结论边界与训练决定','', '当前仅确认与已知材料的样本编号、原始音频/PCM及长文本重复已排除，并完成所选视频/人脸输入和三帧相似性检查。缺少原始视频/说话者映射，未完成对全部训练视频的近重复搜索，也无法排除未记录的预训练曝光。因此本报告不是严格来源独立的泛化结论，也不是九标准集新最好成绩。','两个权重训练预算不同，不能将权重之间差值全部归因于图。三个生成种子不代表多个训练种子；配对区间按样本重采样，不能冒充按原视频/人物重采样。','当前不新增训练。新语义证据尚无独立验证的监督，来源隔离条件也未满足；直接训练会把当前不确定性写进模型。','', '逐类情绪得失、正负类召回、纠错/伤害、配对区间：evaluation/development/paired_analysis.json与evaluation/confirmation/paired_analysis.json。官方指标与逐样本重算核对见metrics_verified.json。所有代码、媒体、日志和结果均在服务器。']
 (run/'analysis/METHOD_DECISION.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);a.add_argument('--index',type=int,required=True);x=a.parse_args();controller(Path(x.run),x.index)
