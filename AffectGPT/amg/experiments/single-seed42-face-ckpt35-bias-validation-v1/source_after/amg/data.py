"""AMG dataset adapter. The unchanged AffectGPT dataset stays available.

Only the observed subtitle is returned to the frozen BGE branch. Training
answers remain in Qwen's masked causal-LM target and never enter `subtitles`.
"""
from __future__ import annotations

import logging
import random
from pathlib import Path

import torch
from transformers import AutoTokenizer

import config
from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
from my_affectgpt.datasets.datasets.mercaptionplus_dataset import MERCaptionPlus_Dataset
from .manifest import build_source_records, read_manifest
from .budget import budget_prompt

LOGGER = logging.getLogger(__name__)
QUESTION_MARKER = "Now, please answer my question based on all the provided information."


def load_fast_training_tokenizer(model_name: str):
    """Same vocabulary and special-token order as the original Qwen loader."""
    tokenizer = AutoTokenizer.from_pretrained(config.PATH_TO_LLM[model_name], use_fast=True)
    if model_name in ("Qwen2", "Qwen25"):
        tokenizer.bos_token = "<|im_start|>"
    tokenizer.pad_token = tokenizer.eos_token
    for token in (config.DEFAULT_IMAGE_PATCH_TOKEN, config.DEFAULT_AUDIO_PATCH_TOKEN,
                  config.DEFAULT_FRAME_PATCH_TOKEN, config.DEFAULT_FACE_PATCH_TOKEN,
                  config.DEFAULT_MULTI_PATCH_TOKEN):
        tokenizer.add_tokens([token], special_tokens=True)
    if not tokenizer.is_fast:
        raise ValueError("AMG requires a fast tokenizer with offset_mapping support")
    return tokenizer


def _index_from_offsets(prompt: str, offsets, bos_offset: int) -> int:
    # rfind prevents an occurrence quoted in the observed subtitle taking priority.
    start = prompt.rfind(QUESTION_MARKER)
    if start < 0:
        raise ValueError(f"Prompt does not contain the question marker {QUESTION_MARKER!r}")
    for index, (left, right) in enumerate(offsets):
        left, right = int(left), int(right)
        if right > start:
            return index + bos_offset
    raise ValueError("Question marker was truncated; memory insertion cannot be located")


def memory_insert_index(tokenizer, prompt: str, bos_offset: int = 1,
                        max_length: int | None = None) -> int:
    """Token boundary before the question; index includes the collater's BOS.

    Fast-tokenizer offsets avoid prefix-retokenization errors at BPE boundaries.
    Inference callers without a manually prepended BOS must pass bos_offset=0.
    """
    options = {"add_special_tokens": False, "return_offsets_mapping": True}
    if max_length is not None:
        options.update(max_length=max_length, truncation=True)
    encoded = tokenizer(prompt, **options)
    return _index_from_offsets(prompt, encoded["offset_mapping"], bos_offset)


