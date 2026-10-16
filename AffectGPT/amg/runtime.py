"""Explicit model/data loading shared by the new AMG commands."""
from pathlib import Path
import hashlib, json, os, random
import numpy as np
import torch

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT / "train_configs/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz.yaml"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def load_config(path=DEFAULT_CONFIG, *, face_or_frame=None):
    from omegaconf import OmegaConf
    path = Path(path).resolve()
    os.chdir(PROJECT)
    cfg = OmegaConf.load(path)
    if face_or_frame:
        cfg.datasets.mercaptionplus.face_or_frame = face_or_frame
    return cfg

def load_base(cfg, checkpoint, device):
    # Registration imports load code, not additional model instances.
    import my_affectgpt.models
    from my_affectgpt.models.affectgpt import AffectGPT
    from omegaconf import OmegaConf
    mc = OmegaConf.create(OmegaConf.to_container(cfg.model, resolve=True))
    for k in ("ckpt", "ckpt_2", "ckpt_3"):
        mc[k] = ""
    model = AffectGPT.from_config(mc)
    raw = torch.load(checkpoint, map_location="cpu", weights_only=True, mmap=True)
    state = dict(raw["model"] if "model" in raw else raw)
    renames = {}
    for suffix in ("weight", "bias"):
        old, new = f"video_llama_proj.{suffix}", f"affectgpt_proj.{suffix}"
        if old in state:
            if new in state:
                raise ValueError(f"Ambiguous legacy/new checkpoint keys: {old}, {new}")
            state[new] = state.pop(old)
            renames[old] = new
    required = {name for name, p in model.named_parameters() if p.requires_grad}
    own = model.state_dict()
    missing_trained = required - set(state)
    extra = set(state) - set(own)
    mismatched = [name for name, value in state.items()
                  if name in own and value.shape != own[name].shape]
    if missing_trained or extra or mismatched:
        raise ValueError(f"Checkpoint coverage failed missing_trainable={sorted(missing_trained)} "
                         f"unexpected={sorted(extra)} shape={mismatched}")
    info = model.load_state_dict(state, strict=False)
    print(json.dumps({"checkpoint": str(Path(checkpoint).resolve()), "legacy_renames": renames,
        "restored_trainable_count": len(required), "frozen_missing_count": len(info.missing_keys)}), flush=True)
    del raw, state
    model = model.to(device)
    # Original AV projections emit float32 on CPU (no autocast). Keep CPU
    # Qwen in the same dtype; CUDA keeps the original FP16/autocast path.
    if torch.device(device).type == "cpu":
        model = model.float()
    return model

def build_dataset(cfg, manifest_path=None, *, evaluation=False, memory_tokens=None):
    import my_affectgpt.processors
    from my_affectgpt.common.registry import registry
    from amg.data import AMGTrainingDataset
    pc = cfg.inference if evaluation else cfg.model
    def processor(field):
        item = pc.get(field)
        if item is None:
            from my_affectgpt.processors.base_processor import BaseProcessor
            return BaseProcessor()
        return registry.get_processor_class(item.train.name).from_config(item.train)
    return AMGTrainingDataset(
        vis_processor=processor("vis_processor"),
        txt_processor=processor("text_processor"),
        img_processor=processor("img_processor"),
        dataset_cfg=cfg.datasets.mercaptionplus,
        model_cfg=cfg.model, manifest_path=manifest_path, memory_tokens=memory_tokens)

def move_batch(batch, device):
    return {k: v.to(device, non_blocking=True) if torch.is_tensor(v) else v
            for k, v in batch.items()}

def validate_bank_metadata(path, cfg, *, allow_partial=False):
    """Verify the bank bytes and AV sampling space before loading large models."""
    path = Path(path).resolve()
    sidecar = Path(str(path) + ".json")
    with sidecar.open() as f:
        meta = json.load(f)
    expected = {
        "schema": "amg-m0-bank-v1",
        "face_or_frame": str(cfg.datasets.mercaptionplus.face_or_frame),
        "num_frames": int(cfg.model.vis_processor.train.n_frms),
        "visual_encoder": str(cfg.model.visual_encoder),
        "acoustic_encoder": str(cfg.model.acoustic_encoder),
    }
    for key, value in expected.items():
        if meta.get(key) != value:
            raise ValueError(f"Memory metadata {key}: expected {value!r}, got {meta.get(key)!r}")
    if not isinstance(meta.get("records"), int) or meta["records"] <= 0:
        raise ValueError("Memory metadata has invalid record count")
    if not meta.get("complete") and not allow_partial:
        raise ValueError("Partial smoke-test Memory cannot be used for a production run")
    if meta.get("complete") and meta["records"] != meta.get("total_manifest_records"):
        raise ValueError("Complete Memory has inconsistent record counts")
    if sha256_file(path) != meta.get("bank_sha256"):
        raise ValueError("Memory bank SHA256 mismatch")
    manifest = Path(meta["manifest_path"])
    if not manifest.is_file() or sha256_file(manifest) != meta.get("manifest_sha256"):
        raise ValueError("Memory source manifest is missing or changed")
    artifacts = meta.get("encoder_artifacts", {})
    if artifacts:
        import config
        expected_paths = {"visual": config.PATH_TO_VISUAL[str(cfg.model.visual_encoder)],
                          "audio": config.PATH_TO_AUDIO[str(cfg.model.acoustic_encoder)]}
        for modality, item in artifacts.items():
            directory = Path(item["path"]).resolve()
            if modality not in expected_paths or directory != Path(expected_paths[modality]).resolve():
                raise ValueError(f"Memory encoder path changed: {modality}")
            for relative, info in item["files"].items():
                artifact = (directory / relative).resolve()
                if directory not in artifact.parents or not artifact.is_file():
                    raise ValueError(f"Missing encoder artifact: {artifact}")
                if artifact.stat().st_size != info["bytes"] or sha256_file(artifact) != info["sha256"]:
                    raise ValueError(f"Memory encoder artifact changed: {artifact}")
    return meta

def atomic_torch_save(payload, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    torch.save(payload, temp)
    os.replace(temp, path)

def media_sample(dataset, record):
    """No training answer tokenization, replacement, or hidden skipping for bank extraction."""
    sample = {"name": record["name"]}
    paths = {}
    for kind in ("video", "audio", "face", "image"):
        fn = getattr(dataset, f"_get_{kind}_path", None)
        paths[kind] = fn(sample) if fn else None
    return dataset.read_frame_face_audio_text(paths["video"], paths["face"], paths["audio"], paths["image"])

def load_records(path):
    with open(path) as f:
        rows = [json.loads(l) for l in f if l.strip()]
    if not rows:
        raise ValueError("Empty manifest")
    if len({r["name"] for r in rows}) != len(rows):
        raise ValueError("Duplicate clip IDs in manifest")
    return rows

def checkpoint_payload(model, optimizer, *, step, config):
    return {"schema": "amg-m0-train-v1", "step": step, "model": model.trainable_state(),
            "optimizer": optimizer.state_dict(), "config": config}
