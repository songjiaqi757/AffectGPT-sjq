import ast,copy,os,sys,importlib.util
from types import SimpleNamespace
from .common import *
QUESTION="Please recognize all possible emotional states of the character."
def setup():
 os.chdir(RL);sys.path.insert(0,str(RL))
 import config
 spec=importlib.util.spec_from_file_location('official_base_config_paths',BASE/'config.py')
 original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
 changes={}
 for field in ['DATA_DIR','PATH_TO_RAW_AUDIO','PATH_TO_RAW_VIDEO','PATH_TO_RAW_FACE','PATH_TO_TRANSCRIPTIONS','PATH_TO_LABEL']:
  target=getattr(config,field)
  for d in DATASETS:
   if d not in target:
    target[d]=str((BASE/getattr(original,field)[d]).resolve())
    changes.setdefault(field,{})[d]=target[d]
 import inference_hybird as n
 cfg=n.Config(SimpleNamespace(cfg_path=str(RL/'train_configs/mercaptionplus_outputhybird_bestsetup_bestfusion_face_r1stage2_mer25ov1000_continue60_g4_formatbeta00_ovlabel_numrestrict3.yaml'),options=None))
 return n,cfg,changes
def reader(n,cfg,d):
 r=n.get_name2cls(d);r.needed_data=r.get_needed_data(n.get_face_or_frame(cfg.datasets_cfg,None))
 r.vis_processor=n.BaseProcessor();r.img_processor=n.BaseProcessor()
 for attr in ['vis_processor','img_processor']:
  v=cfg.inference_cfg.get(attr)
  if v is not None:setattr(r,attr,n.registry.get_processor_class(v.train.name).from_config(v.train))
 r.n_frms=cfg.model_cfg.vis_processor.train.n_frms
 # Localize the official nested-face filename convention to the existing flat files.
 # The same NPY bytes feed the unchanged official media reader.
 if hasattr(r,'_get_face_path'):
  official_face=r._get_face_path
  def face_path(sample):
   value=official_face(sample)
   if Path(value).exists():return value
   flat=Path(r.face_root)/(sample['name']+'.npy')
   require(flat.exists(),'Official face data unavailable: '+value)
   return str(flat)
  r._get_face_path=face_path
 return r
