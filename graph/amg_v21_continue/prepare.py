"""Graph-only grouped OOF with v2.1 admission and the frozen P4 serializer."""
import argparse,collections,copy,json,os,sys,time,traceback
from pathlib import Path
import numpy as np
from .common import *
from .policy import gate,restricted_graph,make_tokens
def initialize(run):
 p=load_plan(run);base=ROOT/"amg_graph_v2"
 z=dict(np.load(base/"data/labels.npz"));rows=read(run/"train_records.json")
 assert set(z["sample_ids"])=={r["sample_id"] for r in rows}
 gm=read(base/"v21/data/group_manifest.json");groups_by_id=dict(zip(gm["sample_ids"],gm["group_ids"]))
 groups=np.array([groups_by_id[s] for s in z["sample_ids"]]);unique=np.unique(groups);rng=np.random.default_rng(42);rng.shuffle(unique);mapping={g:i%5 for i,g in enumerate(unique)};assignment=np.array([mapping[g] for g in groups])
 assignment_doc=dict(sample_ids=z["sample_ids"].tolist(),groups=groups.tolist(),folds=assignment.tolist(),seed=42,split_unit="source IDs + exact audio/video hashes + existing conservative transcript groups",student_retrained=False,graph_only=True)
 atomic_json(run/"fold_assignment.json",assignment_doc)
 config=read(base/"config.json");config["fusion_alpha_grid"]=[0]
 original_dev=dict(np.load(base/"v21/data/development.npz"));original_eval=dict(np.load(base/"v21/data/internal_evaluation.npz"));where={s:i for i,s in enumerate(z["sample_ids"])}
 for k in range(5):
  fold=run/"folds"/str(k);out=fold/"v2";(out/"data").mkdir(parents=True,exist_ok=True)
  held=assignment==k;zz={key:val.copy() for key,val in z.items()}
  for mask in ["train","tune","evaluation"]:zz[mask]&=~held
  zz["groups"]=groups.copy()
  zz["fold"]=np.array([int(canonical([20261105,g])[:12],16)%5 for g in groups])
  np.savez_compressed(out/"data/labels.npz",**zz)
  atomic_json(out/"data/prepared.json",read(base/"data/prepared.json"));atomic_json(out/"config.json",config)
  import shutil
  shutil.copyfile(base/"data/cue_scores.npz",out/"data/cue_scores.npz")
  v21=fold/"v21";(v21/"data").mkdir(parents=True,exist_ok=True)
  for name,data in [("development",original_dev),("internal_evaluation",original_eval)]:
   take=np.array([not held[where[s]] for s in data["sample_ids"]])
   sliced={key:val[take] for key,val in data.items()}
   np.savez_compressed(v21/"data"/(name+".npz"),**sliced)
  atomic_json(v21/"data/prepared.json",read(base/"v21/data/prepared.json"));atomic_json(v21/"config.json",read(base/"v21/config.json"))
  fit_groups=set(groups[zz["train"]]);tune_groups=set(groups[zz["tune"]]);eval_groups=set(groups[zz["evaluation"]]);held_groups=set(groups[held]);assert not held_groups&(fit_groups|tune_groups|eval_groups)
  atomic_json(fold/"membership.json",dict(fold=k,fit_ids=z["sample_ids"][zz["train"]].tolist(),tune_ids=z["sample_ids"][zz["tune"]].tolist(),branch_audit_ids=z["sample_ids"][zz["evaluation"]].tolist(),held_ids=z["sample_ids"][held].tolist(),held_group_overlap=0,held_groups=sorted(held_groups),fit_groups=sorted(fit_groups),no_held_labels_used_for_relations_calibration_edges_or_admission=True,Student_predictions="Frozen original in-sample Students; graph-only OOF",AE_disabled=True))
 atomic_json(run/"preparation_initialized.json",dict(complete=True,samples=len(rows),folds=5,all_operations_on_server=True))
 print("INITIALIZED",run,flush=True)

