"""Fit-only semantic Memory values. Retrieval keys and query inputs stay AV-only."""
from pathlib import Path
import json,random
import torch

MODES=('av_only','subtitle','caption','shuffled_caption')
class SemanticValues:
    dim=1024
    def __init__(self,ids,groups,subtitle,caption,subtitle_valid,caption_valid,*,bank_sha256,fit_sha256,seed=42):
        self.ids=list(ids);self.groups=list(groups);self.index={n:i for i,n in enumerate(ids)}
        n=len(ids)
        if not n or len(self.index)!=n or len(groups)!=n:raise ValueError('Invalid semantic identities')
        self.features={'subtitle':subtitle.float().cpu(),'caption':caption.float().cpu()}
        self.valid={'subtitle':subtitle_valid.bool().cpu(),'caption':caption_valid.bool().cpu()}
        for name,x in self.features.items():
            if tuple(x.shape)!=(n,1024) or tuple(self.valid[name].shape)!=(n,) or not torch.isfinite(x).all():raise ValueError('Invalid semantic features')
            if not torch.allclose(x[~self.valid[name]],torch.zeros_like(x[~self.valid[name]])):raise ValueError('Missing text must be zero')
        self.bank_sha256=bank_sha256;self.fit_sha256=fit_sha256;self.seed=seed
        self.permutation=list(range(n));random.Random(seed).shuffle(self.permutation)
        # A deterministic derangement; same-group donors are also rejected below.
        if n<2:raise ValueError('Shuffle control needs at least two records')
        for i in range(n):
            if self.permutation[i]==i:
                j=(i+1)%n;self.permutation[i],self.permutation[j]=self.permutation[j],self.permutation[i]
        if all(g==groups[0] for g in groups):raise ValueError('Need multiple groups')
    @classmethod
    def load(cls,path,bank,expected_sha256=None):
        from .manifest import sha256_file
        if expected_sha256 and sha256_file(path)!=expected_sha256:raise ValueError('Semantic artifact hash mismatch')
        d=torch.load(path,map_location='cpu',weights_only=True)
        if d.get('schema')!='amg-semantic-fit-values-v1':raise ValueError('Invalid semantic artifact schema')
        if d['clip_ids']!=bank.clip_ids or d['group_ids']!=bank.group_ids:raise ValueError('Semantic/AV identities must match exactly')
        return cls(d['clip_ids'],d['group_ids'],d['subtitle'],d['caption'],d['subtitle_valid'],d['caption_valid'],
                   bank_sha256=d['bank_sha256'],fit_sha256=d['fit_sha256'],seed=d['shuffle_seed'])
    def lookup(self,neighbor_ids,query_ids,query_groups,mode):
        if mode not in MODES:raise ValueError('Unknown semantic content')
        b=len(neighbor_ids);k=len(neighbor_ids[0]);out=torch.zeros(b,k,1024);sources=[]
        if len(query_ids)!=b or len(query_groups)!=b:raise ValueError('Query provenance required')
        for i,row in enumerate(neighbor_ids):
            source_row=[]
            for j,name in enumerate(row):
                if name is None or mode=='av_only':source_row.append(None);continue
                idx=self.index[name]
                if mode=='shuffled_caption':
                    donor=self.permutation[idx]
                    # Fixed global permutation, deterministic repair only when a
                    # donor is same-group or the query's own training caption.
                    forbidden={self.groups[idx],query_groups[i]}
                    for _ in range(len(self.ids)):
                        if self.groups[donor] not in forbidden and self.ids[donor]!=query_ids[i]:break
                        donor=(donor+1)%len(self.ids)
                    else:raise ValueError('No safe shuffled caption donor')
                    idx=donor
                if self.ids[idx]==query_ids[i] or self.groups[idx]==query_groups[i]:
                    raise ValueError('Query/self-group semantic value leakage')
                field='subtitle' if mode=='subtitle' else 'caption'
                if self.valid[field][idx]:out[i,j]=self.features[field][idx];source_row.append(self.ids[idx])
                else:source_row.append(None)
            sources.append(source_row)
        return out,sources

def merge_caches(subtitle_path,caption_path,output,bank_sha256,fit_sha256):
    a=torch.load(subtitle_path,weights_only=True,map_location='cpu');b=torch.load(caption_path,weights_only=True,map_location='cpu')
    if a['field']!='subtitle' or b['field']!='description':raise ValueError('Wrong cache text roles')
    for key in ['clip_ids','group_ids','fit_sha256','bank_sha256','encoder_sha256','max_length']:
        if a[key]!=b[key]:raise ValueError('Text caches differ in '+key)
    if a['fit_sha256']!=fit_sha256 or a['bank_sha256']!=bank_sha256:raise ValueError('Cache provenance mismatch')
    d={'schema':'amg-semantic-fit-values-v1','clip_ids':a['clip_ids'],'group_ids':a['group_ids'],
       'subtitle':a['dense'],'caption':b['dense'],'subtitle_valid':a['valid'],'caption_valid':b['valid'],
       'fit_sha256':fit_sha256,'bank_sha256':bank_sha256,'shuffle_seed':42,
       'encoder_sha256':a['encoder_sha256'],'max_length':a['max_length'],'source_contract':'fit-only; no query descriptions or gold read online'}
    with Path(output).open('xb') as f:torch.save(d,f)
    return d
