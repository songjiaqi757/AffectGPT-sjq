"""Independent sample-level heads; no Teacher labels or explanations are model inputs."""
from __future__ import annotations
from graph_paths import resolve_path as _graph_resolve_path
import contextlib, math
import torch
from torch import nn
from transformers import AutoModel, CLIPVisionModelWithProjection
from .temporal import AudioTemporalHead, VideoTemporalHead, temporal_spec

def segment_pad(features, owners, batch_size):
    pieces=[features[owners==i] for i in range(batch_size)]
    if any(len(p)==0 for p in pieces): raise ValueError("Empty sample sequence")
    padded=nn.utils.rnn.pad_sequence(pieces,batch_first=True)
    mask=torch.arange(padded.shape[1],device=features.device)[None,:]<torch.tensor([len(p) for p in pieces],device=features.device)[:,None]
    return padded,mask

class TemporalHead(nn.Module):
    def __init__(self,dim,n_cues,pooling="mean",dropout=.1,topk=3):
        super().__init__(); self.pooling=pooling; self.topk=topk
        self.classifier=nn.Sequential(nn.Linear(dim,256),nn.GELU(),nn.Dropout(dropout),nn.Linear(256,n_cues))
        self.attention=nn.Linear(dim,n_cues) if pooling=="attention" else None
    def forward(self,features,mask):
        if not mask.any(1).all(): raise ValueError("No valid time steps")
        if self.pooling=="mean":
            weights=mask.unsqueeze(-1).to(features.dtype)
            return self.classifier((features*weights).sum(1)/weights.sum(1))
        local=self.classifier(features)
        if self.pooling=="attention":
            scores=self.attention(features).float().masked_fill(~mask.unsqueeze(-1),-torch.inf)
            weights=scores.softmax(dim=1).to(local.dtype)
            return (weights*local).sum(1)
        if self.pooling=="topk":
            local=local.masked_fill(~mask.unsqueeze(-1),-torch.inf)
            outputs=[]
            for i in range(len(features)):
                k=min(self.topk,int(mask[i].sum()))
                outputs.append(local[i].topk(k,dim=0).values.mean(0))
            return torch.stack(outputs)
        raise ValueError("Unknown pooling")

