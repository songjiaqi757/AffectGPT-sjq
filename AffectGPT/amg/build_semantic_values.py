"""Offline BGE-M3 encoding of authorized FIT Memory subtitles/captions only."""
import argparse,json
from pathlib import Path
import torch
from torch.nn import functional as F
from .manifest import read_manifest,sha256_file
from .memory import MemoryBank
from .text import _validate_loading_info

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--memory-bank',required=True)
    p.add_argument('--field',choices=['subtitle','description'],required=True);p.add_argument('--output',required=True)
    p.add_argument('--model',default='/ai/sjq/AffectGPT-sjq/AffectGPT/models/bge-m3')
    p.add_argument('--device',default='cuda:0');p.add_argument('--batch-size',type=int,default=16);p.add_argument('--max-length',type=int,default=256)
    a=p.parse_args();dest=Path(a.output).resolve()
    if dest.exists():raise FileExistsError(dest)
    if a.max_length<2 or a.batch_size<1:raise ValueError('Invalid text budget')
    rows=read_manifest(a.manifest);bank=MemoryBank.load(a.memory_bank)
    if [r['name'] for r in rows]!=bank.clip_ids or [r['group_id'] for r in rows]!=bank.group_ids:raise ValueError('Need exact fit Memory order')
    bankmeta=json.loads(Path(a.memory_bank+'.json').read_text());fit_hash=sha256_file(a.manifest)
    if bankmeta['manifest_sha256']!=fit_hash:raise ValueError('Refuse non-fit text manifest')
    from transformers import AutoTokenizer,AutoModel
    torch.manual_seed(42);torch.set_num_threads(2)
    if a.device.startswith('cuda'):torch.cuda.set_per_process_memory_fraction(.25,torch.device(a.device))
    tokenizer=AutoTokenizer.from_pretrained(a.model,local_files_only=True,trust_remote_code=False)
    model,info=AutoModel.from_pretrained(a.model,local_files_only=True,trust_remote_code=False,add_pooling_layer=False,output_loading_info=True)
    _validate_loading_info(info);model.requires_grad_(False).eval().to(a.device)
    if a.device.startswith('cuda'):model.half()
    hashes={str(x.relative_to(a.model)):sha256_file(x) for x in sorted(Path(a.model).rglob('*')) if x.is_file() and x.suffix in ['.bin','.safetensors','.model','.json','.txt'] and '.git' not in x.parts}
    encoder_sha=__import__('hashlib').sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    dense=torch.zeros(len(rows),1024);valid=torch.tensor([bool(r[a.field].strip()) for r in rows]);lengths=[]
    with torch.inference_mode():
        for start in range(0,len(rows),a.batch_size):
            end=min(start+a.batch_size,len(rows));ix=[i for i in range(start,end) if valid[i]]
            if ix:
                texts=[rows[i][a.field] for i in ix]
                lengths.extend(len(x) for x in tokenizer(texts,add_special_tokens=True,truncation=False)['input_ids'])
                batch=tokenizer(texts,padding=True,truncation=True,max_length=a.max_length,return_tensors='pt')
                hidden=model(**{k:v.to(a.device) for k,v in batch.items()}).last_hidden_state
                out=F.normalize(hidden[:,0].float(),dim=-1).cpu()
                if out.shape!=(len(ix),1024) or not torch.isfinite(out).all():raise ValueError('Invalid BGE dense output')
                dense[ix]=out
            if start==0 or end%512==0 or end==len(rows):print(json.dumps({'field':a.field,'encoded':end,'total':len(rows)}),flush=True)
    payload={'schema':'amg-fit-semantic-cache-v1','clip_ids':bank.clip_ids,'group_ids':bank.group_ids,'dense':dense,'valid':valid,
             'fit_sha256':fit_hash,'bank_sha256':sha256_file(a.memory_bank),'field':a.field,'encoder_sha256':encoder_sha,
             'encoder_artifacts':hashes,'encoder_model_path':str(Path(a.model).resolve()),'pooling':'L2-normalized last_hidden_state[:,0]',
             'max_length':a.max_length,'dtype':'fp16 encoder / fp32 pooled dense','input_contract':'offline FIT historical Memory value only; not query text or retrieval keys',
             'text_statistics':{'valid':int(valid.sum()),'missing':int((~valid).sum()),'truncated':sum(n>a.max_length for n in lengths),'max_tokens':max(lengths,default=0)}}
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb') as f:torch.save(payload,f)
    meta={k:v for k,v in payload.items() if k not in ['dense','valid']};meta['sha256']=sha256_file(dest)
    Path(str(dest)+'.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(dest),'sha256':meta['sha256'],'statistics':payload['text_statistics']}),flush=True)
if __name__=='__main__':main()
