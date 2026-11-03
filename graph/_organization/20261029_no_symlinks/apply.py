"""Replace organization symlinks with actual runtime addresses and audited source provenance."""
import os,re,ast,json,hashlib,shutil
from pathlib import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq');GRAPH=ROOT/'graph';AUDIT=GRAPH/'_organization/20261029_no_symlinks'
old_plan=json.loads((GRAPH/'_organization/20261029/plan.json').read_text());MOVES=old_plan['moves']
SKIP={'runs','output','artifacts','jobs','reports','browser-cache','cache','datasets','releases','preflight',
 '__pycache__','.git','node_modules','emotion_release','assets','20261026','tools','source_before','_organization'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
 p=Path(p);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def paths_text(text,bare=True):
 for old,new in sorted(MOVES.items(),key=lambda item:-len(item[0])):
  text=text.replace(old+'/',new+'/')
  text=re.sub(re.escape(old)+r'(?=["\x27\s\x60)\]]|$)',lambda m:new,text)
 if bare:text=re.sub(re.escape(str(ROOT))+r'(?!/)(?=["\x27\s\x60)\]]|$)',str(GRAPH),text)
 return text
def inserted(source,line):
 tree=ast.parse(source);body=tree.body;pos=0
 if body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):pos=body[0].end_lineno
 for node in body:
  if isinstance(node,ast.ImportFrom) and node.module=='__future__':pos=node.end_lineno
 lines=source.splitlines(keepends=True);lines.insert(pos,line+'\n');return ''.join(lines)
def edit_nodes(source,replacements):
 data=source.encode();starts=[];n=0
 for l in data.splitlines(keepends=True):starts.append(n);n+=len(l)
 edits=[(starts[node.lineno-1]+node.col_offset,starts[node.end_lineno-1]+node.end_col_offset,text.encode()) for node,text in replacements]
 last=len(data)+1
 for start,end,new in sorted(edits,reverse=True):
  assert end<=last,'Overlapping source edits';data=data[:start]+new+data[end:];last=start
 return data.decode()
FIRST_PATH={
 'open','os.chdir','os.listdir','os.scandir','os.makedirs','os.remove','os.unlink','os.stat',
 'os.path.exists','os.path.isfile','os.path.isdir','os.path.getsize','glob.glob',
 'torch.load','np.load','np.save','np.savez','np.savez_compressed','numpy.load','numpy.save',
 'Image.open','cv2.VideoCapture','librosa.load','sf.read','sf.info','soundfile.read','soundfile.info',
 'pd.read_csv','pd.read_json','pd.read_excel','load_file','safe_open',
 'safetensors.torch.load_file','shutil.copy2','shutil.copyfile','shutil.move'}
SECOND_PATH={'torch.save','shutil.copy2','shutil.copyfile','shutil.move'}
HASH_FUNCS={'sha','sha256','digest','media.sha','runner.sha','core.sha'}
def transform(source):
 source=paths_text(source).replace('from pathlib import Path','from graph_paths import Path')
 if 'pathlib.Path' in source:
  source=source.replace('pathlib.Path','_GraphPath');source=inserted(source,'from graph_paths import Path as _GraphPath')
 tree=ast.parse(source);repls=[]
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call):continue
  name=ast.unparse(node.func);positions=[]
  if name in FIRST_PATH or name.endswith('.from_pretrained'):positions.append(0)
  if name in SECOND_PATH:positions.append(1)
  if not positions:continue
  if any(isinstance(child,ast.Call) and child is not node and (ast.unparse(child.func) in FIRST_PATH or ast.unparse(child.func) in SECOND_PATH) for child in ast.walk(node)):continue
  args=list(node.args);changed=False
  for pos in positions:
   if len(args)>pos and not isinstance(args[pos],ast.Starred):
    args[pos]=ast.Call(func=ast.Name(id='_graph_resolve_path',ctx=ast.Load()),args=[args[pos]],keywords=[]);changed=True
  if changed:repls.append((node,ast.unparse(ast.Call(func=node.func,args=args,keywords=node.keywords))))
 if repls:
  source=edit_nodes(source,repls);source=inserted(source,'from graph_paths import resolve_path as _graph_resolve_path')
 tree=ast.parse(source);repls=[]
 for node in ast.walk(tree):
  if not isinstance(node,ast.Compare) or len(node.ops)!=1 or not isinstance(node.ops[0],(ast.Eq,ast.NotEq)):continue
  left=node.left;right=node.comparators[0];call=None;expected=None
  if isinstance(left,ast.Call) and ast.unparse(left.func) in HASH_FUNCS and len(left.args)==1:call=left;expected=right
  elif isinstance(right,ast.Call) and ast.unparse(right.func) in HASH_FUNCS and len(right.args)==1:call=right;expected=left
  if call is None:continue
  expression=ast.Call(func=ast.Name(id='_graph_hash_matches',ctx=ast.Load()),args=[call.args[0],expected,call],keywords=[])
  if isinstance(node.ops[0],ast.NotEq):expression=ast.UnaryOp(op=ast.Not(),operand=expression)
  repls.append((node,ast.unparse(expression)))
 if repls:
  source=edit_nodes(source,repls);source=inserted(source,'from graph_paths import hash_matches as _graph_hash_matches')
 ast.parse(source);return source
