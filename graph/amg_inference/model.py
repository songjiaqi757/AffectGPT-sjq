"""Original AffectGPT encoders and Chat with frozen training evidence formatting."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import copy,os,sys,random
from graph_paths import Path
import numpy as np
import torch
from amg_runtime.common import read,sha,require
from amg_finetune_nogc.prompts import clean_text,trim_text,format_evidence,encode,SPECIAL_MARKERS
from .common import ROOT,canonical
def make_prompt(reader,chat,row,evidence,p):
 t=chat.tokenizer;limits=p["limits"]
 subtitle,truncated=trim_text(t,clean_text(row["subtitle"]),limits["subtitle_token_budget"])
 graph,info=format_evidence(evidence,t,limits["graph_token_budget"])
 def render(g):
  return reader.get_prompt_for_multimodal("multiface_audio_face_text",subtitle,p["prompt_question"]+("\n"+g if g else ""))
 prompt=render(graph);ids=encode(t,chat.replace_token_for_multimodal(prompt))
 if len(ids)>limits["prompt_token_budget"]:
  graph,info=format_evidence(evidence,t,max(1,limits["graph_token_budget"]-(len(ids)-limits["prompt_token_budget"])-8))
  prompt=render(graph);ids=encode(t,chat.replace_token_for_multimodal(prompt))
 require(len(ids)<=limits["prompt_token_budget"],"Inference prompt budget exceeded")
 require(len(ids)+p["generation"]["max_new_tokens"]<=p["generation"]["max_length"],"Chat would left-truncate multimodal input")
 for marker,expected in zip(SPECIAL_MARKERS,[0,1,0,1,1]):require(prompt.count(marker)==expected,"Multimodal marker count changed")
 info.update(prompt_tokens=len(ids),subtitle_truncated=truncated,prompt_id=canonical(prompt))
 return prompt,info
def probe_generation_settings(settings):
 result=dict(settings);result.pop("min_length",None);result["min_new_tokens"]=result["max_new_tokens"];return result
class Predictor:
 def __init__(self,p):
  torch.set_num_threads(4);random.seed(42);np.random.seed(42);torch.manual_seed(42);torch.cuda.manual_seed_all(42)
  torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"))
  from omegaconf import OmegaConf
  from my_affectgpt.models.affectgpt import AffectGPT
  from my_affectgpt.conversation.conversation_video import Chat
  from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
  from my_affectgpt.processors import AlproVideoEvalProcessor
  config=copy.deepcopy(read(Path(p["training_run"])/"original_config.json"))
  config["model"].update(ckpt="",ckpt_2="",ckpt_3="",max_length=p["generation"]["max_length"])
  cfg=OmegaConf.create(config["model"]);self.model=AffectGPT.from_config(cfg)
  self.trainable=set(n for n,v in self.model.named_parameters() if v.requires_grad)
  require(len(self.trainable)==412,"Checkpoint architecture/trainable set changed")
  self.model.requires_grad_(False);self.model.to("cuda:0").eval()
  self.model.llama_model.gradient_checkpointing_disable();self.model.llama_model.config.use_cache=True
  self.chat=Chat(self.model,cfg,device="cuda:0")
  self.reader=BaseDataset.__new__(BaseDataset);self.reader.n_frms=cfg.vis_processor.train.n_frms;self.reader.needed_data=["face","audio"]
  self.reader.vis_processor=AlproVideoEvalProcessor.from_config(OmegaConf.create(config["inference"]["vis_processor"]["train"]))
  self.loaded=None;self.p=p
 def load(self,spec,job=None):
  if self.loaded==spec["sha256"]:return
  require(_graph_hash_matches(spec['path'], spec['sha256'], sha(spec['path'])),"Saved checkpoint checksum changed")
  x=torch.load(_graph_resolve_path(spec['path']), map_location='cpu', weights_only=True)
  require(x["epoch"]==spec["epoch"],"Checkpoint epoch mismatch")
  if job is not None:
   require(x["amg_finetune"]["plan_id"]==self.p["training_plan_id"] and x["amg_finetune"]["base_epoch"]==job["base_epoch"],"Wrong continuation provenance")
  state=x["model"];current=self.model.state_dict()
  require(not (self.trainable-set(state)) and not (set(state)-set(current)),"Incomplete checkpoint")
  for k,v in state.items():require(v.shape==current[k].shape,"Checkpoint shape mismatch: "+k)
  result=self.model.load_state_dict(state,strict=False)
  require(not result.unexpected_keys and not(set(result.missing_keys)&self.trainable),"Incomplete trainable restoration")
  self.loaded=spec["sha256"];del x,state,current
 def predict(self,row,evidence,seed,stress=False):
  random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
  prompt,info=make_prompt(self.reader,self.chat,row,evidence,self.p)
  if stress:
   # Source-only capacity probe fills the entire planned input and output window.
   from transformers import StoppingCriteriaList
   for _ in range(1536):
    candidate=prompt.replace(" ###Assistant:"," observation ###Assistant:")
    require(candidate!=prompt,"Source padding delimiter absent")
    if len(encode(self.chat.tokenizer,self.chat.replace_token_for_multimodal(candidate)))>1536:break
    prompt=candidate
   self.chat.stopping_criteria=StoppingCriteriaList([])
   info["stress_prompt_tokens"]=len(encode(self.chat.tokenizer,self.chat.replace_token_for_multimodal(prompt)))
  with torch.inference_mode():
   media=self.reader.read_frame_face_audio_text(video_path=None,face_npy=row["face_path"],audio_path=row["audio_path"],image_path=None)
   ah,al=self.chat.postprocess_audio(media);fh,fl=self.chat.postprocess_face(media);_,ml=self.chat.postprocess_multi(fh,ah)
   require(al is not None and fl is not None and ml is not None,"Required inference modality absent")
   kwargs=dict(self.p["generation"])
   original_generate=self.model.llama_model.generate
   if stress:
    def measured_generate(*args,**settings):
     result=original_generate(*args,**probe_generation_settings(settings));info["stress_generated_tokens"]=int(result.shape[-1]);return result
    self.model.llama_model.generate=measured_generate
   try:response=self.chat.answer_sample(prompt,dict(audio=al,face=fl,multi=ml,frame=None,image=None),**kwargs)
   finally:
    if stress:self.model.llama_model.generate=original_generate
   torch.cuda.synchronize()
  return response,info
