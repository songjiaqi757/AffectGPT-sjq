"""Build frozen AV M0 Memory without instantiating Qwen or AffectGPT.

Each requested manifest row is read exactly once. A failed read/extraction
aborts the run; there is no hidden replacement, skipping, or partial full bank.
Example: python -m amg.build_memory --manifest amg/artifacts/manifests/fit.jsonl
         --output amg/artifacts/fit-face.pt --device cpu
"""
from __future__ import annotations

import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Callable

import torch
from torch import nn

from .manifest import read_manifest
from .memory import MemoryBank, VISUAL_DIM, AUDIO_DIM
from .runtime import DEFAULT_CONFIG, PROJECT, load_config, media_sample, sha256_file

SCHEMA = "amg-m0-bank-v1"


def encoder_artifacts(path):
    """Hash local encoder/processor artifacts, including the actual weight files."""
    root = Path(path).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Local encoder directory missing: {root}")
    files = {}
    for item in sorted(root.iterdir()):
        if item.is_file() and item.suffix in {".bin", ".safetensors", ".json", ".txt", ".model"}:
            files[item.name] = {"bytes": item.stat().st_size, "sha256": sha256_file(item)}
    if not files:
        raise ValueError(f"No encoder artifacts found in {root}")
    return {"path": str(root), "files": files}


def load_media_reader(cfg):
    """Shared original media reads and evaluation transforms, no target/tokenizer."""
    import config
    import my_affectgpt.processors
    from my_affectgpt.common.registry import registry
    from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
    from my_affectgpt.datasets.datasets.mercaptionplus_dataset import MERCaptionPlus_Dataset

    pc = cfg.inference if cfg.get("inference") is not None else cfg.model
    processors = {}
    for field in ("vis_processor", "img_processor"):
        item = pc.get(field)
        if item is None:
            from my_affectgpt.processors.base_processor import BaseProcessor
            processors[field] = BaseProcessor()
        else:
            # Reject stochastic augmentation; a bank must use a fixed eval chain.
            if "train" in item.train.name:
                raise ValueError(f"Bank requires an eval processor, got {item.train.name}")
            processors[field] = registry.get_processor_class(item.train.name).from_config(item.train)

    class BankMediaReader(MERCaptionPlus_Dataset):
        def __init__(self):
            BaseDataset.__init__(
                self, vis_processor=processors["vis_processor"],
                img_processor=processors["img_processor"], model_cfg=None, dataset_cfg=None,
                vis_root=config.PATH_TO_RAW_VIDEO["MERCaptionPlus"],
                wav_root=config.PATH_TO_RAW_AUDIO["MERCaptionPlus"],
                face_root=config.PATH_TO_RAW_FACE["MERCaptionPlus"],
            )
            self.face_or_frame = cfg.datasets.mercaptionplus.face_or_frame
            self.needed_data = self.get_needed_data(self.face_or_frame)
            self.n_frms = int(cfg.model.vis_processor.train.n_frms)
            if not self.needed_data:
                raise ValueError("M0 Memory requires at least one audio/visual modality")

    return BankMediaReader()