assert not (AUDIT/'applied.json').exists(),'Already applied; inspect first'
files=[]
for top in GRAPH.iterdir():
 if top.name in SKIP or top.is_symlink() or not top.is_dir():continue
 for base,dirs,fs in os.walk(top):
  dirs[:]=[d for d in dirs if d not in SKIP]
  for f in fs:
   p=Path(base)/f
   if f=='AGENTS.md':raise RuntimeError('Review '+str(p))
   if p.suffix in {'.py','.sh','.md','.yaml','.yml'}:files.append(p)
for old,new in MOVES.items():
 d=Path(new)
 if d.is_dir():files.extend(p for p in d.iterdir() if p.is_file() and p.name in {'current.json','current_run.json','server_resources.json'})
for rel in ['amg_runtime/releases/current.json','amg_graph/preflight/current.json','cue_student/artifacts/current_release.json']:files.append(GRAPH/rel)
files.extend((GRAPH/'cue_student/configs').glob('*.json'));files=sorted(set(files))
changes={}
for p in files:
 before=p.read_text()
 if p.suffix=='.py':after=transform(before)
 else:
  after=paths_text(before,bare=p.suffix!='.json')
  if p.name=='start.sh' and 'export PYTHONPATH=' not in after:after=after.replace('set -euo pipefail\n','set -euo pipefail\nexport PYTHONPATH=/ai/sjq/AffectGPT-sjq/graph\n')
 if after!=before:changes[str(p.relative_to(GRAPH))]=(before,after)
frozen={}
for rel,want in old_plan['protected_sha256'].items():
 p=GRAPH/rel
 if '/runs/' in rel and p.exists():frozen[rel]=sha(p)
records={}
for rel,(before,after) in changes.items():
 old=AUDIT/'before'/rel;old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(GRAPH/rel,old)
 records[rel]=dict(before_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=hashlib.sha256(after.encode()).hexdigest())
dump(AUDIT/'source_migration.json',dict(schema='actual_graph_paths_v1',files=records,frozen_sha256=frozen,old_to_new=MOVES,
 policy='Real directories. Preserve frozen metadata bytes. Historical source checks accept only exact audited before/after migrations.'))
for name,label in [('README.md','graph_README.before.md'),('paths.json','paths.before.json'),('run.py','run.before.py')]:shutil.copy2(GRAPH/name,AUDIT/label)
shutil.copy2(ROOT/'README.md',AUDIT/'project_README.before.md')
(GRAPH/'graph_paths.py').write_text((AUDIT/'graph_paths.py.prepared').read_text())
for rel,(_,after) in changes.items():
 p=GRAPH/rel;tmp=p.with_name(p.name+'.relocation_tmp');tmp.write_text(after);shutil.copymode(p,tmp);tmp.replace(p)
