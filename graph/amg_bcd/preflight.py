"""CPU-only preflight: provenance, prompt bounds, gates, shards, barriers."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,collections,copy,json,os,sys
from graph_paths import Path
from .common import *
from .policy import POLICY,gate,format_evidence,make_tokens,make_prompt
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);a=ap.parse_args();run=Path(a.run);p=plan(run)
 for f in (ROOT/"amg_bcd").glob("*.py"):compile(f.read_text(),str(f),"exec")
 require(p["logical_jobs"]==45 and len(p["variants"])==3,"Unexpected task budget")
 records=read(run/"train_records.json");audit=read(run/"human_audit_500.json")
 aids={r["sample_id"] for r in audit};ids={r["sample_id"] for r in records}
 require(len(ids)==30755 and len(aids)==500 and not(ids&aids),"Training/audit membership overlap")
 old=read(SOURCE/"plan.json");require(_graph_hash_matches(run / 'train_records.json', old['inputs']['train_records_sha256'], sha(run / 'train_records.json')),"Changed training records")
 require(_graph_hash_matches(p['base_checkpoint']['path'], p['base_checkpoint']['sha256'], sha(p['base_checkpoint']['path'])),"Original checkpoint changed")
 for d,spec in p["datasets"].items():
  require(_graph_hash_matches(spec['path'], spec['sha256'], sha(spec['path'])) and len(read(spec["path"]))==spec["samples"],"Target input membership changed")
 for name,binding in read(run/"model_assets_manifest.json")["assets"].items():
  st=Path(name).stat();require(st.st_size==binding["bytes"] and st.st_mtime_ns==binding["mtime_ns"],"Model asset changed")
 fake=dict(query_cues=[],emotion_candidates=[],appraisal_dimensions=[],explanation_paths=[],fallback=dict(required=True))
 require(gate(fake,"C")[0]==0,"Empty evidence did not abstain")
 fake["query_cues"]=[dict(cue_id="AUD_VOICE_TENSE",score=.9)]
 require(gate(fake,"C")[0]==1,"Single cue should not yield full graph")
 require(gate(fake,"C",.1)[0]==0,"Training dropout missing")
 fake=dict(query_cues=[dict(cue_id="AUD_VOICE_TENSE",score=.9),dict(cue_id="VIS_BROWS_FURROWED",score=.9)],
  emotion_candidates=[dict(emotion_id="E1",canonical_name="anger",association_score=.5,query_coverage=1),dict(emotion_id="E2",canonical_name="worry",association_score=.2,query_coverage=1)],
  appraisal_dimensions=[dict(dimension_id="APP_CERTAINTY",display_candidates=[dict(state_id="APP_CERTAIN")])],
  explanation_paths=[dict(cue_id="AUD_VOICE_TENSE",emotion_id="E1"),dict(cue_id="VIS_BROWS_FURROWED",emotion_id="E1")],fallback=dict(required=False))
 require(gate(fake,"C")[0]==3,"Supported evidence did not pass")
 changed=copy.deepcopy(fake);changed["answer"]="neutral";changed["ground_truth"]="happy"
 require(gate(changed,"C")==gate(fake,"C"),"Gate consumes answers or labels")
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"))
 from my_affectgpt.models.tokenizer import load_tokenizer_from_LLM
 from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
 tokenizer=load_tokenizer_from_LLM("Qwen25")
 class Reader(BaseDataset):pass
 reader=Reader.__new__(Reader);reader.tokenizer=tokenizer;reader.dataset="MERCaptionPlus";reader.face_or_frame="multiface_audio_face_text"
 cfg=read(run/"original_config.json")["model"]
 for key in ["num_audio_query_token","num_video_query_token","num_multi_query_token","num_image_query_token"]:setattr(reader,key,cfg[key])
 for attr,marker in [("IMAGE_PATCH_TOKEN_ID","<ImageHere>"),("AUDIO_PATCH_TOKEN_ID","<AudioHere>"),("FRAME_PATCH_TOKEN_ID","<FrameHere>"),("FACE_PATCH_TOKEN_ID","<FaceHere>"),("MULTI_PATCH_TOKEN_ID","<MultiHere>")]:setattr(reader,attr,tokenizer.get_vocab()[marker])
 selected={r["sample_id"]:r for r in records[::max(1,len(records)//64)]}
 for r in sorted(records,key=lambda r:len(r["description"]),reverse=True)[:32]:selected[r["sample_id"]]=r
 for r in sorted(records,key=lambda r:len(r["subtitle"]),reverse=True)[:16]:selected[r["sample_id"]]=r
 maximum=0;levels=collections.Counter();checked=0
 for r in selected.values():
  cache=read(source_cache(p,r["sample_id"]));require(cache["cache_id"]==canonical({k:v for k,v in cache.items() if k!="cache_id"}),"Source cache corrupted")
  for variant in ["B","C","D"]:
   for task in ["description","ovlabel"]:
    prompt,target,text,info=make_tokens(reader,r,cache["evidence"],task,p["training"],variant)
    n=len(prompt)+len(target)+2;maximum=max(maximum,n);levels[str(info["evidence_level"])]+=1
    require(n<=1398 and info["graph_tokens"]<=512,"Actual no-GC context envelope exceeded")
    require(len(target)>0,"No supervised answer")
    for marker,count in zip(["<ImageHere>","<AudioHere>","<FrameHere>","<FaceHere>","<MultiHere>"],[0,1,0,1,1]):require(text.count(marker)==count,"Multimodal marker count changed")
    checked+=1
 # Freeze shared work shards before any GPU process starts.
 (run/"shards").mkdir(exist_ok=False);total=0
 for f in sorted((run/"jobs").glob("*.json")):
  job=read(f);job["shards"]=[]
  for lo in range(0,job["samples"],64):
   name=job["job_id"]+f"_{lo:04d}.json";job["shards"].append(name);total+=1
   atomic_json(run/"shards"/name,dict(job_id=job["job_id"],variant=job["variant"],epoch=job["epoch"],dataset=job["dataset"],dataset_samples=job["samples"],start=lo,stop=min(lo+64,job["samples"]),samples=min(64,job["samples"]-lo),state="pending",attempts=0))
  atomic_json(f,job)
 oldlock=read(OLD_INFER/"evaluation_all_20261023_175630/evaluation_lock.json");resources=dict(files=oldlock["files_sha256"],original_sampling_preserved=True,source_evaluation_lock=oldlock["lock_id"])
 for path,digest in resources["files"].items():require(_graph_hash_matches(path, digest, sha(path)),"Evaluation resource changed")
 resources["lock_id"]=canonical(resources);atomic_json(run/"evaluation_resources.json",resources)
 # Bind the new package and reused source modules, leaving all historical code untouched.
 paths=list((ROOT/"amg_bcd").glob("*.py"))
 for folder in ["amg_finetune_nogc","amg_runtime","amg_graph","amg_inference"]:paths+=list((ROOT/folder).glob("*.py"))
 manifest=dict(files={str(f.relative_to(ROOT)):sha(f) for f in paths},created_at_beijing=now())
 atomic_json(run/"code_manifest.json",manifest)
 for variant in p["variants"]:(run/(variant+"_plan")/"code_manifest.json").symlink_to(run/"code_manifest.json")
 report=dict(passed=True,cpu_only=True,gpu_model_calls=0,training_records=30755,audit_records=500,independent_validation=False,source_examples_checked=len(selected),prompt_tasks_checked=checked,maximum_checked_sequence_tokens=maximum,certified_runtime_limit=1398,evidence_levels=dict(levels),logical_inference_jobs=45,inference_shards=total,total_predictions=21000,gate_parameters_frozen=POLICY,evaluation_after_all_inference=True,completed_at_beijing=now())
 atomic_json(run/"cpu_preflight.json",report);print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
