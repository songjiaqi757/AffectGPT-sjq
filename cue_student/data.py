"""Raw media only; no dependency on deleted API media copies or Teacher explanations."""
from __future__ import annotations
import json, math, random
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from .common import MODALITIES, absolute, canonical_hash, sha256
from .holdout import load_fixed_holdout,assert_holdout_separation
from .temporal import relative_frame_times
from .eligibility import POLICY,assert_eligible_members

class Release:
    def __init__(self, path):
        self.path = absolute(path)
        self.manifest = json.loads((self.path/"manifest.json").read_text())
        content = {k:v for k,v in self.manifest.items() if k != "release_id"}
        if canonical_hash(content) != self.manifest["release_id"]: raise ValueError("Manifest hash mismatch")
        for name, digest in self.manifest["files"].items():
            if sha256(self.path/name) != digest: raise ValueError("Release file changed: " + name)
        self.rows = json.loads((self.path/"members.json").read_text())
        if self.manifest.get("sample_eligibility") != POLICY or "eligibility.json" not in self.manifest["files"]:
            raise ValueError("Release must enforce whole-sample failed-annotation exclusion")
        self.eligibility=json.loads((self.path/"eligibility.json").read_text())
        assert_eligible_members([r["sample_id"] for r in self.rows],self.eligibility)
        self.ontology = json.loads((self.path/"ontology.json").read_text())
        fixed=load_fixed_holdout()
        self.fixed_holdout_id=fixed["holdout_id"] if fixed else None
        if fixed is not None:assert_eligible_members(fixed["sample_ids"],self.eligibility)
        declared=self.manifest.get("fixed_holdout_id")
        if declared is not None and declared!=self.fixed_holdout_id: raise ValueError("Fixed holdout version mismatch")
        assert_holdout_separation(self.rows,fixed)
        with np.load(self.path/"labels.npz", allow_pickle=False) as z:
            self.targets, self.mask, self.states = z["targets"], z["mask"].astype(bool), z["states"]
        if self.targets.shape != (len(self.rows),42): raise ValueError("Release dimensions")
        seen = {}
        for row in self.rows:
            role = "reserved_audit" if row["role"] in ("gold_audit","audit_group_excluded") else row["role"]
            if row["group_id"] in seen and seen[row["group_id"]] != role: raise ValueError("Cross-role group leakage")
            seen[row["group_id"]] = role
        self.offsets = {}; k = 0
        for m in MODALITIES:
            n = len(self.ontology["cue_ids"][m]); self.offsets[m] = slice(k,k+n); k += n

class CueDataset(torch.utils.data.Dataset):
    def __init__(self, release, modality, role, training=False):
        if training and role!="pseudo_train": raise ValueError("Only pseudo_train may supply optimization data")
        self.release = release; self.modality = modality; self.sl = release.offsets[modality]
        self.indices = [i for i,r in enumerate(release.rows) if r["role"] == role and
                        (not training or release.mask[i,self.sl].any())]
        if not self.indices: raise ValueError(f"No {modality} samples for {role}")
        self.targets = release.targets[self.indices,self.sl]
        self.label_mask = release.mask[self.indices,self.sl]
        self.cue_ids = release.ontology["cue_ids"][modality]
        self.costs = [max(1, (release.rows[i].get(modality+"_duration", 1))) for i in self.indices]
    def __len__(self): return len(self.indices)
    def __getitem__(self, index):
        i = self.indices[index]; row = dict(self.release.rows[i])
        asset = row.get("media_assets", {}).get(self.modality)
        if asset:
            st = Path(asset["path"]).stat()
            if st.st_size != asset["bytes"] or st.st_mtime_ns != asset["mtime_ns"]:
                raise ValueError("Media changed since release: " + asset["path"])
        row["targets"] = self.release.targets[i,self.sl].copy()
        row["label_mask"] = self.release.mask[i,self.sl].copy()
        return row