(GRAPH/'__init__.py').write_text('"""Actual graph workspace."""\nimport sys\nfrom pathlib import Path\n_workspace=str(Path(__file__).resolve().parent)\nif _workspace not in sys.path:sys.path.insert(0,_workspace)\n')
(GRAPH/'run.py').write_text("""#!/usr/bin/env python
\"\"\"Run graph modules from the actual workspace.\"\"\"
import argparse,os,runpy,sys
from pathlib import Path
GRAPH=Path(__file__).resolve().parent
sys.path.insert(0,str(GRAPH))
if __name__=='__main__':
    p=argparse.ArgumentParser(description='python graph/run.py MODULE [arguments]')
    p.add_argument('module')
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args()
    roots={x.name for x in GRAPH.iterdir() if x.is_dir() and not x.name.startswith('_')}
    if args.module.split('.')[0] not in roots:p.error('Choose a package in graph/paths.json')
    os.chdir(GRAPH)
    os.environ['PYTHONPATH']=os.pathsep.join([str(GRAPH),os.environ.get('PYTHONPATH','')])
    sys.argv=[args.module]+args.arguments
    runpy.run_module(args.module,run_name='__main__',alter_sys=True)
""")
removed=[]
for old,new in MOVES.items():
 p=Path(old);assert p.is_symlink() and p.resolve()==Path(new).resolve(),str(p);p.unlink();removed.append(str(p))
for n in ['AffectGPT','dataset']:
 p=GRAPH/n;assert p.is_symlink() and p.resolve()==(ROOT/n).resolve(),str(p);p.unlink();removed.append(str(p))
index=json.loads((GRAPH/'paths.json').read_text())
for value in index.values():
 if isinstance(value,dict) and 'legacy_path' in value:value['previous_path']=value.pop('legacy_path')
index['_structure']=dict(mode='actual_directories_no_organization_symlinks',project_root=str(ROOT),graph_root=str(GRAPH),
 base_affectgpt=str(ROOT/'AffectGPT'),base_dataset=str(ROOT/'dataset'),historical_path_map=str(AUDIT/'source_migration.json'))
dump(GRAPH/'paths.json',index)
(GRAPH/'README.md').write_text("""# 图相关工程与实验

实体目录：/ai/sjq/AffectGPT-sjq/graph

图代码、标注、Cue 学生模型、训练与消融、报告均在此实体目录内，旧根目录入口已移除。
原始 AffectGPT 与数据分别使用 /ai/sjq/AffectGPT-sjq/AffectGPT 和 /ai/sjq/AffectGPT-sjq/dataset 的实际目录。
本次整理创建的 31 个软链接已全部删除。

目录索引及当前结果：paths.json。
图构建方案：图构建.md；Cue 提取与训练方案：Cue 提取与训练执行方案.md。
最新分析：amg_method_decision/runs/decision_20261028_200538/analysis/FINAL_ANALYSIS_20261029.md。
资源配置：amg_188_path_noemotion/server_resources.json，A800/A100 各四路推理。

## 启动

    cd /ai/sjq/AffectGPT-sjq/graph
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B -m amg_runtime.cli --help

或从工程根目录运行：

    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B graph/run.py amg_runtime.cli --help

## 历史记录

历史结果、冻结计划和选择记录保留原始字节；旧路径由 graph_paths.py 在读取时解析到实际位置。
代码和可编辑配置已使用新路径。代码指纹变化逐项记录在
_organization/20261029_no_symlinks/source_migration.json，并保存修改前原文。
历史源代码校验只接受该清单中精确对应的改动；其他漂移仍然失败。
本次没有重新训练或改动指标。完整验证见 _organization/20261029_no_symlinks/。
""")
readme=ROOT/'README.md';text=readme.read_text().replace('规范路径及当前结果见 [graph/paths.json](graph/paths.json)；旧路径通过兼容软链接继续有效。','规范路径及当前结果见 [graph/paths.json](graph/paths.json)。图相关内容使用实际目录，旧根目录入口已移除。');readme.write_text(text)
dump(AUDIT/'removed_links.json',removed)
for rel,want in frozen.items():assert sha(GRAPH/rel)==want,rel
assert not any((Path(old).exists() or Path(old).is_symlink()) for old in MOVES)
assert not (GRAPH/'AffectGPT').exists() and not (GRAPH/'dataset').exists()
result=dict(applied=True,removed_symlinks=len(removed),changed_files=len(changes),frozen_files_byte_preserved=len(frozen),graph_root=str(GRAPH))
dump(AUDIT/'applied.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
