from __future__ import annotations
from graph_paths import resolve_path as _graph_resolve_path
import hashlib, json, os, random, tempfile
from graph_paths import Path
import numpy as np
import torch

PROJECT = Path(__file__).resolve().parents[1]
MODALITIES = ("text", "audio", "visual")
STATES = ("positive", "negative", "uncertain", "unobservable", "unlabeled")

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False); f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(_graph_resolve_path(tmp)): os.unlink(_graph_resolve_path(tmp))

def absolute(path):
    p = Path(path)
    return (PROJECT / p).resolve() if not p.is_absolute() else p.resolve()

def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

def rng_state():
    return dict(python=random.getstate(), numpy=np.random.get_state(), torch=torch.get_rng_state(),
                cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None)

def restore_rng(state):
    random.setstate(state["python"]); np.random.set_state(state["numpy"]); torch.set_rng_state(state["torch"].cpu())
    if state["cuda"] is not None and torch.cuda.is_available(): torch.cuda.set_rng_state_all([x.cpu() for x in state["cuda"]])

def code_hash():
    return canonical_hash({p.name: sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))})

def model_assets(directory):
    directory = absolute(directory)
    weights = directory / "model.safetensors"
    if not weights.exists(): weights = directory / "pytorch_model.bin"
    if not weights.exists(): raise FileNotFoundError(f"No local model weights: {directory}")
    names = [weights.name, "config.json", "preprocessor_config.json", "tokenizer_config.json",
             "tokenizer.json", "sentencepiece.bpe.model", "special_tokens_map.json"]
    paths = [directory / n for n in names if (directory / n).is_file()]
    stats = {p.name: [p.stat().st_size, p.stat().st_mtime_ns] for p in paths}
    cache = PROJECT / "cue_student/artifacts/model_fingerprints" / (canonical_hash(str(directory)) + ".json")
    old = json.loads(cache.read_text()) if cache.exists() else {}
    if old.get("stats") == stats:
        hashes = old["hashes"]
    else:
        hashes = {p.name: sha256(p) for p in paths}
        atomic_json(cache, dict(directory=str(directory), stats=stats, hashes=hashes))
    return dict(directory=str(directory), sha256=hashes)

def load_config(path):
    import yaml, math
    source=Path(path).read_text()
    # JSON numbers (including 2e-05) must not pass through YAML 1.1 parsing.
    cfg = json.loads(source) if Path(path).suffix.lower()==".json" else yaml.safe_load(source)
    for key in ("head_lr","encoder_lr","weight_decay","warmup_fraction","clip_grad_norm"):
        if key in cfg:
            value=cfg[key]
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                raise ValueError(key+" must be a finite number; use a JSON number or e.g. 2.0e-5 in YAML")
            if value<0 or (key in ("head_lr","encoder_lr","clip_grad_norm") and value==0):
                raise ValueError(key+" has an invalid nonpositive/negative value")
    if cfg["modality"] not in MODALITIES: raise ValueError("Unknown modality")
    cfg["model_dir"] = str(absolute(cfg["model_dir"]))
    if cfg.get("encoder_train", "frozen") not in ("frozen", "full", "last_layers"): raise ValueError("encoder_train")
    if cfg.get("precision", "float32") not in ("float32", "bf16"): raise ValueError("Use float32 or bf16")
    if cfg.get("pooling", "mean") not in ("mean", "attention", "topk"): raise ValueError("pooling")
    from .temporal import temporal_spec
    temporal_spec(cfg)
    return cfg

def move_batch(batch, device):
    return {k: v.to(device, non_blocking=True) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
