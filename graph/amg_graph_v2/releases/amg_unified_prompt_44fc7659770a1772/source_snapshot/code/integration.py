"""Append-only AffectGPT bridge; preserves task text, subtitle and every feature object."""
import copy,random
import numpy as np
from .adapter import PromptAblations
from .common import *
from .tokenization import MARKERS
class OriginalInputOverBudget(ValueError):pass

class AffectGPTUnifiedBridge:
 def __init__(self,adapter):self.adapter=adapter
 def prepare(self,reader,chat,sample_graph,original_question,subtitle,*,face_or_frame='multiface_audio_face_text',max_length=2048,max_new_tokens=512,evidence_token_budget=None):
  return self._prepare(reader,chat,sample_graph,original_question,subtitle,face_or_frame,max_length,max_new_tokens,evidence_token_budget,None)
 def prepare_ablation(self,reader,chat,sample_graph,original_question,subtitle,condition,*,face_or_frame='multiface_audio_face_text',max_length=2048,max_new_tokens=512,evidence_token_budget=None):
  return self._prepare(reader,chat,sample_graph,original_question,subtitle,face_or_frame,max_length,max_new_tokens,evidence_token_budget,condition)
 def _prepare(self,reader,chat,g,question,subtitle,face_or_frame,max_length,max_new_tokens,evidence_token_budget,condition):
  if not isinstance(question,str) or not isinstance(subtitle,str):raise ValueError('Original question and subtitle must be strings')
  if max_length<=0 or max_new_tokens<=0 or max_new_tokens>=max_length:raise ValueError('Invalid total/generation budget')
  def render(evidence):return reader.get_prompt_for_multimodal(face_or_frame,subtitle,question+('\n\n'+evidence if evidence else ''))
  def count(evidence):return len(chat.tokenizer.encode(chat.replace_token_for_multimodal(render(evidence)),add_special_tokens=False))
  prompt_limit=min(max_length-max_new_tokens,self.adapter.config['max_prompt_tokens']);baseline=render('');baseline_count=count('')
  if baseline_count>prompt_limit:raise OriginalInputOverBudget('Original multimodal input alone exceeds the available context; no original input was truncated')
  if condition=='P0':
   from ..v21.runtime import SampleGraphV21
   legacy=SampleGraphV21(self.adapter.graph_release);packet=None;budget=self.adapter.config['evidence_token_budget'] if evidence_token_budget is None else evidence_token_budget
   for k in range(self.adapter.config['cue_limit'],0,-1):
    text=legacy.prompt(copy.deepcopy(g),'open_vocabulary','relation_aware',cue_limit=k)
    if self.adapter.tokens(text)<=budget and count(text)<=prompt_limit:packet=dict(text=text,audit=dict(experimental_condition='P0',baseline_task='open_vocabulary',baseline_mode='relation_aware',cue_limit=k,evidence_tokens=self.adapter.tokens(text),full_prompt_tokens=count(text),fallback=not bool(text)));break
   if packet is None:packet=dict(text='',audit=dict(experimental_condition='P0',fallback=True,fallback_reason='budget',evidence_tokens=0,full_prompt_tokens=baseline_count))
  elif condition is None:packet=self.adapter.build(g,evidence_token_budget=evidence_token_budget,full_prompt_counter=count,prompt_token_budget=prompt_limit)
  else:packet=PromptAblations(self.adapter).build(g,condition,evidence_token_budget=evidence_token_budget,full_prompt_counter=count,prompt_token_budget=prompt_limit)
  prompt=render(packet['text']);full_tokens=count(packet['text'])
  if full_tokens>prompt_limit or full_tokens+max_new_tokens>max_length:raise AssertionError('Unsafe context would reach Chat left-truncation')
  if prompt!=reader.get_prompt_for_multimodal(face_or_frame,subtitle,question+('\n\n'+packet['text'] if packet['text'] else '')):raise AssertionError('Original task/input altered')
  if any(prompt.count(m)!=baseline.count(m) for m in MARKERS):raise AssertionError('AMG modified multimodal marker counts')
  packet['audit'].update(original_question_sha256=digest(question),original_subtitle_sha256=digest(subtitle),original_prompt_sha256=digest(baseline),final_prompt_sha256=digest(prompt),original_prompt_tokens=baseline_count,full_prompt_tokens=full_tokens,full_expanded_prompt_tokens=full_tokens,expanded_prompt_token_budget=prompt_limit,total_context_limit=max_length,max_new_tokens=max_new_tokens,original_question_preserved=True,original_subtitle_preserved=True,multimodal_marker_counts={m:prompt.count(m) for m in MARKERS},left_truncation_required=False,tokenizer_actual=True)
  return dict(prompt=prompt,question=question+('\n\n'+packet['text'] if packet['text'] else ''),evidence=packet,baseline_prompt=baseline)
 def generate_with_features(self,reader,chat,sample_graph,original_question,subtitle,img_list,*,face_or_frame='multiface_audio_face_text',**generation):
  max_length=generation.get('max_length',2048);max_new_tokens=generation.get('max_new_tokens',512)
  prepared=self.prepare(reader,chat,sample_graph,original_question,subtitle,face_or_frame=face_or_frame,max_length=max_length,max_new_tokens=max_new_tokens);before={k:id(v) for k,v in img_list.items()};result=chat.answer_sample(prepared['prompt'],img_list,**generation)
  if before!={k:id(v) for k,v in img_list.items()}:raise AssertionError('Feature dictionary changed during integration')
  prepared['evidence']['audit']['original_multimodal_feature_objects_preserved']=True;return result,prepared['evidence']['audit']

def predict_with_existing_predictor(predictor,row,sample_graph,adapter,seed):
 """Use an already loaded amg_inference Predictor; change only its prompt serialization."""
 import torch
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed);bridge=AffectGPTUnifiedBridge(adapter)
 with torch.inference_mode():
  media=predictor.reader.read_frame_face_audio_text(video_path=None,face_npy=row['face_path'],audio_path=row['audio_path'],image_path=None)
  ah,al=predictor.chat.postprocess_audio(media);fh,fl=predictor.chat.postprocess_face(media);_,ml=predictor.chat.postprocess_multi(fh,ah)
  if any(x is None for x in [al,fl,ml]):raise ValueError('Original inference modality is missing')
  response,info=bridge.generate_with_features(predictor.reader,predictor.chat,sample_graph,predictor.p['prompt_question'],row['subtitle'],dict(audio=al,face=fl,multi=ml,frame=None,image=None),**dict(predictor.p['generation']))
  torch.cuda.synchronize();return response,info