def runtime_and_adapter(run,k,tokenizer):
 from amg_graph_v2.v21.runtime import SampleGraphV21
 from amg_graph_v2.unified_prompt.adapter import UnifiedAMGPromptAdapter
 p=load_plan(run);fold=run/"folds"/str(k);g=SampleGraphV21(p["graph_v21_release"]);work=fold/"v2/work";g.model=dict(np.load(work/"G1.npz"));g.cal=read(work/"calibration.json");assert g.cal["path_branch_enabled"] is False
 g.edges=read(work/"admitted_edges.json");g.paths=[];g.policy=read(fold/"v21/work/cue_admission_policy.json")
 g.release_id="amg_v21_graph_oof_fold_"+str(k)+"_"+sha(work/"G1.npz")[:16]
 g.by_target={typ:collections.defaultdict(list) for typ in g.edges}
 for typ,edges in g.edges.items():
  for e in edges:g.by_target[typ][e["target_index"]].append(e)
 g._stable={}
 for typ in ["CA","CE"]:
  mask=np.zeros_like(g.model[typ],bool)
  for e in g.edges[typ]:mask[e["source_index"],e["target_index"]]=True
  g._stable[typ]=mask
 zz=np.load(fold/"v2/data/labels.npz")
 for d,row in enumerate(g.app_metadata):row["valid_training_samples"]=int(zz["app_mask"][zz["train"],d].sum())
 adapter=UnifiedAMGPromptAdapter(tokenizer,graph_release=p["graph_v21_release"])
 adapter.model=g.model;adapter.admission=g.policy;adapter.manifest=dict(adapter.manifest,release_id=g.release_id);adapter.config=dict(adapter.config,graph_release_id=g.release_id,evidence_token_budget=p["training"]["graph_token_budget"],max_prompt_tokens=p["training"]["prompt_token_budget"]);adapter.stable=g._stable;adapter.edges={(typ,e["source_index"],e["target_index"]):e for typ,edges in g.edges.items() for e in edges}
 return g,adapter
def reader_for(run):
 os.chdir(PROJECT/"AffectGPT");sys.path.insert(0,str(PROJECT/"AffectGPT"))
 from my_affectgpt.models.tokenizer import load_tokenizer_from_LLM
 from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
 tokenizer=load_tokenizer_from_LLM("Qwen25")
 reader=BaseDataset.__new__(BaseDataset);reader.tokenizer=tokenizer;reader.dataset="MERCaptionPlus";reader.face_or_frame="multiface_audio_face_text"
 cfg=read(run/"original_config.json")["model"]
 for key in ["num_audio_query_token","num_video_query_token","num_multi_query_token","num_image_query_token"]:setattr(reader,key,cfg[key])
 for attr,marker in [("IMAGE_PATCH_TOKEN_ID","<ImageHere>"),("AUDIO_PATCH_TOKEN_ID","<AudioHere>"),("FRAME_PATCH_TOKEN_ID","<FrameHere>"),("FACE_PATCH_TOKEN_ID","<FaceHere>"),("MULTI_PATCH_TOKEN_ID","<MultiHere>")]:setattr(reader,attr,tokenizer.get_vocab()[marker])
 return reader
