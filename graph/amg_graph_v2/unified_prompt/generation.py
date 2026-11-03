"""Run frozen P0-P5 source probes using an already loaded AffectGPT Predictor when GPU is available."""
import collections,json,random,time
from .common import *
def run_paired_generation(predictor,artifact_directory,checkpoint_spec,output_directory,seed=42):
 import numpy as np
 import torch
 run=Path(artifact_directory);out=Path(output_directory);out.mkdir(parents=True,exist_ok=True);manifest=read(run/'release_manifest.json');expected_checkpoint=checkpoint_spec['sha256'];predictor.load(checkpoint_spec)
 if predictor.loaded!=expected_checkpoint:raise ValueError('Wrong frozen AffectGPT checkpoint')
 expected_inputs=manifest['artifact_sha256']['prompts/source_probe_P0_P5.jsonl']
 if sha(run/'prompts/source_probe_P0_P5.jsonl')!=expected_inputs:raise ValueError('Frozen paired prompts changed')
 rows={r['sample_id']:r for r in read(BASE/'data/input_rows.json')};records=collections.defaultdict(list)
 for line in (run/'prompts/source_probe_P0_P5.jsonl').read_text().splitlines():
  item=json.loads(line);records[item['sample_id']].append(item)
 settings=dict(max_new_tokens=512,max_length=2048,num_beams=1,temperature=1.,do_sample=False,top_p=.9,min_length=1,repetition_penalty=1.,length_penalty=1.);binding=dict(adapter_release_id=manifest['release_id'],checkpoint=checkpoint_spec,generation=settings,seed=seed,source_probe_sha256=sha(run/'validation/source_probe_manifest.json'),target_datasets_used=False)
 if (out/'binding.json').exists() and read(out/'binding.json')!=binding:raise ValueError('Output directory belongs to a different frozen experiment')
 write(out/'binding.json',binding)
 for sid,items in records.items():
  if {i['condition'] for i in items}!={'P0','P1','P2','P3','P4','P5'}:raise ValueError('Incomplete paired conditions')
  row=rows[sid];face=PROJECT/'dataset/mer2025-dataset/openface_face'/sid/(sid+'.npy');pair_seed=(seed+int(digest([expected_checkpoint,sid])[:8],16))%2**32
  with torch.inference_mode():
   media=predictor.reader.read_frame_face_audio_text(video_path=None,face_npy=str(face),audio_path=row['audio_path'],image_path=None);ah,al=predictor.chat.postprocess_audio(media);fh,fl=predictor.chat.postprocess_face(media);_,ml=predictor.chat.postprocess_multi(fh,ah);features=dict(audio=al,face=fl,multi=ml,frame=None,image=None)
   if any(x is None for x in [al,fl,ml]):raise ValueError('An original input modality is missing; sample was not silently excluded')
   for item in sorted(items,key=lambda x:x['condition']):
    dest=out/(sid+'_'+item['condition']+'.json')
    if dest.exists():
     previous=read(dest)
     if previous['checkpoint_sha256']!=expected_checkpoint or previous['adapter_release_id']!=manifest['release_id'] or previous['prompt_sha256']!=digest(item['final_prompt']) or previous['seed']!=pair_seed:raise ValueError('Stale paired-generation response found')
     continue
    prompt=item['final_prompt'];actual_tokens=len(predictor.chat.tokenizer.encode(predictor.chat.replace_token_for_multimodal(prompt),add_special_tokens=False))
    if actual_tokens!=item['packet']['audit']['full_prompt_tokens'] or actual_tokens+512>2048:raise ValueError('Actual inference tokenizer/context differs from frozen input preflight')
    random.seed(pair_seed);np.random.seed(pair_seed);torch.manual_seed(pair_seed);torch.cuda.manual_seed_all(pair_seed);response=predictor.chat.answer_sample(prompt,features,**settings);torch.cuda.synchronize();write(dest,dict(sample_id=sid,condition=item['condition'],response=response,seed=pair_seed,checkpoint_sha256=expected_checkpoint,prompt_sha256=digest(prompt),actual_tokens=actual_tokens,adapter_release_id=manifest['release_id'],actual_model_generation_run=True))
  event('paired_source_sample_generated',sample_id=sid,conditions=6)
 write(out/'status.json',dict(status='paired_generation_complete',samples=len(records),conditions=6,checkpoint_sha256=expected_checkpoint,downstream_scoring='not_performed_by_this_function',target_datasets_used=False));return read(out/'status.json')
