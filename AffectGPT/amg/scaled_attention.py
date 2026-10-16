"""Opt-in memory attention logit scaling; default delegates to PyTorch unchanged."""
import math
import torch
from torch import nn
from torch.nn import functional as F

class LogitScaledAttention(nn.MultiheadAttention):
    def __init__(self, *args, logit_scale=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        if not math.isfinite(logit_scale) or logit_scale <= 0:
            raise ValueError('logit_scale must be finite and positive')
        self.logit_scale = float(logit_scale)

    def forward(self, query, key, value, key_padding_mask=None, need_weights=True,
                attn_mask=None, average_attn_weights=True, is_causal=False):
        if self.logit_scale == 1.0:
            return super().forward(query, key, value, key_padding_mask=key_padding_mask,
                need_weights=need_weights, attn_mask=attn_mask,
                average_attn_weights=average_attn_weights, is_causal=is_causal)
        if (not self.batch_first or not self._qkv_same_embed_dim or self.bias_k is not None
            or self.bias_v is not None or self.add_zero_attn or attn_mask is not None or is_causal):
            raise ValueError('Scaled experimental path supports batch-first equal-dim noncausal memory attention only')
        b,t,d=query.shape; k=key.shape[1];h=self.num_heads;hd=d//h
        weights=self.in_proj_weight.chunk(3,0)
        biases=self.in_proj_bias.chunk(3,0) if self.in_proj_bias is not None else (None,)*3
        q,kk,v=[F.linear(x,w,bb).reshape(b,-1,h,hd).transpose(1,2)
                  for x,w,bb in zip((query,key,value),weights,biases)]
        logits=(q.float() @ kk.float().transpose(-2,-1))*(self.logit_scale/math.sqrt(hd))
        if key_padding_mask is not None:
            if key_padding_mask.dtype != torch.bool:
                raise ValueError('Only boolean key padding masks supported')
            if key_padding_mask.all(-1).any():
                raise ValueError('All-masked memory rows must bypass attention')
            logits=logits.masked_fill(key_padding_mask[:,None,None,:],-torch.inf)
        probs=logits.softmax(-1)
        used=F.dropout(probs,p=self.dropout,training=self.training)
        attended=(used.to(v.dtype) @ v).transpose(1,2).reshape(b,t,d)
        output=F.linear(attended,self.out_proj.weight,self.out_proj.bias)
        result=None if not need_weights else (probs.mean(1) if average_attn_weights else probs)
        return output,result