def evidence(run,k):
 p=load_plan(run);fold=run/"folds"/str(k);membership=read(fold/"membership.json");held=set(membership["held_ids"]);reader=reader_for(run);graph,adapter=runtime_and_adapter(run,k,reader.tokenizer)
 from amg_graph_v2.unified_prompt.integration import AffectGPTUnifiedBridge
 bridge=AffectGPTUnifiedBridge(adapter)
 z=np.load(ROOT/"amg_graph_v2/data/labels.npz");q=dict(np.load(ROOT/"amg_graph_v2/data/cue_scores.npz"));where={s:i for i,s in enumerate(z["sample_ids"])};rows=[r for r in read(run/"train_records.json") if r["sample_id"] in held];counts=collections.Counter();maxseq=0;maxprompt=0;examples=[]
 from amg_finetune_nogc.prompts import clean_text,encode
 tmp=fold/"evidence.jsonl.tmp";ntests=0
 with tmp.open("w") as out:
  for n,row in enumerate(rows):
   sid=row["sample_id"];j=where[sid];scores=[float(q["scores"][j,h]) if q["available"][j,h] else None for h in range(42)]
   sg=graph.build(sid,scores,q["available"][j].tolist());sg.update(G1_refitted=True,graph_only_oof=True,held_fold=k,cue_training_predictions_oof=False);level,reasons=gate(sg);counts[level]+=1
   questions=[reader.get_qa_pairs(reader.dataset,t,row)["question"] for t in ["description","ovlabel"]]
   def count(text):
    return max(len(encode(reader.tokenizer,reader.replace_token_for_multimodal(reader.get_prompt_for_multimodal(reader.face_or_frame,clean_text(row["subtitle"]),question+("\n\n"+text if text else ""))))) for question in questions)
   assert count("")<=p["training"]["prompt_token_budget"],(sid,"Original input exceeds prompt budget",count(""))
   item=dict(sample_id=sid,fold=k,fold_graph_id=graph.release_id,level=level,gate_reasons=reasons,tasks={},input_record_sha256=canonical({key:row[key] for key in ["sample_id","text","audio_path","video_path"]}))
   for task in ["description","ovlabel"]:
    qa=reader.get_qa_pairs(reader.dataset,task,row);item["tasks"][task]=dict(question=qa["question"],levels={})
    for lev in range(1,level+1):
     prepared=bridge.prepare(reader,reader,restricted_graph(sg,lev),qa["question"],row["subtitle"],max_length=2000,max_new_tokens=1200)
     packet=prepared["evidence"];audit=packet["audit"]
     item["tasks"][task]["levels"][str(lev)]=dict(text=packet["text"],graph_tokens=audit["evidence_tokens"],fallback=audit["fallback"],CA_edge_count=audit["CA_edge_count"],CE_edge_count=audit["CE_edge_count"],full_prompt_sha256=canonical(prepared["prompt"]))
     assert audit["evidence_tokens"]<=p["training"]["graph_token_budget"] and audit["full_prompt_tokens"]<=800
   for label in ["description","ovlabel"]:
    for drop in [None,.1,.3]:
     ids,target,prompt,info=make_tokens(reader,row,item,label,p["training"],drop)
     seq=len(ids)+len(target)+2;maxseq=max(maxseq,seq);maxprompt=max(maxprompt,len(ids));assert seq<=p["training"]["certified_actual_max_tokens"]
     for marker,num in [("<ImageHere>",0),("<AudioHere>",1),("<FrameHere>",0),("<FaceHere>",1),("<MultiHere>",1)]:assert prompt.count(marker)==num
     assert len(target)>0;ntests+=1
   if len(examples)<3:examples.append(dict(sample_id=sid,gate_level=level,tasks=item["tasks"]))
   out.write(json.dumps(item,ensure_ascii=False,allow_nan=False)+"\n")
   if (n+1)%100==0:
    atomic_json(fold/"evidence_progress.json",dict(completed=n+1,total=len(rows),max_sequence_tokens=maxseq,levels=dict(counts),updated_at_beijing=now()));print("CACHE",k,n+1,len(rows),flush=True)
 tmp.replace(fold/"evidence.jsonl")
 atomic_json(fold/"evidence_manifest.json",dict(complete=True,fold=k,samples=len(rows),sha256=sha(fold/"evidence.jsonl"),graph_id=graph.release_id,maximum_sequence_tokens=maxseq,maximum_prompt_tokens=maxprompt,cpu_prompt_checks=ntests,levels=dict(counts),original_subtitles_preserved=True,graph_only_oof=True,Student_retrained=False,AE_enabled=False,created_at_beijing=now()))
 atomic_json(fold/"prompt_examples.json",examples)
def process(run,k):
 fold=run/"folds"/str(k);status=fold/"status.json"
 def update(state,**kw):atomic_json(status,dict(state=state,pid=os.getpid(),fold=k,time_beijing=now(),**kw))
 try:
  if (fold/"evidence_manifest.json").exists():return
  update("fitting_G1_graph_oof")
  from . import fold_fit
  fold_fit.ROOT=fold/"v2"
  if not (fold/"v2/work/fit_complete.json").exists():fold_fit.main()
  update("fitting_v21_cue_admission")
  from . import fold_cue_fit
  fold_cue_fit.ROOT=fold/"v21"
  if not (fold/"v21/work/fit_complete.json").exists():fold_cue_fit.main()
  update("building_P4_compact_gated_evidence");evidence(run,k)
  update("complete")
 except BaseException as exc:update("failed",error=repr(exc),traceback=traceback.format_exc());raise
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);ap.add_argument("--init",action="store_true");ap.add_argument("--fold",type=int);a=ap.parse_args();run=Path(a.run)
 if a.init:initialize(run)
 else:process(run,a.fold)
if __name__=="__main__":main()
