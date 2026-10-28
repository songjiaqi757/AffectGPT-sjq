"""Frozen 42D Cue inference. No labels, Teacher calls, calibration fitting or training."""
import contextlib,os
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG",":4096:8")
import copy,hashlib,json
from pathlib import Path
from .common import MODALITIES,OFFSETS,canonical,finite_number,read,require,sha,release_path,p0_context

def validate_records(records):
 require(isinstance(records,list),"Input must be an array")
 seen=set()
 for row in records:
  require(isinstance(row,dict) and not(set(row)-{"sample_id","text","audio_path","video_path"}),"Only current-sample input fields are allowed; labels and Teacher outputs are rejected")
  require(isinstance(row.get("sample_id"),str) and bool(row["sample_id"]) and row["sample_id"] not in seen,"sample_id must be a unique nonempty string")
  seen.add(row["sample_id"])
  if "text" in row:
   require(isinstance(row["text"],dict) and not(set(row["text"])-{"chinese","english"}),"Only bilingual text fields are allowed")
   require(all(v is None or isinstance(v,str) for v in row["text"].values()),"Text must be strings or null")
  for key in ["audio_path","video_path"]:
   require(key not in row or row[key] is None or isinstance(row[key],str),"Media paths must be strings or null")
   if row.get(key):require(Path(row[key]).is_absolute(),"Media paths must be absolute server paths")
 return records

class CueAssembler:
 def __init__(self,inputs,policy,profile="engineering"):
  require(profile in ("engineering","deployment"),"Unknown Cue policy profile")
  self.inputs=inputs;self.policy=copy.deepcopy(policy);self.profile=profile
  self.ids=inputs["cue_id_order"];self.n=len(self.ids)
  require(self.n==42 and policy["cue_id_order"]==self.ids,"Cue order mismatch")
  require(len(policy["thresholds"])==42 and all(finite_number(t) and 0<=t<=1 for t in policy["thresholds"]),"Invalid thresholds")
  decision=policy["profiles"][profile]
  for k in ["active_mask","deferred_mask"]:
   require(len(decision[k])==42 and all(type(x) is bool for x in decision[k]),"Invalid policy mask")
  require(all(a!=d for a,d in zip(decision["active_mask"],decision["deferred_mask"])),"Cue must be active or deferred, not both")
  require(policy["calibration"]["method"]=="identity" and policy["calibration"]["status"]=="uncalibrated","Only P0 uncalibrated identity scores are supported")
  require(policy["thresholds"]==inputs["scores"]["engineering_thresholds"],"Cue thresholds cannot be changed inside AMG")
  self.policy_id=canonical(policy);self.decision=decision
 def assemble(self,sample_id,modalities,requested_mask=None,input_fingerprints=None):
  requested_mask=[True]*42 if requested_mask is None else list(requested_mask)
  require(len(requested_mask)==42 and all(type(v) is bool for v in requested_mask),"Invalid requested Cue mask")
  require(set(modalities)<=set(MODALITIES),"Unknown modality")
  scores=[];availability=[];diagnostics={};model_versions={}
  for m in MODALITIES:
   a,b=OFFSETS[m];row=modalities.get(m,dict(sample_id=sample_id,input_valid=False,scores=None,error_code="modality_not_provided"))
   require(row.get("sample_id")==sample_id,"Modality/sample alignment mismatch")
   valid=row.get("input_valid",False)
   require(type(valid) is bool,"input_valid must be boolean")
   if valid:
    require(row.get("cue_ids")==self.ids[a:b],"Modality Cue order mismatch")
    values=row.get("scores")
    require(isinstance(values,list) and len(values)==b-a and all(finite_number(v) and 0<=v<=1 for v in values),"Invalid Cue scores")
    scores.extend(values);availability.extend([True]*(b-a))
   else:
    require(row.get("scores") is None,"Unavailable modality must have null scores")
    scores.extend([None]*(b-a));availability.extend([False]*(b-a))
   diagnostics[m]={k:row[k] for k in ["input_valid","input_observation","error","error_code"] if k in row}
   spec=self.inputs["checkpoints"][m]
   model_versions[m]=dict(run=spec["run"],checkpoint_sha256=spec["sha256"],signature=spec["signature"])
   if "inference_weights_sha256" in row:model_versions[m]["inference_weights_sha256"]=row["inference_weights_sha256"]
  active=self.decision["active_mask"];deferred=self.decision["deferred_mask"]
  allowed=[v and a and not d and r for v,a,d,r in zip(availability,active,deferred,requested_mask)]
  selected=[a and s>=t for a,s,t in zip(allowed,[s if s is not None else 0 for s in scores],self.policy["thresholds"])]
  weights=[float(s) if take else 0.0 for s,take in zip(scores,selected)]
  states=["modality_unavailable" if not v else "deferred" if d else "not_requested" if not r else "selected" if take else "below_threshold" for v,d,r,take in zip(availability,deferred,requested_mask,selected)]
  reason=None if any(selected) else ("deployment_policy_pending_human_audit" if self.profile=="deployment" else "no_query_cues")
  out=dict(schema_version="cue_query_42_v1",sample_id=sample_id,cue_id_order=list(self.ids),scores=scores,modality_present={m:all(availability[slice(*OFFSETS[m])]) for m in MODALITIES},availability_mask=availability,active_mask=list(active),deferred_mask=list(deferred),requested_mask=requested_mask,query_allowed_mask=allowed,selected_mask=selected,query_weights=weights,cue_states=states,thresholds=list(self.policy["thresholds"]),threshold_status=self.policy["threshold_status"],calibration=copy.deepcopy(self.policy["calibration"]),policy_profile=self.profile,policy_status=self.decision["status"],policy_id=self.policy_id,selected_cues=[dict(cue_id=c,score=s,query_weight=w) for c,s,w,ok in zip(self.ids,scores,weights,selected) if ok],model_versions=model_versions,cue_release_id=self.inputs["cue_release"]["release_id"],graph_release_id=self.inputs["graph"]["release_id"],diagnostics=diagnostics,input_fingerprints=input_fingerprints or {},fallback=dict(required=not any(selected),reason=reason,target="original_affectgpt"),semantics="Cue sigmoid scores are uncalibrated; low/unavailable/deferred/unselected are distinct; no inference of absence")
  out["query_input_id"]=canonical(out)
  return out

