"""CPU checks for BCD loss isolation, graph dropout, data provenance and work distribution."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,collections,copy,json,os,sys
from graph_paths import Path
from .common import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);a=ap.parse_args();run=Path(a.run);p=plan(run)
 for f in (ROOT/"amg_bcd_polarity_oof").glob("*.py"):compile(f.read_text(),str(f),"exec")
 from .verify_oof import verify_oof
 oof_report=verify_oof(run,p)
 records=read(run/"train_records.json");audit=read(run/"human_audit_500.json");labels=read(run/"polarity_labels.json")
 require(len(records)==30755 and len({x["sample_id"] for x in records})==30755,"Training size changed")
 require(len(audit)==500 and not ({x["sample_id"] for x in records}&{x["sample_id"] for x in audit}),"Audit overlap")
 require({x["sample_id"] for x in labels}=={x["sample_id"] for x in records},"Polarity coverage mismatch")
 require(_graph_hash_matches(run / 'polarity_labels.json', p['polarity_labels_sha256'], sha(run / 'polarity_labels.json')),"Polarity file changed")
 require(sum(x["valid_for_polarity_loss"] for x in labels)==30688 and sum(not x["valid_for_polarity_loss"] for x in labels)==67,"Polarity mask changed")
 require(all(x["polarity_id"] in [0,1,2] if x["valid_for_polarity_loss"] else x["polarity_id"]==-100 for x in labels),"Invalid auxiliary target")
 require(_graph_hash_matches(p['base_checkpoint']['path'], p['base_checkpoint']['sha256'], sha(p['base_checkpoint']['path'])),"Original checkpoint35 changed")
 require(p["base_checkpoint"]["base_epoch"]==35 and p["epochs"]==[36,37,38,39,40],"Incorrect start/epochs")
 old=read(SOURCE/"plan.json")
 require(_graph_hash_matches(run / 'train_records.json', old['inputs']['train_records_sha256'], sha(run / 'train_records.json')) and _graph_hash_matches(run / 'human_audit_500.json', old['inputs']['audit_records_sha256'], sha(run / 'human_audit_500.json')),"Source manifests changed")
 for d,spec in p["datasets"].items():require(_graph_hash_matches(spec['path'], spec['sha256'], sha(spec['path'])) and len(read(spec["path"]))==spec["samples"],"Target membership changed")
 for filename,binding in read(run/"model_assets_manifest.json")["assets"].items():
  st=Path(filename).stat();require(st.st_size==binding["bytes"] and st.st_mtime_ns==binding["mtime_ns"],"Model asset changed")
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"))
 from .dataset import graph_enabled
 masks={v:[graph_enabled(x["sample_id"],1,v) for x in records] for v in ["B","C","D"]}
 require(masks["B"]==masks["D"] and all(masks["C"]),"Inconsistent paired graph masks")
 fraction=sum(masks["B"])/len(records);require(.49<fraction<.51,"Graph dropout probability incorrect")
 require(any(graph_enabled(x["sample_id"],1,"B")!=graph_enabled(x["sample_id"],2,"B") for x in records[:100]),"Graph dropout not resampled")
 import torch
 from .auxiliary import prompt_positions
 from transformers import Qwen2Config,Qwen2Model
 torch.manual_seed(42);torch.set_num_threads(2)
 tiny=Qwen2Model(Qwen2Config(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=2,max_position_embeddings=64,attention_dropout=0.0)).eval()
 ids=torch.tensor([[1,2,3,4,5,6],[7,8,9,10,11,12]]);target=torch.tensor([[-100,-100,-100,4,5,6],[-100,-100,-100,10,11,12]])
 pos=prompt_positions(target);require(pos.tolist()==[2,2],"Prompt boundary includes answer")
 h1=tiny(input_ids=ids).last_hidden_state[torch.arange(2),pos]
 changed=ids.clone();changed[:,3:]=torch.tensor([[21,22,23],[24,25,26]])
 h2=tiny(input_ids=changed).last_hidden_state[torch.arange(2),pos]
 require(torch.allclose(h1,h2,atol=1e-6,rtol=1e-6),"Polarity representation leaks future answers")
 embeds=tiny.embed_tokens(ids).detach().requires_grad_(True);head=torch.nn.Linear(32,3)
 out=tiny(inputs_embeds=embeds).last_hidden_state[torch.arange(2),pos];logits=head(out)
 loss=torch.nn.functional.cross_entropy(logits,torch.tensor([0,-100]),ignore_index=-100);loss.backward()
 require(bool(embeds.grad[0,:3].abs().sum()>0) and not bool(embeds.grad[0,3:].abs().sum()) and not bool(embeds.grad[1].abs().sum()),"Masked polarity gradient leaks")
 from my_affectgpt.models.tokenizer import load_tokenizer_from_LLM
 from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
 from .policy import make_tokens,format_evidence,gate
 t=load_tokenizer_from_LLM("Qwen25");reader=BaseDataset.__new__(BaseDataset);reader.tokenizer=t;reader.dataset="MERCaptionPlus";reader.face_or_frame="multiface_audio_face_text"
 cfg=read(run/"original_config.json")["model"]
 for key in ["num_audio_query_token","num_video_query_token","num_multi_query_token","num_image_query_token"]:setattr(reader,key,cfg[key])
 for attr,marker in [("IMAGE_PATCH_TOKEN_ID","<ImageHere>"),("AUDIO_PATCH_TOKEN_ID","<AudioHere>"),("FRAME_PATCH_TOKEN_ID","<FrameHere>"),("FACE_PATCH_TOKEN_ID","<FaceHere>"),("MULTI_PATCH_TOKEN_ID","<MultiHere>")]:setattr(reader,attr,t.get_vocab()[marker])
 selected={x["sample_id"]:x for x in records[::max(1,len(records)//48)]}
 for key,n in [("description",24),("subtitle",16)]:
  for x in sorted(records,key=lambda x:len(x[key]),reverse=True)[:n]:selected[x["sample_id"]]=x
 maximum=0;checked=0;drop_count=0
 for row in selected.values():
  cache=read(Path(p["oof_cache"])/(row["sample_id"]+".json"));require(cache["cache_id"]==canonical({k:v for k,v in cache.items() if k!="cache_id"}),"Source cache changed")
  require(cache["evidence"]["query_config_id"]==p["oof_folds"][str(cache["fold"])]["query_config_id"],"Fold query parameters changed")
  for keep in [True,False]:
   ev=copy.deepcopy(cache["evidence"])
   for task in ["description","ovlabel"]:
    prompt,answer,text,info=make_tokens(reader,row,ev,task,p["training"],"D",None if keep else 0.0);maximum=max(maximum,len(prompt)+len(answer)+2);checked+=1
    require(len(prompt)+len(answer)+2<=1398,"No-GC sequence envelope exceeded")
    require((keep or info["graph_tokens"]==0) and info["graph_tokens"]<=512,"Dropout or compact graph budget failed")
    for marker,count in zip(["<ImageHere>","<AudioHere>","<FrameHere>","<FaceHere>","<MultiHere>"],[0,1,0,1,1]):require(text.count(marker)==count,"Raw modalities missing")
    if not keep:drop_count+=1
 require(len(jobs(run))==45 and len(list((run/"shards").glob("*.json")))==360,"Wrong inference budget")
 require(sum(x["samples"] for x in jobs(run))==21000,"Prediction coverage budget wrong")
 # Exercise real exclusive shard claim without touching the live queue.
 from .infer_worker import choose
 fixture=run/"claim_fixture";fixture.mkdir();(fixture/"shards").mkdir()
 for v in ["B","C","D"]:(fixture/v).mkdir();atomic_json(fixture/v/"checkpoints.json",[dict(epoch=36,path="fixture",sha256="fixture")])
 for i,n in enumerate([411,532,457]):
  atomic_json(fixture/"shards"/f"{i}.json",dict(variant="B",epoch=36,dataset_samples=n,samples=64,state="pending",attempts=0))
 a=choose(fixture,p);b=choose(fixture,p)
 require(a[2]["dataset_samples"]==532 and b[2]["dataset_samples"]==457,"LPT or exclusive shard claim failed");a[1].close();b[1].close()
 # Missing or incomplete inference must keep the global scoring barrier closed.
 require(complete_count(run)==0 and not (run/"evaluation_barrier.json").exists(),"Evaluation started early")
 resources=read(OLD_INFER/"phases/priority_20x3_20261023_121637/evaluation_lock.json")
 lock=dict(files=resources["files_sha256"],original_sampling_preserved=True,source_evaluation_lock=resources["lock_id"])
 for path,digest in lock["files"].items():require(_graph_hash_matches(path, digest, sha(path)),"Original evaluation changed")
 lock["lock_id"]=canonical(lock);atomic_json(run/"evaluation_resources.json",lock)
 paths=list((ROOT/"amg_bcd_polarity_oof").glob("*.py"))
 for folder in ["amg_finetune_nogc","amg_runtime","amg_inference"]:paths+=list((ROOT/folder).glob("*.py"))
 paths+=[run/"oof_cache_inventory.json",run/"oof_reuse_verification.json"]
 paths+=[ROOT/"AffectGPT/my_affectgpt/models/affectgpt.py",ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py"]
 manifest=dict(files={str(f.relative_to(ROOT)):sha(f) for f in paths},created_at_beijing=now());atomic_json(run/"code_manifest.json",manifest)
 for v in p["variants"]:(run/(v+"_plan")/"code_manifest.json").symlink_to(run/"code_manifest.json")
 report=dict(passed=True,graph_oof_records_verified=oof_report["samples"],all_variants_compact_gate_oof=True,cpu_only=True,gpu_model_calls=0,training_records=30755,polarity_valid=30688,polarity_ignored=67,audit_records=500,graph_probability_first_visit=fraction,paired_B_D_mask=True,causal_answer_invariance=True,polarity_gradient_reaches_prefix=True,answer_and_ignored_samples_zero_polarity_gradient=True,prompt_examples=len(selected),prompt_tasks_checked=checked,maximum_checked_sequence_tokens=maximum,logical_jobs=45,shards=360,predictions=21000,lpt_exclusive_claim=True,global_scoring_barrier=True,completed_at_beijing=now())
 atomic_json(run/"cpu_preflight.json",report);print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