class AMGTrainingDataset(MERCaptionPlus_Dataset):
    """MER-Caption+ with stable metadata and explicit failed-read replacements.

    BaseDataset.__init__ is called only for shared fields with both configs None.
    Its default three-sample debug path reads media and consumes random state;
    the small tokenizer/config setup is reproduced here to avoid those reads.
    No model weights or GPU state are allocated by this constructor.
    """

    def __init__(self, vis_processor=None, txt_processor=None, img_processor=None,
                 dataset_cfg=None, model_cfg=None, *, manifest_path=None,
                 tokenizer=None, max_retries: int = 10, memory_tokens: int | None = None):
        if model_cfg is None or dataset_cfg is None:
            raise ValueError("model_cfg and dataset_cfg are required")
        if max_retries < 1:
            raise ValueError("max_retries must be positive")
        self.dataset = "MERCaptionPlus"
        self.annotation = (read_manifest(manifest_path) if manifest_path is not None else
                           build_source_records(Path(config.DATA_DIR[self.dataset])))
        BaseDataset.__init__(self, vis_processor=vis_processor, txt_processor=txt_processor,
                             img_processor=img_processor, model_cfg=None, dataset_cfg=None,
                             vis_root=config.PATH_TO_RAW_VIDEO[self.dataset], ann_path=manifest_path or "",
                             wav_root=config.PATH_TO_RAW_AUDIO[self.dataset],
                             face_root=config.PATH_TO_RAW_FACE[self.dataset])
        self.model_cfg, self.dataset_cfg = model_cfg, dataset_cfg
        self.label_type, self.face_or_frame = dataset_cfg.label_type, dataset_cfg.face_or_frame
        self.label_type_candidates = ["description", "ovlabel"]
        self.needed_data = self.get_needed_data(self.face_or_frame)
        self.max_length = int(model_cfg.max_length)
        self.memory_tokens = int(getattr(model_cfg, "amg_memory_tokens", 4)
                                 if memory_tokens is None else memory_tokens)
        if self.memory_tokens < 0:
            raise ValueError("memory_tokens must be nonnegative")
        self.n_frms = model_cfg.vis_processor.train.n_frms
        for name in ("num_video_query_token", "num_audio_query_token", "num_multi_query_token", "num_image_query_token"):
            setattr(self, name, getattr(model_cfg, name))
        self.tokenizer = tokenizer or load_fast_training_tokenizer(model_cfg.llama_model)
        if not getattr(self.tokenizer, "is_fast", False):
            raise ValueError("Pass a fast Qwen tokenizer; AMG uses offset_mapping for insertion")
        vocab = self.tokenizer.get_vocab()
        for attr, token in (("IMAGE_PATCH_TOKEN_ID", config.DEFAULT_IMAGE_PATCH_TOKEN),
                            ("AUDIO_PATCH_TOKEN_ID", config.DEFAULT_AUDIO_PATCH_TOKEN),
                            ("FRAME_PATCH_TOKEN_ID", config.DEFAULT_FRAME_PATCH_TOKEN),
                            ("FACE_PATCH_TOKEN_ID", config.DEFAULT_FACE_PATCH_TOKEN),
                            ("MULTI_PATCH_TOKEN_ID", config.DEFAULT_MULTI_PATCH_TOKEN)):
            setattr(self, attr, vocab[token])
        ratio = float(dataset_cfg.get("ratio", 1.0)) if hasattr(dataset_cfg, "get") else float(getattr(dataset_cfg, "ratio", 1.0))
        if not 0 < ratio <= 1:
            raise ValueError("dataset ratio must be in (0, 1]")
        if ratio < 1:
            self.annotation = self.func_random_sample_subset(self.annotation, ratio=ratio)
        if not self.annotation:
            raise ValueError("Dataset is empty")
        self.max_retries = max_retries
        self.manifest_path = str(manifest_path) if manifest_path is not None else None

    def __getitem__(self, index):
        original_id = self.annotation[index]["name"]
        failures = []
        for attempt in range(self.max_retries):
            sample = self.annotation[index]
            try:
                cur_label_type = self.get_cur_label_type(self.label_type_candidates, self.label_type)
                media = self.read_frame_face_audio_text(
                    self._get_video_path(sample), self._get_face_path(sample),
                    self._get_audio_path(sample), None)
                qa = self.get_qa_pairs(self.dataset, cur_label_type, sample)
                # Never truncate targets independently: the entire answer and
                # delimiter are reserved before only the observed ASR is clipped.
                target_ids = self.tokenizer(qa["answer"] + "###", return_tensors="pt",
                                            add_special_tokens=False)["input_ids"][0]
                budgeted = budget_prompt(self.tokenizer,
                    lambda subtitle: self.replace_token_for_multimodal(self.get_prompt_for_multimodal(
                        self.face_or_frame, subtitle, qa["question"])),
                    sample["subtitle"], max_length=self.max_length,
                    target_tokens=len(target_ids), bos_tokens=1, eos_tokens=1,
                    memory_tokens=self.memory_tokens)
                prompt_ids = torch.tensor(budgeted.input_ids, dtype=torch.long)
                insertion = _index_from_offsets(budgeted.prompt, budgeted.offsets, bos_offset=1)
                text_input = torch.cat([prompt_ids, target_ids])
                labels = torch.cat([torch.full_like(prompt_ids, config.IGNORE_INDEX), target_ids])
            except Exception as error:
                failures.append({"clip_id": sample["name"], "error": f"{type(error).__name__}: {error}"})
                LOGGER.warning("AMG failed clip %s (requested %s), attempt %d/%d: %s",
                               sample["name"], original_id, attempt + 1, self.max_retries, error)
                if attempt + 1 < self.max_retries:
                    index = random.randint(0, len(self) - 1)
                continue
            result = {key: media.get(key) for key in
                      ("face", "raw_face", "frame", "raw_frame", "audio", "raw_audio", "image", "raw_image")}
            result.update(label=labels, text_input=text_input, dataset=self.dataset.lower(),
                          face_or_frame=self.face_or_frame, clip_id=sample["name"],
                          actual_id=sample["name"], original_id=original_id,
                          group_id=sample["group_id"], subtitle=sample["subtitle"],
                          memory_insert_index=insertion, was_replaced=sample["name"] != original_id,
                          replacement_failures=failures, task_type=cur_label_type,
                          budget_metadata=budgeted.metadata)
            return result
        raise RuntimeError(f"Failed AMG sample requested={original_id} after {self.max_retries} attempts: {failures}")

    def collater(self, instances):
        batch = super().collater(instances)
        for singular, plural in (("clip_id", "clip_ids"), ("actual_id", "actual_ids"),
                                 ("original_id", "original_ids"), ("group_id", "group_ids"),
                                 ("subtitle", "subtitles"), ("was_replaced", "was_replaced"),
                                 ("replacement_failures", "replacement_failures"),
                                 ("task_type", "task_types"), ("budget_metadata", "budget_metadata")):
            batch[plural] = [instance[singular] for instance in instances]
        batch["max_length"] = self.max_length
        batch["memory_insert_indices"] = torch.tensor(
            [instance["memory_insert_index"] for instance in instances], dtype=torch.long)
        return batch