class FrozenAVExtractor(nn.Module):
    def __init__(self, visual_encoder, acoustic_encoder, needed_data):
        super().__init__()
        self.visual_encoder = visual_encoder.requires_grad_(False).eval()
        self.acoustic_encoder = acoustic_encoder.requires_grad_(False).eval()
        self.needed_data = tuple(needed_data)
        if int(self.visual_encoder.hidden_size) != VISUAL_DIM:
            raise ValueError("M0 requires the selected CLIP-768 visual features")
        if int(self.acoustic_encoder.hidden_size) != AUDIO_DIM:
            raise ValueError("M0 requires the selected HuBERT-1024 acoustic features")

    def train(self, mode=True):
        super().train(False)
        return self

    @staticmethod
    def pool(hidden, expected_dim):
        if hidden.ndim < 3 or hidden.shape[0] != 1 or hidden.shape[-1] != expected_dim:
            raise ValueError(f"Unexpected encoder hidden shape: {tuple(hidden.shape)}")
        pooled = hidden.float().reshape(1, -1, hidden.shape[-1]).mean(1)[0]
        if not torch.isfinite(pooled).all() or pooled.norm() <= 1e-12:
            raise ValueError("Encoder produced nonfinite or zero features for requested media")
        return pooled.detach().cpu()

    @torch.no_grad()
    def forward(self, media, device):
        self.eval()
        visual_key = next((key for key in ("face", "frame", "image") if key in self.needed_data), None)
        visual = torch.zeros(VISUAL_DIM)
        audio = torch.zeros(AUDIO_DIM)
        if visual_key:
            processed, raw = media.get(visual_key), media.get("raw_" + visual_key)
            if processed is None or raw is None:
                raise ValueError(f"Missing required {visual_key} media")
            hidden = self.visual_encoder(processed.unsqueeze(0).to(device), raw.unsqueeze(0).to(device))
            visual = self.pool(hidden, VISUAL_DIM)
        if "audio" in self.needed_data:
            processed, raw = media.get("audio"), media.get("raw_audio")
            if processed is None or raw is None:
                raise ValueError("Missing required audio media")
            hidden = self.acoustic_encoder(processed.unsqueeze(0).to(device), raw.unsqueeze(0).to(device))
            audio = self.pool(hidden, AUDIO_DIM)
        return visual, audio, visual_key is not None, "audio" in self.needed_data


def load_extractor(cfg, needed_data, device):
    # Registration imports definitions only. Never call AffectGPT.from_config.
    import config
    import my_affectgpt.models.encoder
    from my_affectgpt.common.registry import registry
    visual_name, audio_name = cfg.model.visual_encoder, cfg.model.acoustic_encoder
    if visual_name != "CLIP_VIT_LARGE" or audio_name != "HUBERT_LARGE":
        raise ValueError("M0 currently supports CLIP_VIT_LARGE + HUBERT_LARGE only")
    artifacts = {
        "visual": encoder_artifacts(config.PATH_TO_VISUAL[visual_name]),
        "audio": encoder_artifacts(config.PATH_TO_AUDIO[audio_name]),
    }
    visual = registry.get_visual_encoder_class(visual_name)()
    acoustic = registry.get_acoustic_encoder_class(audio_name)()
    extractor = FrozenAVExtractor(visual, acoustic, needed_data).to(device).eval()
    return extractor, artifacts


def extract_records(records, reader, extractor, device, *, progress=None, workers=0):
    """Extract in manifest order with bounded optional CPU media prefetch.

    At most workers media futures are queued/running, plus the current clip.
    Only decoding/evaluation transforms run in threads. Encoder calls stay on
    the caller thread, one clip at a time; completed reads never reorder IDs.
    """
    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 0:
        raise ValueError("--workers must be a nonnegative integer")
    visuals, audios, vv, av = [], [], [], []
    pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="amg-media") if workers else None
    pending = deque()
    next_index = 0
    try:
        if pool is not None:
            for next_index in range(min(workers, len(records))):
                pending.append((next_index, pool.submit(media_sample, reader, records[next_index])))
            next_index = len(pending)
        for index, record in enumerate(records):
            try:
                if pool is None:
                    media = media_sample(reader, record)
                else:
                    submitted_index, future = pending.popleft()
                    if submitted_index != index:
                        raise AssertionError("Media prefetch order differs from the manifest")
                    media = future.result()
                    # Refill only one slot. Queue size never grows with the
                    # manifest, and this next CPU read overlaps GPU extraction.
                    if next_index < len(records):
                        pending.append((next_index, pool.submit(media_sample, reader, records[next_index])))
                        next_index += 1
                visual, audio, visual_valid, audio_valid = extractor(media, device)
            except Exception as error:
                raise RuntimeError(
                    f"Memory extraction aborted at row {index + 1}, clip_id={record['name']}: "
                    f"{type(error).__name__}: {error}; no replacement or skipping"
                ) from error
            visuals.append(visual)
            audios.append(audio)
            vv.append(visual_valid)
            av.append(audio_valid)
            if progress is not None:
                progress(index + 1, len(records), record["name"])
            del media
            if pool is not None:
                del future
    finally:
        if pool is not None:
            # Active CPU reads may finish, but queued work is cancelled and no
            # later clip is extracted after any read/extraction failure.
            for _, future in pending:
                future.cancel()
            pool.shutdown(wait=True, cancel_futures=True)
    return torch.stack(visuals), torch.stack(audios), torch.tensor(vv), torch.tensor(av)


