"""CPU semantic-value utilization diagnostics on fixed real dev query caches."""
import json,math
from pathlib import Path
import torch
from torch.nn import functional as F
from .memory import MemoryBank,MemoryAdapter
from .semantic_values import SemanticValues
from .run_experiment import sha,write_json

def audit(root,p):
    torch.set_num_threads(2)
    caches=[torch.load(x,weights_only=True,map_location='cpu') for x in p['query_caches']]
    for x in caches:
        if x['bank_sha256']!=p['memory_bank_sha256'] or x['manifest_sha256']!=p['splits']['dev']['sha256']:raise ValueError('Query cache provenance mismatch')
    bank=MemoryBank.load(p['memory_bank']);semantic=SemanticValues.load(p['semantic_values'],bank,sha(p['semantic_values']))
    query=torch.cat([x['query'] for x in caches]);ids=[n for x in caches for n in x['clip_ids']]
    groups={x['name']:x['group_id'] for x in [json.loads(line) for line in Path(p['splits']['dev']['path']).read_text().splitlines()]}
    neighbor_ids=[row for x in caches for row in x['normal_neighbor_ids']];lookup={n:i for i,n in enumerate(bank.clip_ids)}
    av=bank.features[torch.tensor([[lookup[n] for n in row] for row in neighbor_ids])];mask=torch.ones(500,5,dtype=torch.bool)
    results={}
    for arm in p['training_arms']:
        checkpoint=root/'training'/arm['name']/'checkpoint_001334.pth';d=torch.load(checkpoint,weights_only=True,map_location='cpu',mmap=True)
        adapter=MemoryAdapter(d_value=2816).eval();adapter.load_state_dict({k.removeprefix('memory_adapter.'):v for k,v in d['model'].items() if k.startswith('memory_adapter.')},strict=True)
        with torch.no_grad():
            text,sources=semantic.lookup(neighbor_ids,ids,[groups[n] for n in ids],arm['content']);values=torch.cat([av,text],-1)
            tokens=adapter(query,values,mask).tokens;zero=adapter(query,torch.cat([av,torch.zeros_like(text)],-1),mask).tokens
            q=adapter.query_projection(query)[:,None]+adapter.queries[None];v=adapter.value_projection(values)
            _,w=adapter.attention(q,v,v,need_weights=True,average_attn_weights=False)
            entropy=-(w*w.clamp_min(1e-30).log()).sum(-1)/math.log(5)
            weight=adapter.value_projection[0].weight
            avsignal=F.linear(av,weight[:,:1792]);textsignal=F.linear(text,weight[:,1792:])
            results[arm['name']]={'checkpoint_sha256':sha(checkpoint),'semantic_content':arm['content'],
                'normal_attention_normalized_entropy_mean':float(entropy.mean()),'attention_max_weight_mean':float(w.max(-1).values.mean()),
                'tokens_vs_same_adapter_av_only_cosine_mean':float(F.cosine_similarity(tokens.flatten(1),zero.flatten(1)).mean()),
                'tokens_vs_same_adapter_av_only_relative_l2_mean':float(((tokens-zero).flatten(1).norm(dim=-1)/tokens.flatten(1).norm(dim=-1).clamp_min(1e-12)).mean()),
                'first_layer_av_signal_norm_mean':float(avsignal.norm(dim=-1).mean()),'first_layer_text_signal_norm_mean':float(textsignal.norm(dim=-1).mean()),
                'nonempty_semantic_slots':sum(x is not None for row in sources for x in row)}
        del adapter,d
    write_json(root/'reports/MECHANISM_AUDIT.json',{'N':500,'results':results,'scope':'fixed frozen real-dev query/AV candidates; internal sensitivity does not prove semantic correctness or benefit','all_artifacts_server_only':True})