def epoch_batches(dataset, batch_size, epoch=0, seed=42, shuffle=True, max_units=None):
    order = list(range(len(dataset))); rng = random.Random(seed+epoch)
    if shuffle: rng.shuffle(order)
    batches = []
    for k in range(0,len(order),128):
        block = sorted(order[k:k+128], key=lambda i:dataset.costs[i])
        current=[]; units=0.
        for i in block:
            cost=dataset.costs[i]
            if current and (len(current)>=batch_size or (max_units and units+cost>max_units)):
                batches.append(current); current=[]; units=0.
            current.append(i); units+=cost
        if current: batches.append(current)
    if shuffle: rng.shuffle(batches)
    return batches

def labels(items):
    return dict(targets=torch.tensor(np.stack([x["targets"] for x in items]),dtype=torch.float32),
                label_mask=torch.tensor(np.stack([x["label_mask"] for x in items]),dtype=torch.bool),
                sample_ids=[x["sample_id"] for x in items])

class TextCollator:
    def __init__(self, model_dir, max_length=128, overlap=32):
        from transformers import AutoTokenizer
        self.tokenizer=AutoTokenizer.from_pretrained(model_dir,local_files_only=True)
        self.tokenizer.padding_side="right"; self.max_length=max_length; self.overlap=overlap
        if max_length>512 or max_length<=overlap+2: raise ValueError("Invalid text chunk size/overlap")
    def __call__(self,items):
        tok=self.tokenizer; chunks=[]; weights=[]; owners=[]; present=[]; spans=[]
        capacity=self.max_length-tok.num_special_tokens_to_add(pair=False)
        for b,item in enumerate(items):
            flags=[]
            for lang_idx,lang in enumerate(("chinese","english")):
                text=item.get("text",{}).get(lang,"") or ""; flags.append(bool(text.strip()))
                ids=tok.encode(text,add_special_tokens=False)
                starts=list(range(0,max(len(ids)-capacity,0)+1,capacity-self.overlap))
                if starts[-1]+capacity<len(ids): starts.append(starts[-1]+capacity-self.overlap)
                coverage=np.zeros(len(ids),dtype=np.float32)
                for st in starts: coverage[st:min(st+capacity,len(ids))]+=1
                for st in starts:
                    piece=ids[st:st+capacity]; seq=tok.build_inputs_with_special_tokens(piece)
                    special=[1]+[0]*len(piece)+[1]
                    if seq != [tok.bos_token_id]+piece+[tok.eos_token_id]: raise ValueError("Expected XLM-R single-sequence layout")
                    w=[]; j=st
                    for flag in special:
                        w.append(0. if flag or not flags[-1] else float(1/coverage[j]))
                        if not flag: j+=1
                    chunks.append(dict(input_ids=seq,attention_mask=[1]*len(seq)))
                    weights.append(w); owners.append(b*2+lang_idx)
                    spans.append(dict(sample_index=b,language=lang,token_start=st,token_end=min(st+capacity,len(ids))))
            if not any(flags) and np.asarray(item["label_mask"]).any(): raise ValueError("Both text fields absent in a supervised sample")
            present.append(flags)
        batch=tok.pad(chunks,padding=True,return_tensors="pt")
        pool=torch.zeros_like(batch["attention_mask"],dtype=torch.float32)
        for i,w in enumerate(weights): pool[i,:len(w)]=torch.tensor(w)
        return dict(**labels(items),input_ids=batch["input_ids"],attention_mask=batch["attention_mask"],
                    pool_weights=pool,owners=torch.tensor(owners),language_present=torch.tensor(present,dtype=torch.float32),chunk_spans=spans)