def build_bank(config_path, manifest_path, output_path, *, device="cpu", limit=None,
               face_or_frame=None, workers=0, reader_loader=load_media_reader, extractor_loader=load_extractor):
    config_path, manifest_path, output_path = (Path(p).resolve() for p in (config_path, manifest_path, output_path))
    sidecar = Path(str(output_path) + ".json")
    if output_path.exists() or sidecar.exists():
        raise FileExistsError(f"Bank output or sidecar already exists: {output_path}")
    if limit is not None and limit < 1:
        raise ValueError("--limit must be a positive integer")
    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 0:
        raise ValueError("--workers must be a nonnegative integer")
    cfg = load_config(config_path, face_or_frame=face_or_frame)
    all_records = read_manifest(manifest_path)
    records = all_records if limit is None else all_records[:limit]
    reader = reader_loader(cfg)
    extractor, artifacts = extractor_loader(cfg, reader.needed_data, device)
    def progress(done, total, clip_id):
        if done == 1 or done == total or done % 100 == 0:
            print(json.dumps({"extracted": done, "requested": total, "clip_id": clip_id}), flush=True)
    visual, audio, vv, av = extract_records(records, reader, extractor, device, progress=progress, workers=workers)
    num_frames = int(cfg.model.vis_processor.train.n_frms)
    metadata = {
        "schema": SCHEMA,
        "face_or_frame": str(cfg.datasets.mercaptionplus.face_or_frame),
        "num_frames": num_frames,
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "total_manifest_records": len(all_records),
        "records": len(records),
        "complete": limit is None and len(records) == len(all_records),
        "partial_for_testing": limit is not None,
        "visual_encoder": str(cfg.model.visual_encoder),
        "acoustic_encoder": str(cfg.model.acoustic_encoder),
        "encoder_artifacts": artifacts,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "sampling": {"visual": "original-uniform-repeat-last-if-short", "audio": "original-8x2s"},
        "feature_contract": "original-prefusion-hidden-float32-global-mean-v1",
        "compute_dtype": "float32",
    }
    digest = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
    metadata["version"] = "amg-m0-" + digest
    bank = MemoryBank(visual, audio, [r["name"] for r in records],
                      [r["group_id"] for r in records], vv, av, version=metadata["version"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bank_temp = output_path.with_name(output_path.name + ".tmp")
    json_temp = sidecar.with_name(sidecar.name + ".tmp")
    try:
        bank.save(bank_temp)
        metadata["bank_sha256"] = sha256_file(bank_temp)
        metadata["created_at"] = datetime.now(timezone.utc).isoformat()
        json_temp.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(bank_temp, output_path)
        os.replace(json_temp, sidecar)
    finally:
        bank_temp.unlink(missing_ok=True)
        json_temp.unlink(missing_ok=True)
    print(json.dumps({key: metadata[key] for key in
          ("schema", "version", "records", "complete", "partial_for_testing", "bank_sha256")}), flush=True)
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--limit", type=int, help="Test-only partial bank; never marked complete")
    parser.add_argument("--face-or-frame")
    parser.add_argument("--workers", type=int, default=0,
                        help="Bounded CPU media prefetch threads; 0 preserves serial reads (try 4)")
    args = parser.parse_args(argv)
    # Original encoder constructors use local paths. Enforce no remote fallback.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    torch.set_num_threads(max(1, int(os.environ.get("OMP_NUM_THREADS", "2"))))
    return build_bank(args.config, args.manifest, args.output, device=args.device,
                      limit=args.limit, face_or_frame=args.face_or_frame, workers=args.workers)


if __name__ == "__main__":
    main()
