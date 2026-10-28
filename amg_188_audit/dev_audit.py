
"""Prepare official-val candidates and exact-media overlap evidence; never approve independence automatically."""
import argparse,csv,runpy,re,collections
from .common import *
def group(d,n):
 if d in ["CMUMOSI","CMUMOSEI"]:return n.rsplit("_",1)[0]
 if d=="MELD":return n.rsplit("_utt",1)[0]
 return n.rsplit("_",1)[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);a=ap.parse_args();run=Path(a.run);p=plan(run)
 os.chdir(ROOT/"AffectGPT");cfg=runpy.run_path("config.py");dev=read(run/"dev_inventory.json");source=read(Path(p["source_run"])/"train_records.json")
 trainhash={x.get("media_assets",{}).get("audio",{}).get("sha256") for x in source};trainhash.discard(None)
 targethash=set();targetgroups={};corpora={}
 for d,di in p["datasets"].items():
  rows=read(di["path"]);targetgroups[d]={group(d,x["name"]) for x in rows}
  for row in rows:
   c=read(Path(p["target_cache"])/(sid_key(row["sample_id"])+".json"))
   h=c.get("cue",{}).get("input_fingerprints",{}).get("audio",{}).get("sha256")
   if h:targethash.add(h)
  print("TARGET_HASHES",d,len(targethash),flush=True)
 import numpy as np
 candidates=[];labels={};summary={}
 for d,inventory in dev.items():
  with Path(cfg["PATH_TO_TRANSCRIPTIONS"][d]).open(newline="") as f:texts={x["name"]:x for x in csv.DictReader(f)}
  corpus=np.load(cfg["PATH_TO_LABEL"][d],allow_pickle=True)["val_corpus"].item();counts=collections.Counter()
  for n in inventory["candidate_names"]:
   audio=(Path(cfg["PATH_TO_RAW_AUDIO"][d])/(n+".wav")).resolve();face=(Path(cfg["PATH_TO_RAW_FACE"][d])/(n+".npy")).resolve()
   if not face.exists():face=(Path(cfg["PATH_TO_RAW_FACE"][d])/n/(n+".npy")).resolve()
   vr=Path(cfg["PATH_TO_RAW_VIDEO"][d]);video=next((vr/(n+e) for e in [".mp4",".avi",".mkv"] if (vr/(n+e)).exists()),vr/(n+".mp4")).resolve()
   x=texts.get(n,{});ch=x.get("chinese","");en=x.get("english","");h=sha(audio) if audio.exists() else None
   flags=dict(missing_audio=not audio.exists(),missing_face=not face.exists(),missing_video=not video.exists(),missing_transcript=n not in texts,empty_text=not(ch.strip() or en.strip()),translation_refusal=bool(re.search("无法提供翻译|无法翻译|不适当的言辞|as an ai|unable to translate",ch+" "+en,re.I)),exact_source_audio_overlap=h in trainhash if h else False,exact_test_audio_overlap=h in targethash if h else False,test_video_group_overlap=group(d,n) in targetgroups[d])
   counts.update(k for k,v in flags.items() if v)
   sid=d+"::"+n;candidates.append(dict(sample_id=sid,name=n,dataset=d,split="official_val_candidate",group_id=group(d,n),subtitle=en or ch,text=dict(chinese=ch,english=en),audio_path=str(audio),face_path=str(face),video_path=str(video),audio_sha256=h,quality_flags=flags,independence_status="not_admitted_base_and_cue_training_exposure_unknown"))
   if d=="MELD":labels[sid]=["anger","joy","sadness","neutral","disgust","fear","surprise"][int(corpus[n]["emo"])]
   else:labels[sid]=float(corpus[n]["val"])
  summary[d]=dict(candidate_count=inventory["candidate_count"],flags=dict(counts),admitted=False)
  print("DEV",d,summary[d],flush=True)
 atomic_json(run/"dev_candidates.json",candidates);atomic_json(run/"dev_candidate_labels.json",labels)
 review=[]
 for d in dev:
  eligible=[x for x in candidates if x["dataset"]==d and not any(x["quality_flags"][k] for k in ["missing_audio","missing_face","missing_video","missing_transcript","translation_refusal","exact_source_audio_overlap","exact_test_audio_overlap"])]
  eligible.sort(key=lambda x:canonical("blind-review-v1::"+x["sample_id"]))
  review.extend(eligible[:40])
 atomic_json(run/"dev_review_queue.json",dict(schema="blind_semantic_evidence_review_v1",samples=review,reference_labels_visible=False,teacher_predictions_visible=False,fields=["target_speaker","emotion_holder","event_time","evaluation_target","negation_scope","contrast_or_only_scope","speech_act","overall_stance","current_emotion","evidence_phrase_or_time","observable_or_abstain"],instructions="Review current media and original text first; record ambiguity and abstain when not observable. No target-test examples or predicted answers supplied. This queue does not by itself certify independence."))
 atomic_json(run/"dev_overlap_audit.json",dict(summary=summary,candidates=len(candidates),source_audio_hashes=len(trainhash),test_audio_hashes=len(targethash),admitted=False,reason="Exact overlap checks do not prove base/Cue pretraining exclusion or speaker/source independence; no tuning/training permitted from this inventory yet.",checked_at_beijing=now()))
if __name__=="__main__":main()
