"""Server-only graph relocation; preserve source and frozen experiment bytes."""
import os,json,hashlib,ast,shutil,datetime
from pathlib import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq');GRAPH=ROOT/'graph';AUDIT=GRAPH/'_organization'/'20261029'
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):
 p=Path(p);t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');t.replace(p)
NAMES=sorted([p.name for p in ROOT.iterdir() if p.name.startswith('amg_')]+[
 'appraisal_annotation','cue_annotation','cue_student','emotion_nodes','human_annotation',
 'data_migrations','analysis_reports','Cue 提取与训练执行方案.md','图构建.md'])
def map_path(s):
 prefix=str(ROOT)+'/'
 if isinstance(s,str) and s.startswith(prefix):
  tail=s[len(prefix):]
  if tail.split('/',1)[0] in NAMES:return str(GRAPH)+'/'+tail
 return s
def map_obj(x):
 if isinstance(x,str):return map_path(x)
 if isinstance(x,list):return [map_obj(v) for v in x]
 if isinstance(x,dict):return {map_path(k):map_obj(v) for k,v in x.items()}
 return x
assert len(NAMES)==len(set(NAMES))
assert not (AUDIT/'complete.json').exists(),'Already completed'
for n in NAMES:
 p=ROOT/n;assert p.exists() and not p.is_symlink(),str(p)
 assert not (GRAPH/n).exists(),str(GRAPH/n)
skip={'runs','output','artifacts','jobs','reports','browser-cache','cache','datasets','releases',
 'preflight','__pycache__','.git','node_modules','emotion_release','assets','20261026','tools','source_before'}
sources=[]
for n in NAMES:
 p=ROOT/n
 if p.is_file():sources.append(p);continue
 for base,dirs,files in os.walk(p):
  dirs[:]=[d for d in dirs if d not in skip]
  for f in files:
   fp=Path(base)/f
   if f=='AGENTS.md':raise RuntimeError('Unreviewed instructions '+str(fp))
   if fp.suffix in {'.py','.sh','.yaml','.yml'}:sources.append(fp)
protected=[p for p in sources if p.is_file()]
frozen_specs={
'amg_method_decision/runs/decision_20261028_200538':[
 'inference_plan.json','experiment_code_manifest.json','frozen_selection.json','method_decision.json',
 'final_verification.json','evaluation/development/metrics.json','evaluation/confirmation/metrics.json',
 'analysis/FINAL_ANALYSIS_20261029.md','analysis/POSTRUN_INTEGRITY_20261029.json'],
'amg_188_path_noemotion/runs/path_noemotion_20261028_170538':[
 'plan.json','code_manifest.json','final_verification.json','metrics_all.json'],
'amg_188_audit/runs/winner188_20261028_114057':['plan.json','code_manifest.json','final_verification.json']}
for d,fs in frozen_specs.items():
 for f in fs:
  p=ROOT/d/f
  if p.exists():protected.append(p)
protected=sorted(set(protected));hashes={str(p.relative_to(ROOT)):digest(p) for p in protected}
stats={n:dict(inode=(ROOT/n).stat().st_ino,device=(ROOT/n).stat().st_dev,is_directory=(ROOT/n).is_dir()) for n in NAMES}
checkpoint=ROOT/'amg_d_multistart10/runs/d_multistart10_20261025_160152/from_45/checkpoint_000054_loss_0.511.pth';ckstat=checkpoint.stat()
dump(AUDIT/'plan.json',dict(schema='graph_directory_relocation_v1',
 time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),project=str(ROOT),canonical_root=str(GRAPH),
 moves={str(ROOT/n):str(GRAPH/n) for n in NAMES},roots_before=stats,protected_sha256=hashes,
 checkpoint_before=dict(path=str(checkpoint),inode=ckstat.st_ino,device=ckstat.st_dev,size=ckstat.st_size,mtime_ns=ckstat.st_mtime_ns),
 policy='Atomic rename; old root names remain relative compatibility symlinks; no source or frozen result edits'))
