from graph_paths import resolve_path as _graph_resolve_path
import argparse,json
import numpy as np
import torch
from .common import absolute,atomic_json,model_assets
from .data import Release,CueDataset,make_collator
from .models import CueModel
from .train import evaluate
from .objectives import group_bootstrap

def main():
    p=argparse.ArgumentParser(); p.add_argument("--checkpoint",required=True); p.add_argument("--release",required=True)
    p.add_argument("--output",required=True); p.add_argument("--device",default="cuda:0"); p.add_argument("--bootstrap",type=int,default=0)
    args=p.parse_args(); c=torch.load(_graph_resolve_path(absolute(args.checkpoint)), map_location='cpu', weights_only=False)
    release=Release(args.release)
    if c["release_id"]!=release.manifest["release_id"]: raise ValueError("Checkpoint release mismatch")
    if model_assets(c["config"]["model_dir"])!=c["assets"]: raise ValueError("Encoder assets mismatch")
    ds=CueDataset(release,c["config"]["modality"],"pseudo_validation")
    model=CueModel(c["config"]).to(args.device); model.restore_weights(c["model"])
    metrics,pred=evaluate(model,ds,make_collator(c["config"]),c["config"],torch.device(args.device))
    if args.bootstrap:
        groups={r["sample_id"]:r["group_id"] for r in release.rows}
        metrics["bootstrap"]=group_bootstrap(pred["targets"],pred["scores"],pred["mask"],[groups[s] for s in pred["sample_ids"]],ds.cue_ids,args.bootstrap)
    atomic_json(absolute(args.output),metrics)
    print(json.dumps(dict(samples=metrics["samples"],macro_ap=metrics["macro_ap"],masked_bce=metrics["masked_bce"])))
if __name__=="__main__": main()
