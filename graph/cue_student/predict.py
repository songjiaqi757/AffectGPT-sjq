"""JSON input -> cue scores with explicit unavailable status, without Teacher labels."""
from graph_paths import resolve_path as _graph_resolve_path
import argparse,json
from graph_paths import Path
import numpy as np
import torch
from .common import absolute,atomic_json,model_assets,move_batch
from .data import make_collator
from .models import CueModel
from .train import autocast
from .observations import describe
from .temporal import temporal_spec

@torch.inference_mode()
def predict(checkpoint,records,device="cuda:0"):
    ckpt=torch.load(_graph_resolve_path(absolute(checkpoint)), map_location='cpu', weights_only=False)
    cfg=ckpt["config"]; device=torch.device(device)
    if model_assets(cfg["model_dir"])!=ckpt["assets"]: raise ValueError("Encoder assets differ from checkpoint")
    model=CueModel(cfg).to(device); model.restore_weights(ckpt["model"]); model.eval()
    collator=make_collator(cfg); m=cfg["modality"]; output=[]
    for i,record in enumerate(records):
        sid=record.get("sample_id",str(i)); base=dict(sample_id=sid,modality=m,cue_ids=ckpt["cue_ids"],checkpoint=str(absolute(checkpoint)),
            thresholds=[.5]*len(ckpt["cue_ids"]),threshold_status="uncalibrated_0.5",temporal_architecture=temporal_spec(cfg),encoder_assets=ckpt["assets"],checkpoint_scope=ckpt.get("scope","unspecified"),
            preprocessing={k:cfg[k] for k in ("max_length","text_overlap","fps","spatial") if k in cfg})
        row=dict(record,sample_id=sid,targets=np.zeros(len(ckpt["cue_ids"]),np.float32),label_mask=np.zeros(len(ckpt["cue_ids"]),bool))
        try:
            if m=="text" and not any(str(row.get("text",{}).get(lang,"") or "").strip() for lang in ("chinese","english")):
                raise ValueError("Both text fields absent")
            if m!="text":
                key="audio_path" if m=="audio" else "video_path"
                if not row.get(key) or not Path(row[key]).is_file(): raise FileNotFoundError("Media unavailable")
            batch=move_batch(collator([row]),device)
            with autocast(cfg,device): logits=model(batch)
            if not torch.isfinite(logits).all(): raise FloatingPointError("Non-finite prediction")
            scores=logits.float().sigmoid()[0].cpu().tolist()
            output.append(dict(**base,input_valid=True,scores=scores,input_observation=describe(batch,0,m,cfg),selected_positive=[c for c,s in zip(ckpt["cue_ids"],scores) if s>=.5],
                               trained_two_class_support=[p>0 and n>0 for p,n in zip(ckpt["train_positive"],ckpt["train_negative"])]))
        except (ValueError,FileNotFoundError,OSError) as error:
            output.append(dict(**base,input_valid=False,scores=None,selected_positive=[],error=str(error)))
    return output

def main():
    p=argparse.ArgumentParser(); p.add_argument("--checkpoint",required=True); p.add_argument("--input",required=True)
    p.add_argument("--output",required=True); p.add_argument("--device",default="cuda:0"); args=p.parse_args()
    records=json.loads(absolute(args.input).read_text())
    if isinstance(records,dict): records=[records]
    atomic_json(absolute(args.output),predict(args.checkpoint,records,args.device))
if __name__=="__main__": main()