def sample_function(n):
 tree=ast.parse((RL/'inference_hybird.py').read_text())
 loop=next(x for x in ast.walk(tree) if isinstance(x,ast.For) and isinstance(x.target,ast.Tuple) and [getattr(y,'id',None) for y in x.target.elts]==['ii','name'])
 body=[]
 for node in loop.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='name2reason' for t in node.targets):continue
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='print' and any(isinstance(x,ast.Name) and x.id=='ii' for x in ast.walk(node)):continue
  body.append(copy.deepcopy(node))
 original=copy.deepcopy(body)
 modified=[]
 for node in body:
  modified.append(node)
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user_message' for t in node.targets):
   modified.extend(ast.parse("user_message = user_message + ('\\n' + graph_text if graph_text else '')").body)
 fn=ast.parse('def official_sample(dataset_cls,chat,face_or_frame,name,graph_text):\n pass').body[0]
 fn.body=ast.parse('name2subtitle = dataset_cls.name2subtitle').body+modified+ast.parse('return response,prompt').body
 module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
 scope=dict(vars(n));scope['args']=SimpleNamespace(zeroshot=True,outside_user_message=QUESTION)
 exec(compile(module,str(RL/'inference_hybird.py')+'::graph_append','exec'),scope)
 stripped=[x for x in modified if not(isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user_message' for t in x.targets) and isinstance(x.value,ast.BinOp))]
 require(ast.dump(ast.Module(body=stripped,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=original,type_ignores=[]),include_attributes=False),'Native sample differs beyond graph append')
 return scope['official_sample'],dict(native_sample_ast_verified=True,only_prompt_change='append newline + frozen D compact+gate graph evidence to official user_message',generation=dict(num_beams=1,temperature=1,do_sample=True,top_p=.9,max_new_tokens=1200,max_length=2000),seed=None,full_subtitle=True)
class Predictor:
 def __init__(self):
  self.n,self.cfg,self.path_changes=setup();self.fn,self.contract=sample_function(self.n)
  self.model=None;self.chat=None;self.loaded=None;self.readers={}
 def load(self,spec):
  if self.loaded==spec['sha256']:return
  require(sha(spec['path'])==spec['sha256'],'Checkpoint changed')
  self.cfg.model_cfg.ckpt_3=spec['path']
  if self.model is None:self.model=self.n.registry.get_model_class(self.cfg.model_cfg.arch).from_config(self.cfg.model_cfg)
  else:
   ckpt=self.n.torch.load(spec['path'],map_location='cpu',weights_only=True)
   result=self.model.load_state_dict(ckpt['model'],strict=False)
   require(len(result.unexpected_keys)==0,'Unexpected RL checkpoint keys')
  self.model=self.model.to('cuda:0').eval()
  self.chat=self.n.Chat(self.model.model,self.cfg.model_cfg,device='cuda:0')
  self.loaded=spec['sha256']
 def predict(self,p,row,evidence):
  d=row['dataset']
  if d not in self.readers:self.readers[d]=reader(self.n,self.cfg,d)
  r=self.readers[d]
  require(r.name2subtitle[row['name']]==row['subtitle'],'Official subtitle differs')
  graph,info=format_graph(p,evidence,self.chat.tokenizer)
  response,prompt=self.fn(r,self.chat,self.n.get_face_or_frame(self.cfg.datasets_cfg,None),row['name'],graph)
  info.update(prompt_sha256=canonical(prompt),graph_text=graph,contract=self.contract)
  return response,info
def audit(run):
 n,cfg,changes=setup();fn,contract=sample_function(n)
 from omegaconf import OmegaConf
 dump(Path(run)/'rl_original_config.json',OmegaConf.to_container(cfg.config,resolve=True))
 p=read(Path(run)/'plan_draft.json');all_names={};stats={};equivalence=[]
 for d in DATASETS:
  r=reader(n,cfg,d);names=r.read_test_names();old=read(p['prior_datasets'][d]['path']);byname={x['name']:x for x in old}
  require(len(names)==len(old) and set(names)==set(byname),'RL native membership differs '+d)
  rows=[]
  for name in names:
   row=copy.deepcopy(byname[name]);row['subtitle']=r.name2subtitle[name]
   for field,method in [('audio_path','_get_audio_path'),('face_path','_get_face_path'),('video_path','_get_video_path')]:
    if hasattr(r,method):
     v=getattr(r,method)({'name':name})
     if v is not None:
      if Path(v).resolve()!=Path(row[field]).resolve():
       digest=sha(v)
       require(digest==sha(row[field]),'RL official media content differs '+d+' '+name+' '+field)
       equivalence.append(dict(dataset=d,name=name,field=field,official_path=str(v),prior_graph_path=row[field],sha256=digest))
      row[field]=str(v)
   rows.append(row)
  path=Path(run)/'inputs'/('rl_'+d+'.json');dump(path,rows)
  all_names[d]=dict(path=str(path),sha256=sha(path),samples=len(rows))
  stats[d]=dict(samples=len(rows),native_membership_verified=True,native_media_paths_verified=True,subtitle_source='RL native reader')
 dump(Path(run)/'validation/rl_media_equivalence.json',equivalence)
 dump(Path(run)/'rl_preflight.json',dict(passed=True,datasets=all_names,audit=stats,contract=contract,missing_dataset_path_localization=changes,config_note='Official RL release only configures OV-MERD+; other eight existing official readers receive upstream benchmark paths at runtime. Face filenames are localized from nested to existing flat layout when required; exact prior NPY paths verified. No official source files modified.'))
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);x=a.parse_args();audit(x.run)