class FrozenCueStudent:
 """Reuse the existing forward implementation with safely loaded full-state weights."""
 @staticmethod
 def build(cfg):
  import torch
  from torch import nn
  from transformers import AutoConfig,AutoModel,CLIPVisionConfig,CLIPVisionModelWithProjection
  from cue_student.models import CueModel,TemporalHead
  from cue_student.temporal import temporal_spec
  require(cfg["encoder_train"]=="full" and temporal_spec(cfg)["temporal_model"]=="none","This release supports only the P0-selected full/mean trio")
  model=CueModel.__new__(CueModel);nn.Module.__init__(model)
  model.cfg=cfg;model.modality=cfg["modality"];model.temporal_spec=temporal_spec(cfg);model.encoder_mode="full";model._selected_modules=[]
  if model.modality=="visual":
   conf=CLIPVisionConfig.from_pretrained(cfg["model_dir"],local_files_only=True)
   model.encoder=CLIPVisionModelWithProjection(conf);dim=conf.projection_dim
  else:
   conf=AutoConfig.from_pretrained(cfg["model_dir"],local_files_only=True)
   kwargs=dict(add_pooling_layer=False) if model.modality=="text" else {}
   model.encoder=AutoModel.from_config(conf,**kwargs);dim=conf.hidden_size
   if model.modality=="audio":model.encoder.config.apply_spec_augment=False
  if model.modality=="text":model.head=nn.Sequential(nn.Linear(dim*2+2,256),nn.GELU(),nn.Dropout(cfg.get("dropout",.1)),nn.Linear(256,15))
  else:model.head=TemporalHead(dim,17 if model.modality=="audio" else 10,cfg.get("pooling","mean"),cfg.get("dropout",.1),cfg.get("topk",3))
  return model

