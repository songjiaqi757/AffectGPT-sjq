"""Strict current-run membership, original media transforms and answer-only loss masks."""
import random
from pathlib import Path
import torch
from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
from my_affectgpt.models.tokenizer import load_tokenizer_from_LLM
from my_affectgpt.processors import AlproVideoTrainProcessor
from amg_runtime.common import read,canonical,require
from .common import load_plan
from .prompts import make_tokens

class GraphContinueDataset(BaseDataset):
 def __init__(self,run,model_cfg,subset_ids=None):
  self.run=Path(run);self.plan=load_plan(run);self.limits=self.plan["training"];self.model_cfg=model_cfg
  self.annotation=read(self.run/"train_records.json")
  if subset_ids is not None:
   selected_ids=set(subset_ids);self.annotation=[r for r in self.annotation if r["sample_id"] in selected_ids]
  require(bool(self.annotation),"No training records")
  self.dataset="MERCaptionPlus";self.face_or_frame="multiface_audio_face_text";self.needed_data=["audio","face"];self.label_type="hybird";self.label_type_candidates=["description","ovlabel"]
  self.max_length=self.limits["max_sequence_tokens"];self.n_frms=model_cfg.vis_processor.train.n_frms
  self.num_video_query_token=model_cfg.num_video_query_token;self.num_audio_query_token=model_cfg.num_audio_query_token;self.num_multi_query_token=model_cfg.num_multi_query_token;self.num_image_query_token=model_cfg.num_image_query_token
  self.vis_processor=AlproVideoTrainProcessor.from_config(model_cfg.vis_processor.train);self.img_processor=None;self.txt_processor=None
  self.tokenizer=load_tokenizer_from_LLM(model_cfg.llama_model)
  ids=self.tokenizer.get_vocab()
  self.IMAGE_PATCH_TOKEN_ID=ids["<ImageHere>"];self.AUDIO_PATCH_TOKEN_ID=ids["<AudioHere>"];self.FRAME_PATCH_TOKEN_ID=ids["<FrameHere>"];self.FACE_PATCH_TOKEN_ID=ids["<FaceHere>"];self.MULTI_PATCH_TOKEN_ID=ids["<MultiHere>"]
 def evidence(self,sample):
  item=read(self.run/"cache"/(sample["sample_id"]+".json"))
  require(item["plan_id"]==self.plan["plan_id"] and item["sample_id"]==sample["sample_id"],"Cache membership/provenance mismatch")
  require(item["cache_id"]==canonical({k:v for k,v in item.items() if k!="cache_id"}),"Cache changed")
  expected={k:sample[k] for k in ["sample_id","text","audio_path","video_path"]}
  require(item["record_sha256"]==canonical(expected),"Cache/current sample input mismatch")
  require(item["evidence"]["query_config_id"]==self.plan["query_config_id"],"Evidence query configuration drift")
  return item["evidence"]
 def text_example(self,index,label_type):
  sample=self.annotation[index]
  return make_tokens(self,sample,self.evidence(sample),label_type,self.limits)
 def __getitem__(self,index):
  sample=self.annotation[index];label_type=self.label_type_candidates[random.randint(0,1)]
  prompt,target,_,info=self.text_example(index,label_type)
  expected={self.MULTI_PATCH_TOKEN_ID:1,self.AUDIO_PATCH_TOKEN_ID:1,self.FACE_PATCH_TOKEN_ID:1,self.IMAGE_PATCH_TOKEN_ID:0,self.FRAME_PATCH_TOKEN_ID:0}
  for token,count in expected.items():require(prompt.count(token)==count,"Unexpected multimodal placeholder count")
  media=self.read_frame_face_audio_text(video_path=None,face_npy=sample["face_path"],audio_path=sample["audio_path"],image_path=None)
  text=torch.tensor(prompt+target,dtype=torch.long);labels=torch.tensor([-100]*len(prompt)+target,dtype=torch.long)
  require(len(text)+2<=self.max_length and bool((labels!=-100).any()),"Empty supervision or sequence overflow")
  return dict(face=media["face"],raw_face=media["raw_face"],frame=None,raw_frame=None,audio=media["audio"],raw_audio=media["raw_audio"],image=None,raw_image=None,label=labels,text_input=text,dataset="mercaptionplus",face_or_frame=self.face_or_frame,sample_id=sample["sample_id"],prompt_info=info)
 def collater(self,instances):
  batch=super().collater(instances);batch["sample_ids"]=[x["sample_id"] for x in instances];batch["prompt_info"]=[x["prompt_info"] for x in instances]
  require("faces" in batch and "raw_faces" in batch and "audios" in batch and "raw_audios" in batch,"Required raw modality missing from training batch")
  return batch