def read_audio(path):
    import soundfile as sf
    from scipy.signal import resample_poly
    a,sr=sf.read(path,dtype="float32",always_2d=True)
    a=a.mean(axis=1)
    if sr!=16000:
        divisor=math.gcd(sr,16000); a=resample_poly(a,16000//divisor,sr//divisor).astype(np.float32)
    if len(a)<400: raise ValueError("Audio shorter than HuBERT convolution receptive field; not a negative cue")
    if not np.isfinite(a).all(): raise ValueError("Non-finite audio")
    return a

class AudioCollator:
    def __init__(self,model_dir):
        from transformers import Wav2Vec2FeatureExtractor
        self.processor=Wav2Vec2FeatureExtractor.from_pretrained(model_dir,local_files_only=True)
    def __call__(self,items):
        audio=[read_audio(x["audio_path"]) for x in items]
        processed=self.processor(audio,sampling_rate=16000,padding=True,return_attention_mask=True,return_tensors="pt")
        return dict(**labels(items),input_values=processed["input_values"],attention_mask=processed["attention_mask"],
                    audio_lengths=torch.tensor([len(x) for x in audio]))

def sample_video(path,fps=2.,size=224,spatial="letterbox",decode_threads=0):
    import av
    if fps<=0 or spatial not in ("letterbox","center_crop"): raise ValueError("Visual preprocessing")
    if type(decode_threads) is not int or decode_threads<0: raise ValueError("decode_threads")
    frames=[]; times=[]; origin=None; next_target=0.; last=None; last_t=None
    def convert(frame):
        image=frame.to_image().convert("RGB")
        if spatial=="letterbox":
            w,h=image.size; scale=min(size/w,size/h)
            scaled=image.resize((max(1,round(w*scale)),max(1,round(h*scale))),Image.Resampling.BICUBIC)
            result=Image.new("RGB",(size,size),(0,0,0)); result.paste(scaled,((size-scaled.width)//2,(size-scaled.height)//2))
            return result
        return image
    with av.open(str(path)) as container:
        stream=container.streams.video[0]
        stream.thread_count=decode_threads
        for frame in container.decode(stream):
            if frame.pts is None: raise ValueError("Missing actual frame PTS")
            t=float(frame.pts*frame.time_base)
            if origin is None: origin=t
            relative=t-origin
            if last_t is not None and t<=last_t: raise ValueError("Non-increasing frame PTS")
            if not times or relative+1e-8>=next_target:
                frames.append(convert(frame)); times.append(t)
                next_target=(math.floor(relative*fps+1e-8)+1)/fps
            last=frame; last_t=t
        if last is not None and (not times or abs(times[-1]-last_t)>1e-8):
            frames.append(convert(last)); times.append(last_t)
    if not frames: raise ValueError("No video frames")
    return frames,times

class VisualCollator:
    def __init__(self,model_dir,fps=2.,spatial="letterbox",decode_threads=0):
        from transformers import CLIPImageProcessor
        self.processor=CLIPImageProcessor.from_pretrained(model_dir,local_files_only=True)
        self.size=self.processor.crop_size["height"] if isinstance(self.processor.crop_size,dict) else self.processor.crop_size
        self.fps=fps; self.spatial=spatial; self.decode_threads=decode_threads
    def __call__(self,items):
        pixels=[]; owners=[]; timestamps=[]
        for i,row in enumerate(items):
            frames,pts=sample_video(row["video_path"],self.fps,self.size,self.spatial,self.decode_threads)
            kwargs=dict(do_resize=False,do_center_crop=False) if self.spatial=="letterbox" else {}
            pixels.append(self.processor(images=frames,return_tensors="pt",**kwargs)["pixel_values"])
            owners.extend([i]*len(frames)); timestamps.append(pts)
        return dict(**labels(items),pixel_values=torch.cat(pixels),frame_owners=torch.tensor(owners),
                    frame_times=timestamps,frame_time_offsets=relative_frame_times(timestamps),batch_size=len(items))

def make_collator(cfg):
    m=cfg["modality"]
    if m=="text": return TextCollator(cfg["model_dir"],cfg.get("max_length",128),cfg.get("text_overlap",32))
    if m=="audio": return AudioCollator(cfg["model_dir"])
    return VisualCollator(cfg["model_dir"],cfg.get("fps",2.),cfg.get("spatial","letterbox"),cfg.get("decode_threads",0))