class CueModel(nn.Module):
    def __init__(self,cfg):
        super().__init__(); self.cfg=cfg; self.modality=cfg["modality"]
        self.temporal_spec=temporal_spec(cfg)
        if self.modality=="visual":
            self.encoder=CLIPVisionModelWithProjection.from_pretrained(_graph_resolve_path(cfg['model_dir']), local_files_only=True)
            dim=self.encoder.config.projection_dim
        else:
            kwargs=dict(add_pooling_layer=False) if self.modality=="text" else {}
            self.encoder=AutoModel.from_pretrained(_graph_resolve_path(cfg['model_dir']), local_files_only=True, **kwargs)
            dim=self.encoder.config.hidden_size
            if self.modality=="audio": self.encoder.config.apply_spec_augment=False
        if self.modality=="text":
            self.head=nn.Sequential(nn.Linear(dim*2+2,256),nn.GELU(),nn.Dropout(cfg.get("dropout",.1)),nn.Linear(256,15))
        elif self.temporal_spec["temporal_model"]=="transformer":
            if self.modality == "audio":
                stride=1; receptive=1
                for kernel, step in zip(self.encoder.config.conv_kernel,self.encoder.config.conv_stride):
                    receptive += (kernel-1)*stride
                    stride *= step
                if (stride,receptive)!=(self.temporal_spec["audio_feature_stride_samples"],self.temporal_spec["audio_feature_receptive_field_samples"]):
                    raise ValueError("Audio timebase does not match encoder convolution geometry")
                self.head=AudioTemporalHead(dim,cfg)
            else:
                self.head=VideoTemporalHead(dim,cfg)
        else:
            self.head=TemporalHead(dim,17 if self.modality=="audio" else 10,cfg.get("pooling","mean"),cfg.get("dropout",.1),cfg.get("topk",3))
        self.encoder_mode=cfg.get("encoder_train","frozen")
        self._selected_modules=[]
        if self.encoder_mode!="full":
            self.encoder.requires_grad_(False)
            if self.encoder_mode=="last_layers":
                count=cfg.get("last_layers",2)
                if count<1: raise ValueError("last_layers must be positive")
                base=self.encoder.vision_model if self.modality=="visual" else self.encoder
                layers=base.encoder.layer if self.modality=="text" else base.encoder.layers
                if count>len(layers): raise ValueError("Too many last layers")
                modules=list(layers[-count:])
                if self.modality=="visual":
                    modules.extend([base.post_layernorm,self.encoder.visual_projection])
                elif hasattr(base.encoder,"layer_norm"): modules.append(base.encoder.layer_norm)
                for module in modules: module.requires_grad_(True)
                self._selected_modules=modules
        if cfg.get("gradient_checkpointing",False) and self.encoder_mode=="full":
            self.encoder.gradient_checkpointing_enable()
        self.train()
    def train(self,mode=True):
        super().train(mode)
        if hasattr(self,"encoder_mode") and self.encoder_mode!="full":
            self.encoder.eval()
            if mode:
                for module in self._selected_modules: module.train(True)
        return self
    def forward(self,batch):
        ctx=contextlib.nullcontext if any(p.requires_grad for p in self.encoder.parameters()) else torch.no_grad
        with ctx():
            if self.modality=="text":
                hidden=self.encoder(input_ids=batch["input_ids"],attention_mask=batch["attention_mask"]).last_hidden_state
                weights=batch["pool_weights"].to(hidden.dtype)
                summed=(hidden*weights.unsqueeze(-1)).sum(1)
                denominator=weights.sum(1)
                n=batch["language_present"].shape[0]*2
                features=torch.zeros((n,hidden.shape[-1]),device=hidden.device,dtype=hidden.dtype)
                normalizer=torch.zeros(n,device=hidden.device,dtype=hidden.dtype)
                features.index_add_(0,batch["owners"],summed); normalizer.index_add_(0,batch["owners"],denominator)
                features=(features/normalizer.clamp_min(1).unsqueeze(-1)).reshape(-1,2,hidden.shape[-1])
                present=batch["language_present"].to(hidden.dtype)
                features=features*present.unsqueeze(-1)
            elif self.modality=="audio":
                hidden=self.encoder(input_values=batch["input_values"],attention_mask=batch["attention_mask"]).last_hidden_state
                mask=self.encoder._get_feature_vector_attention_mask(hidden.shape[1],batch["attention_mask"]).bool()
                features=hidden
            else:
                parts=[]; chunk=self.cfg.get("frame_batch_size",8)
                if chunk<1: raise ValueError("frame_batch_size must be positive")
                for pixels in batch["pixel_values"].split(chunk):
                    parts.append(self.encoder(pixel_values=pixels).image_embeds)
                features,mask=segment_pad(torch.cat(parts),batch["frame_owners"],batch["batch_size"])
        if self.modality=="text":
            return self.head(torch.cat([features.flatten(1),present],dim=1))
        if self.temporal_spec["temporal_model"]=="transformer":
            if self.modality == "audio":
                return self.head(features,mask)
            return self.head(features,mask,batch["frame_time_offsets"])
        return self.head(features,mask)
    def checkpoint_state(self):
        names={n for n,p in self.named_parameters() if p.requires_grad}
        return {k:v.detach().cpu().clone() for k,v in self.state_dict().items() if not k.startswith("encoder.") or k in names}
    def restore_weights(self,state,initializing=False):
        result=self.load_state_dict(state,strict=False)
        if result.unexpected_keys: raise ValueError("Unexpected checkpoint keys: "+str(result.unexpected_keys))
        required={n for n,p in self.named_parameters() if p.requires_grad}
        bad=[k for k in result.missing_keys if k in required and (not initializing or not k.startswith("encoder."))]
        if bad: raise ValueError("Missing trainable checkpoint parameters: "+str(bad))

def build_optimizer(model,cfg):
    groups={}
    for name,p in model.named_parameters():
        if not p.requires_grad: continue
        lr=cfg.get("encoder_lr",2e-5) if name.startswith("encoder.") else cfg.get("head_lr",1e-3)
        decay=0. if p.ndim<=1 or name.endswith(".bias") else cfg.get("weight_decay",.01)
        groups.setdefault((lr,decay),[]).append(p)
    return torch.optim.AdamW([dict(params=ps,lr=lr,weight_decay=decay) for (lr,decay),ps in groups.items()])