class StudentRunner:
 def __init__(self,directory=None,device="cuda:0",profile="engineering"):
  from .versioning import load_release
  self.directory=release_path(directory);self.manifest=load_release(self.directory)
  self.inputs=read(self.directory/"inputs_p0.json");self.exports=read(self.directory/"weight_exports.json")["exports"]
  self.policy=read(self.directory/"cue_policy.json");self.assembler=CueAssembler(self.inputs,self.policy,profile)
  self.device=device;self.models={};self.collators={};self.verified_assets=set()
  import torch
  torch.manual_seed(42);torch.set_num_threads(4)
  torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  torch.use_deterministic_algorithms(True)
 def _load(self,m):
  if m in self.models:return
  import torch
  from safetensors.torch import load_file
  from cue_student.data import make_collator
  spec=self.exports[m];cfg=spec["config"]
  require(sha(spec["path"])==spec["sha256"],"Inference weight fingerprint mismatch")
  for name,expected in spec["encoder_assets"]["sha256"].items():
   p=str(Path(spec["encoder_assets"]["directory"])/name)
   if p not in self.verified_assets:require(sha(p)==expected,"Encoder asset drift");self.verified_assets.add(p)
  model=FrozenCueStudent.build(cfg)
  model.load_state_dict(load_file(spec["path"],device="cpu"),strict=True)
  model.requires_grad_(False);model.eval();model.to(self.device)
  self.models[m]=model;self.collators[m]=make_collator(cfg)
 def _predict_modality(self,row,m):
  import numpy as np
  import torch
  from cue_student.common import move_batch
  from cue_student.observations import describe
  from av.error import FFmpegError
  a,b=OFFSETS[m];cfg=self.inputs["checkpoints"][m]["config"]
  base=dict(sample_id=row["sample_id"],cue_ids=self.inputs["cue_id_order"][a:b],inference_weights_sha256=self.exports[m]["sha256"])
  if m=="text":
   if not any((row.get("text",{}).get(lang) or "").strip() for lang in ["chinese","english"]):
    return dict(base,input_valid=False,scores=None,error_code="both_text_languages_unavailable"),None
   input_hash=dict(text_sha256=canonical({lang:row.get("text",{}).get(lang) or "" for lang in ["chinese","english"]}))
  else:
   path=row.get("audio_path" if m=="audio" else "video_path")
   if not path or not Path(path).is_file():return dict(base,input_valid=False,scores=None,error_code="media_unavailable"),None
   try:
    stat=Path(path).stat();input_hash=dict(path=str(Path(path).resolve()),sha256=sha(path),bytes=stat.st_size,mtime_ns=stat.st_mtime_ns)
   except OSError as exc:return dict(base,input_valid=False,scores=None,error_code="media_unavailable",error=str(exc)),None
  self._load(m)
  try:
   safe_row={k:row[k] for k in ["sample_id","text","audio_path","video_path"] if k in row}
   safe_row.update(targets=np.zeros(b-a,np.float32),label_mask=np.zeros(b-a,bool))
   batch=move_batch(self.collators[m]([safe_row]),torch.device(self.device))
   cfg=self.inputs["checkpoints"][m]["config"]
   autocast=torch.autocast(device_type="cuda",dtype=torch.bfloat16) if str(self.device).startswith("cuda") and cfg.get("precision")=="bf16" else contextlib.nullcontext()
   with torch.inference_mode(),autocast:logits=self.models[m](batch)
   require(bool(torch.isfinite(logits).all()),"Non-finite prediction")
   scores=logits.float().sigmoid()[0].cpu().tolist()
   if m!="text":
    after=Path(path).stat();require((after.st_size,after.st_mtime_ns)==(stat.st_size,stat.st_mtime_ns),"Media changed during inference")
   return dict(base,input_valid=True,scores=scores,input_observation=describe(batch,0,m,cfg)),input_hash
  except (ValueError,OSError,IndexError,RuntimeError,FFmpegError) as exc:
   # Version and model-integrity checks execute in _load before this input-handling block.
   return dict(base,input_valid=False,scores=None,error_code="input_or_inference_error",error=type(exc).__name__+": "+str(exc)),input_hash
 def predict_records(self,records,requested_mask=None):
  validate_records(records);outputs=[]
  for row in records:
   modalities={};digests={}
   for m in MODALITIES:
    modalities[m],digest=self._predict_modality(row,m)
    if digest is not None:digests[m]=digest
   out=self.assembler.assemble(row["sample_id"],modalities,requested_mask,digests)
   out["runtime_release_id"]=self.manifest["release_id"]
   # Identity includes the original assembled result plus runtime implementation version.
   out["query_input_id"]=canonical({k:v for k,v in out.items() if k!="query_input_id"})
   outputs.append(out)
  return outputs
