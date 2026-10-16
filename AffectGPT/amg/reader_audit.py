"""CPU replay of fixed real dev query/neighbor caches, never an extra task score."""
import json,math
from pathlib import Path
import torch
import torch.nn.functional as F
from .memory import MemoryBank,MemoryAdapter
from .run_experiment import write_json,sha

def audit_arms(root,p):
    torch.set_num_threads(2)
    caches=[torch.load(x,map_location='cpu',weights_only=True) for x in p['query_caches']]
    for cache in caches:
        if cache['bank_sha256']!=p['bank_sha256'] or cache['manifest_sha256']!=p['splits']['dev']['sha256']:
            raise RuntimeError('Query cache provenance mismatch')
    query=torch.cat([x['query'] for x in caches]);bank=MemoryBank.load(p['memory_bank'])
    lookup={name:i for i,name in enumerate(bank.clip_ids)}
    def values(field):
        ids=[row for x in caches for row in x[field]]
        return bank.features[torch.tensor([[lookup[n] for n in row] for row in ids])]
    normal,random=values('normal_neighbor_ids'),values('random_neighbor_ids');mask=torch.ones(500,5,dtype=torch.bool)
    results={}
    for arm in p['training_arms']:
        ckpt=root/'training'/arm['name']/'checkpoint_001334.pth'
        state=torch.load(ckpt,map_location='cpu',weights_only=True,mmap=True)
        adapter=MemoryAdapter(attention_logit_scale=arm['scale']).eval()
        adapter.load_state_dict({k.removeprefix('memory_adapter.'):v for k,v in state['model'].items() if k.startswith('memory_adapter.')},strict=True)
        with torch.no_grad():
            a=adapter(query,normal,mask).tokens;b=adapter(query,random,mask).tokens
            q=adapter.query_projection(query)[:,None,:]+adapter.queries[None]
            v=adapter.value_projection(normal)
            _,w=adapter.attention(q,v,v,need_weights=True,average_attn_weights=False)
            entropy=-(w*w.clamp_min(1e-30).log()).sum(-1)/math.log(5)
            relative=(a-b).flatten(1).norm(dim=-1)/a.flatten(1).norm(dim=-1).clamp_min(1e-12)
            results[arm['name']]={'checkpoint_sha256':sha(ckpt),'attention_logit_scale':arm['scale'],
                'normal_attention_normalized_entropy_mean':float(entropy.mean()),'normal_attention_max_weight_mean':float(w.max(-1).values.mean()),
                'fixed_normal_random_tokens_cosine_mean':float(F.cosine_similarity(a.flatten(1),b.flatten(1)).mean()),
                'fixed_normal_random_tokens_relative_l2_mean':float(relative.mean()),'normal_token_norm_mean':float(a.flatten(1).norm(dim=-1).mean())}
        del state,adapter
    write_json(root/'reports'/'MECHANISM_AUDIT.json',{'N':500,'results':results,
        'scope':'fixed historical real-query/neighbor caches; not the new random inference selections; internal sensitivity only',
        'attention_sharpness_is_not_task_benefit':True,'all_artifacts_server_only':True})
