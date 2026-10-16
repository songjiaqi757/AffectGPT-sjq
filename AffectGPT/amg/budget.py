"""Shared total-context budgeting for AMG training and generation.

The modality blocks, task instruction and complete training target are immutable.
Only the observed ASR subtitle may be shortened, at tokenizer offset boundaries.
Every mode reserves the same possible memory width for paired comparisons;
Memory-off still inserts no tokens during embedding assembly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class BudgetedPrompt:
    prompt: str
    input_ids: tuple[int, ...]
    offsets: tuple[tuple[int, int], ...]
    subtitle: str
    metadata: dict


def _encode(tokenizer, text, *, offsets=False):
    options = {"add_special_tokens": False}
    if offsets:
        options["return_offsets_mapping"] = True
    encoded = tokenizer(text, **options)
    ids = tuple(int(value) for value in encoded["input_ids"])
    spans = tuple((int(left), int(right)) for left, right in encoded["offset_mapping"]) if offsets else ()
    return ids, spans


def budget_prompt(tokenizer, render_prompt: Callable[[str], str], subtitle: str, *,
                  max_length: int, target_tokens: int = 0, bos_tokens: int = 1,
                  eos_tokens: int = 0, memory_tokens: int = 4,
                  generation_tokens: int = 0) -> BudgetedPrompt:
    """Fit a full sequence into max_length, trimming only the ASR prefix.

    Training reserves the untruncated target plus BOS/EOS and memory. Generation
    reserves BOS, memory and max_new_tokens. Prompt tokens are always re-encoded
    after subtitle clipping, so BPE merges at the subtitle boundary are included.
    """
    counts = {"max_length": max_length, "target_tokens": target_tokens,
              "bos_tokens": bos_tokens, "eos_tokens": eos_tokens,
              "memory_tokens": memory_tokens, "generation_tokens": generation_tokens}
    if any(not isinstance(value, int) or isinstance(value, bool) for value in counts.values()):
        raise ValueError("Length budgets must be integer token counts")
    if max_length < 1 or any(value < 0 for key, value in counts.items() if key != "max_length"):
        raise ValueError("max_length must be positive and reserved token counts nonnegative")
    if not isinstance(subtitle, str):
        raise ValueError("Observed subtitle must be a string")
    reserve = target_tokens + bos_tokens + eos_tokens + memory_tokens + generation_tokens
    capacity = max_length - reserve
    original_subtitle_ids, subtitle_offsets = _encode(tokenizer, subtitle, offsets=True)

    def encode_prompt(text):
        prompt = render_prompt(text)
        ids, spans = _encode(tokenizer, prompt, offsets=True)
        return prompt, ids, spans

    prompt, ids, spans = encode_prompt(subtitle)
    kept_subtitle = subtitle
    if len(ids) > capacity:
        empty_prompt = encode_prompt("")
        if len(empty_prompt[1]) > capacity:
            raise ValueError(
                f"Fixed prompt ({len(empty_prompt[1])}) + full target ({target_tokens}) "
                f"+ BOS/EOS ({bos_tokens + eos_tokens}) + memory ({memory_tokens}) "
                f"+ generation ({generation_tokens}) exceeds max_length={max_length}; "
                "only ASR subtitle may be shortened (no silent truncation)")
        # Prefix boundaries come from the original fast-tokenizer offsets.
        # Re-encoding each candidate handles contextual BPE changes. Binary
        # search is conservative even when a boundary changes token merging:
        # only a candidate measured to fit can become the retained prefix.
        boundaries = sorted({0, len(subtitle), *(right for _, right in subtitle_offsets
                                                if 0 <= right <= len(subtitle))})
        low, high, best = 0, len(boundaries) - 1, 0
        best_encoded = empty_prompt
        while low <= high:
            middle = (low + high) // 2
            candidate = encode_prompt(subtitle[:boundaries[middle]])
            if len(candidate[1]) <= capacity:
                best, best_encoded = boundaries[middle], candidate
                low = middle + 1
            else:
                high = middle - 1
        kept_subtitle = subtitle[:best]
        prompt, ids, spans = best_encoded
    kept_subtitle_ids, _ = _encode(tokenizer, kept_subtitle)
    base_input = len(ids) + target_tokens + bos_tokens + eos_tokens
    metadata = {
        "schema": "amg-context-budget-v1",
        "policy": "asr_prefix_only_shared_memory_budget_v1",
        "max_length": max_length,
        "subtitle_tokens_original": len(original_subtitle_ids),
        "subtitle_tokens_kept": len(kept_subtitle_ids),
        "subtitle_tokens_truncated": max(0, len(original_subtitle_ids) - len(kept_subtitle_ids)),
        "subtitle_characters_truncated": len(subtitle) - len(kept_subtitle),
        "prompt_tokens": len(ids),
        "target_tokens": target_tokens,
        "bos_tokens": bos_tokens,
        "eos_tokens": eos_tokens,
        "memory_tokens_reserved": memory_tokens,
        "generation_tokens_reserved": generation_tokens,
        "input_tokens_without_memory": base_input,
        "final_tokens_with_memory": base_input + memory_tokens,
        "total_tokens_with_generation": base_input + memory_tokens + generation_tokens,
    }
    if metadata["total_tokens_with_generation"] > max_length:
        raise AssertionError("Shared length budgeting produced an overlong sequence")
    return BudgetedPrompt(prompt, ids, spans, kept_subtitle, metadata)
