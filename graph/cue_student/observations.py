"""Deterministic input geometry logs, without Teacher states/targets/evidence."""
from graph_paths import Path
import json
from .common import atomic_json,canonical_hash

def describe(batch,index,modality,cfg):
    out=dict(sample_id=batch["sample_ids"][index],modality=modality,format_version=1)
    if modality=="text":
        out.update(max_length=cfg.get("max_length",128),overlap=cfg.get("text_overlap",32),
                   language_present=batch["language_present"][index].detach().cpu().tolist(),
                   token_spans=[{k:v for k,v in span.items() if k!="sample_index"} for span in batch["chunk_spans"] if span["sample_index"]==index])
    elif modality=="audio":
        n=int(batch["audio_lengths"][index])
        out.update(sample_rate=16000,valid_samples=n,covered_seconds=[0,n/16000],temporal_truncation=False)
        if cfg.get("temporal_model","none")=="transformer":
            from .temporal import temporal_spec
            spec=temporal_spec(cfg);stride=spec["audio_feature_stride_samples"]
            count=(n-spec["audio_feature_receptive_field_samples"])//stride+1
            out.update(temporal_architecture=spec,valid_feature_frames=count,
                       feature_step_seconds=stride/16000,
                       first_feature_center_seconds=(spec["audio_feature_receptive_field_samples"]-1)/2/16000,
                       model_feature_time_offsets_seconds=[i*stride/16000 for i in range(count)])
    else:
        out.update(fps=cfg.get("fps",2.),spatial=cfg.get("spatial","letterbox"),
                   actual_frame_pts_seconds=batch["frame_times"][index],includes_first_and_last_decoded_frame=True,temporal_truncation=False)
        if cfg.get("temporal_model","none")=="transformer":
            from .temporal import temporal_spec
            out["temporal_architecture"]=temporal_spec(cfg)
            out["model_frame_time_offsets_seconds"]=[t-batch["frame_times"][index][0] for t in batch["frame_times"][index]]
    return out

def write_observations(batch,directory,modality,cfg):
    directory=Path(directory)
    for i,sid in enumerate(batch["sample_ids"]):
        row=describe(batch,i,modality,cfg)
        path=directory/(canonical_hash(sid)+".json")
        if path.exists():
            if json.loads(path.read_text())!=row: raise ValueError("Input geometry changed within a run: "+sid)
        else: atomic_json(path,row)
