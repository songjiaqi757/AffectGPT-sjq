"""Native original AffectGPT checkpoint/media pipeline; append frozen unified P4 text only."""
import copy,gc,random
import numpy as np
import torch
from .common import *
class Predictor:
 def __init__(self,p):
  torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(p['per_process_memory_fraction'],0)
  from amg_base7_graph10.original_model import Predictor as NativePredictor
  self.p=p;self.native=NativePredictor(p);self.loaded=None;self.required=None;self.readers={}
 def load(self,spec):
  if self.loaded==spec['sha256']:return
  assert sha(spec['path'])==spec['sha256'],'Checkpoint changed'
  self.native.load(spec)
  if self.required is None:self.required={n for n,v in self.native.model.named_parameters() if v.requires_grad}
  checkpoint=torch.load(spec['path'],map_location='cpu',weights_only=True);state=checkpoint['model'];current=self.native.model.state_dict();assert checkpoint['epoch']==spec['epoch'];assert self.required<=set(state),'Required trained parameter missing'
  assert not(set(state)-set(current)),'Unexpected checkpoint parameter'
  for k,v in state.items():assert v.shape==current[k].shape,'Checkpoint shape mismatch: '+k
  self.native.model.requires_grad_(False);self.native.model.eval();self.loaded=spec['sha256'];self.readers={};del checkpoint,state,current;gc.collect();torch.cuda.empty_cache()
 def predict(self,row,cache,seed=None,stress=False):
  if row['dataset']!='SOURCE':return self._predict(row,cache,stress)
  py=random.getstate();npstate=np.random.get_state()
  try:
   with torch.random.fork_rng(devices=[0]):return self._predict(row,cache,stress)
  finally:random.setstate(py);np.random.set_state(npstate)
 def _predict(self,row,cache,stress=False):
  from amg_base7_graph10.original_model import original_reader
  chat=self.native.chat
  if row['dataset']=='SOURCE':
   from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
   reader=BaseDataset.__new__(BaseDataset);reader.needed_data=['audio','face'];reader.n_frms=self.native.config['model']['vis_processor']['train']['n_frms'];reader.vis_processor=self.native.native.registry.get_processor_class(self.native.config['inference']['vis_processor']['train']['name']).from_config(self.native.model_cfg.vis_processor.train)
  else:
   if row['dataset'] not in self.readers:self.readers[row['dataset']]=original_reader(self.native.native,row['dataset'],self.native.config)
   reader=self.readers[row['dataset']];assert reader.name2subtitle[row['name']]==row['subtitle'],'Original subtitle differs from frozen row'
  text=cache['packet']['text'];prompt=reader.get_prompt_for_multimodal('multiface_audio_face_text',row['subtitle'],self.p['prompt_question']+('\n\n'+text if text else ''));assert prompt==cache['final_prompt'],'Native Prompt differs from preflight'
  def count(s):return len(chat.tokenizer.encode(chat.replace_token_for_multimodal(s),add_special_tokens=False))
  original_tokens=count(prompt);settings=dict(self.p['generation']);assert original_tokens<=settings['max_length']-settings['max_new_tokens'] and original_tokens+settings['max_new_tokens']<=settings['max_length'],'Chat would truncate original inputs'
  info=dict(cache['packet']['audit'],native_original_prompt_tokens=original_tokens,actual_generation=self.p['generation'],seed=None,randomness_policy='Native script: no added per-sample reseeding; source-only probes restore RNG states',original_multimodal_inputs_preserved=True,checkpoint_sha256=self.loaded)
  original_generate=self.native.model.llama_model.generate;previous_stopping=chat.stopping_criteria
  if stress:
   marker=' ###Assistant:';assert marker in prompt
   for _ in range(1600):
    candidate=prompt.replace(marker,' observation'+marker)
    if count(candidate)>settings['max_length']-settings['max_new_tokens']:break
    prompt=candidate
   info['stress_prompt_tokens']=count(prompt)
   from transformers import StoppingCriteriaList
   chat.stopping_criteria=StoppingCriteriaList([])
   def force_length(*args,**kw):
    kw.pop('min_length',None);kw['min_new_tokens']=self.p['generation']['max_new_tokens'];result=original_generate(*args,**kw);info['stress_generated_tokens']=int(result.shape[-1]);return result
   self.native.model.llama_model.generate=force_length
  try:
   with torch.inference_mode():
    media=reader.read_frame_face_audio_text(video_path=None,face_npy=row['face_path'],audio_path=row['audio_path'],image_path=None);ah,al=chat.postprocess_audio(media);fh,fl=chat.postprocess_face(media);_,ml=chat.postprocess_multi(fh,ah);assert all(x is not None for x in [al,fl,ml]),'Required native input modality absent';response=chat.answer_sample(prompt,dict(audio=al,face=fl,multi=ml,frame=None,image=None),**settings);torch.cuda.synchronize()
  finally:
   self.native.model.llama_model.generate=original_generate;chat.stopping_criteria=previous_stopping
  info.update(peak_allocated_bytes=int(torch.cuda.max_memory_allocated()),peak_reserved_bytes=int(torch.cuda.max_memory_reserved()),actual_prompt_sha256=digest(prompt));return response,info
