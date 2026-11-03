import os,sys,copy,ast
from types import SimpleNamespace
from .common import *
def setup():
 os.chdir(OPPO);sys.path.insert(0,str(OPPO))
 from affect_r1.merbench import run_inference as n
 args=SimpleNamespace(affectgpt_root=None,dataset_root=str(OPPO/'datasets'),use_face_video=False)
 return n,n.load_config(args)
def sample_function(n):
 tree=ast.parse((OPPO/'affect_r1/merbench/run_inference.py').read_text())
 main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
 loop=next(x for x in ast.walk(main) if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='name')
 body=[]
 for node in loop.body:
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='writer':continue
  body.append(copy.deepcopy(node))
 original=copy.deepcopy(body);modified=[]
 for node in body:
  modified.append(node)
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='messages' for t in node.targets):
   modified.extend(ast.parse("messages = append_graph(messages, graph_text)").body)
 fn=ast.parse('def official_sample(model,processor,config_module,dataset,subtitles,name,graph_text):\n pass').body[0]
 prefix=ast.parse("video_dir=config_module.PATH_TO_RAW_VIDEO.get(dataset,'')\naudio_dir=config_module.PATH_TO_RAW_AUDIO.get(dataset,'')").body
 fn.body=prefix+modified+ast.parse('return response,messages,video_path,audio_path').body
 stripped=[x for x in modified if not(isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='messages' for t in x.targets) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name) and x.value.func.id=='append_graph')]
 require(ast.dump(ast.Module(body=stripped,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=original,type_ignores=[]),include_attributes=False),'OPPO AST differs beyond graph append')
 class MakeFunction(ast.NodeTransformer):
  def visit_Continue(self,node):return ast.copy_location(ast.Raise(exc=ast.Call(func=ast.Name(id='RuntimeError',ctx=ast.Load()),args=[ast.Constant('Official OPPO media missing')],keywords=[]),cause=None),node)
 fn=MakeFunction().visit(fn);module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
 scope=dict(vars(n))
 scope['args']=SimpleNamespace(use_audio_in_video=True,max_new_tokens=1024,do_sample=True,temperature=.9,top_p=.9)
 scope['progress']=SimpleNamespace(write=print);scope['append_graph']=append_graph
 exec(compile(module,str(OPPO/'affect_r1/merbench/run_inference.py')+'::graph_append','exec'),scope)
 return scope['official_sample'],dict(native_sample_ast_verified=True,generation=dict(max_new_tokens=1024,do_sample=True,temperature=.9,top_p=.9),use_audio_in_video=True,use_face_video=False,official_launcher_defaults=True,only_prompt_change='append graph evidence to existing user text content',seed=None)
def append_graph(messages,text):
 messages=copy.deepcopy(messages)
 if text:
  items=[c for m in messages if m['role']=='user' for c in m['content'] if c['type']=='text']
  require(len(items)==1,'Unexpected OPPO text layout');items[0]['text']+='\n'+text
 return messages
class Predictor:
 def __init__(self):
  self.n,self.config=setup();self.fn,self.contract=sample_function(self.n)
  import importlib.util
  attn='flash_attention_2' if importlib.util.find_spec('flash_attn') else 'sdpa'
  self.model=self.n.Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(str(OPPO/'models/OPPO'),torch_dtype=self.n.torch.bfloat16,device_map='auto',attn_implementation=attn).eval()
  self.processor=self.n.Qwen2_5OmniProcessor.from_pretrained(str(OPPO/'models/OPPO'))
  self.subtitles={d:self.n.read_subtitles(self.config.PATH_TO_TRANSCRIPTIONS.get(d,'')) for d in DATASETS}
 def load(self,spec):pass
 def predict(self,p,row,evidence):
  graph,info=format_graph(p,evidence,self.processor.tokenizer)
  response,messages,v,a=self.fn(self.model,self.processor,self.config,row['dataset'],self.subtitles[row['dataset']],row['name'],graph)
  original=self.n.build_messages(v,a,self.subtitles[row['dataset']].get(row['name'],''),use_audio_in_video=True)
  require(messages==append_graph(original,graph),'OPPO messages changed beyond graph append')
  info.update(prompt_sha256=canonical(messages),graph_text=graph,contract=self.contract,video_path=v,audio_path=a)
  return response,info
def audit(run):
 n,config=setup();fn,contract=sample_function(n);p=read(Path(run)/'plan_draft.json');datasets={};stats={}
 for d in DATASETS:
  names=n.load_test_names(d,config);old=read(p['prior_datasets'][d]['path']);byname={x['name']:x for x in old}
  require(len(names)==len(old) and set(names)==set(byname),'OPPO native membership differs '+d)
  subtitles=n.read_subtitles(config.PATH_TO_TRANSCRIPTIONS.get(d,''));rows=[];missing=[]
  for name in names:
   row=copy.deepcopy(byname[name]);row['subtitle']=subtitles.get(name,'')
   for field,root,exts in [('video_path',config.PATH_TO_RAW_VIDEO.get(d,''),['.mp4','.avi','.mkv']),('audio_path',config.PATH_TO_RAW_AUDIO.get(d,''),['.wav','.mp3'])]:
    row[field]=n.find_media(root,name,exts)
    if row[field] is None:missing.append((name,field))
   rows.append(row)
  require(not missing,'OPPO native media missing '+str(missing[:10]))
  path=Path(run)/'inputs'/('oppo_'+d+'.json');dump(path,rows)
  datasets[d]=dict(path=str(path),sha256=sha(path),samples=len(rows))
  stats[d]=dict(samples=len(rows),native_membership_verified=True,native_media_verified=True,subtitle_source='OPPO native read_subtitles',missing=missing)
 dump(Path(run)/'oppo_preflight.json',dict(passed=True,datasets=datasets,audit=stats,contract=contract))
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);x=a.parse_args();audit(x.run)