pointer_names=[]
for n in NAMES:
 p=ROOT/n
 if p.is_dir():pointer_names.extend(x for x in p.iterdir() if x.is_file() and x.name in {'current.json','current_run.json','server_resources.json'})
backup=AUDIT/'navigation_before'
for p in pointer_names+[ROOT/'README.md']:
 dst=backup/p.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
journal=[]
try:
 for n in NAMES:
  old=ROOT/n;new=GRAPH/n;old.rename(new);journal.append(n)
  old.symlink_to(Path('graph')/n,target_is_directory=new.is_dir())
  dump(AUDIT/'journal.json',dict(moved=journal))
 # Derived package roots resolve inside graph after relocation.
 for n in ['AffectGPT','dataset']:(GRAPH/n).symlink_to(Path('..')/n,target_is_directory=True)
 updated=[]
 for old in pointer_names:
  path=GRAPH/old.relative_to(ROOT);data=json.loads(path.read_text());new=map_obj(data)
  if path.name=='server_resources.json':new['graph_workspace']=str(GRAPH)
  if new!=data:
   dump(path,new);updated.append(dict(path=str(path),before_sha256=digest(backup/old.relative_to(ROOT)),after_sha256=digest(path)))
 index={}
 for n in NAMES:
  p=GRAPH/n;index[n]=dict(path=str(p),legacy_path=str(ROOT/n),kind='directory' if p.is_dir() else 'file')
  if p.is_dir():
   for name in ['current_run.json','current.json','server_resources.json']:
    if (p/name).is_file():index[n][name]=str(p/name)
 current_run=json.loads((GRAPH/'amg_method_decision/current_run.json').read_text())['run']
 index['_latest']=dict(method_decision_run=current_run,final_analysis=current_run+'/analysis/FINAL_ANALYSIS_20261029.md',
 method_decision=current_run+'/method_decision.json',
 recommended_checkpoint=str(GRAPH/'amg_d_multistart10/runs/d_multistart10_20261025_160152/from_45/checkpoint_000054_loss_0.511.pth'),
 server_resources=str(GRAPH/'amg_188_path_noemotion/server_resources.json'))
 dump(GRAPH/'paths.json',index)
 run_source="""#!/usr/bin/env python
\"\"\"Run relocated graph packages with their original module names.\"\"\"
import argparse,os,runpy,sys
from pathlib import Path
GRAPH=Path(__file__).resolve().parent
ROOT=GRAPH.parent
sys.path[:0]=[str(GRAPH),str(ROOT)]
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Run graph module: python graph/run.py MODULE [arguments]')
    p.add_argument('module')
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args()
    if args.module.split('.')[0] not in """+repr([n for n in NAMES if (GRAPH/n).is_dir()])+""":
        p.error('Choose a graph package listed in graph/paths.json')
    os.chdir(ROOT)
    os.environ['PYTHONPATH']=os.pathsep.join([str(GRAPH),str(ROOT),os.environ.get('PYTHONPATH','')])
    sys.argv=[args.module]+args.arguments
    runpy.run_module(args.module,run_name='__main__',alter_sys=True)
"""
 (GRAPH/'run.py').write_text(run_source)
 guide="""# 图相关工程与实验

统一实体目录：/ai/sjq/AffectGPT-sjq/graph

本次只整理目录与导航入口；模型、训练设置、推理逻辑、实验结果、冻结计划和源代码内容保持原样。
旧根目录的同名项目是兼容软链接，历史绝对路径、Python 包名和冻结文件哈希仍然有效。
AffectGPT/、dataset/ 在这里是指向原始模型工程和数据的依赖软链接，未复制这些内容。

## 内容位置

| 内容 | 目录或文件 |
| --- | --- |
| 图构建方案 | 图构建.md |
| Cue 提取、训练方案 | Cue 提取与训练执行方案.md |
| Cue/Appraisal 标注 | cue_annotation/、appraisal_annotation/ |
| Cue 学生模型、保留标注集 | cue_student/、human_annotation/ |
| Emotion 节点 | emotion_nodes/ |
| 图构建：188 节点及 10 类版本 | amg_graph/、amg_graph10/、amg_graph10_rebuild/ |
| 图查询运行时 | amg_runtime/ |
| 训练与对照 | amg_finetune*/、amg_bcd*/、amg_d_*/、amg_polarity/ |
| 推理、验证、修复 | amg_inference/、amg_validation/、amg_repair_cpu/ |
| 提示与路径消融 | amg_prompt_ablation*/、amg_188_audit/、amg_188_path_noemotion/ |
| 最新方法判定实验 | amg_method_decision/ |
| 跨实验报告 | analysis_reports/ |
| 历次数据迁移记录 | data_migrations/ |
| 规范路径、当前结果入口 | paths.json |
| 此次整理的清单、备份与验证 | _organization/20261029/ |

## 当前结果与资源配置

- 最终分析：amg_method_decision/runs/decision_20261028_200538/analysis/FINAL_ANALYSIS_20261029.md
- 方法判定：amg_method_decision/runs/decision_20261028_200538/method_decision.json
- A800/A100 配置：amg_188_path_noemotion/server_resources.json
- 当前实验：amg_method_decision/current_run.json

## 执行方法

使用服务器现有环境，保留原来的 Python 包名：

    cd /ai/sjq/AffectGPT-sjq
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B graph/run.py amg_runtime.cli --help

也可进入 graph/ 后按原包名执行 python -m amg_runtime.cli --help。
兼容软链接是历史计划和第三方脚本的路径保障，不代表另有一份数据。请勿直接删除。
历史报告内部的旧路径可直接访问，其规范新路径可通过 paths.json 查询。
"""
 (GRAPH/'README.md').write_text(guide)
 p=ROOT/'README.md';p.write_text(p.read_text()+'\n\n## 图相关工程与实验\n\n图构建、标注、训练、消融实验和分析报告统一位于 [graph/](graph/README.md)。\n规范路径及当前结果见 [graph/paths.json](graph/paths.json)；旧路径通过兼容软链接继续有效。\n')
 dump(AUDIT/'navigation_changes.json',updated)
 errors=[]
 for name,want in hashes.items():
  a=ROOT/name;b=GRAPH/name
  if digest(a)!=want or digest(b)!=want:errors.append('changed:'+name)
  if not os.path.samefile(a,b):errors.append('not_samefile:'+name)
 for n,before in stats.items():
  old=ROOT/n;new=GRAPH/n
  if not old.is_symlink() or not os.path.samefile(old,new):errors.append('link:'+n)
  if new.stat().st_ino!=before['inode'] or new.stat().st_dev!=before['device']:errors.append('inode:'+n)
 ck=checkpoint.stat()
 assert (ck.st_ino,ck.st_dev,ck.st_size,ck.st_mtime_ns)==(ckstat.st_ino,ckstat.st_dev,ckstat.st_size,ckstat.st_mtime_ns)
 for p in sources:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
 assert not errors,errors
 result=dict(passed=True,moved_roots=len(NAMES),protected_files_verified=len(hashes),
 source_bytes_unchanged=True,frozen_experiment_bytes_unchanged=True,checkpoint_inode_size_mtime_unchanged=True,
 compatibility_links_verified=True,mutable_navigation_files_updated=len(updated),
 graph_root=str(GRAPH),latest_analysis=current_run+'/analysis/FINAL_ANALYSIS_20261029.md')
 dump(AUDIT/'complete.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
except BaseException as exc:
 dump(AUDIT/'failure.json',dict(error=repr(exc),moved=journal,
 rollback='Inspect journal; original bytes preserved. Remove compatibility link; rename graph/name to original path; restore navigation_before.'))
 raise
