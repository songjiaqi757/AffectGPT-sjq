"""Shared train/inference embedding assembly with a true no-memory branch."""
from dataclasses import dataclass
from typing import Optional

import torch
from torch import Tensor, nn
import torch.nn.functional as F


@dataclass
class AssemblyOutput:
    inputs_embeds: Tensor
    attention_mask: Tensor
    labels: Optional[Tensor]
    position_ids: Tensor
    memory_enabled: Tensor
    lengths: Tensor


def assemble_inputs(input_ids, base_embedding, attention_mask=None, labels=None,
                    modality_replacements=None, memory_tokens=None,
                    memory_enabled=None, insert_indices=None, pad_token_id=0,
                    max_length=None):
    """Replace AV placeholders, insert enabled memory, and right-pad the batch.

    insert_indices index the original unpadded sequence, including its real BOS.
    Original mask zeros inside the sequence are preserved. In particular, legacy
    AffectGPT can supervise a final EOS whose token ID equals PAD and whose
    attention mask is zero. Such labels extend the retained sequence span.
    Disabled rows receive no memory tokens at all, preserving baseline positions.
    """
    if max_length is not None and (not isinstance(max_length, int) or max_length < 1):
        raise ValueError("max_length must be a positive integer")
    if input_ids.ndim != 2:
        raise ValueError("input_ids must have shape [B,L]")
    b, original_width = input_ids.shape
    if attention_mask is None:
        attention_mask = input_ids.ne(pad_token_id).long()
    if tuple(attention_mask.shape) != tuple(input_ids.shape):
        raise ValueError("attention_mask and input_ids shapes differ")
    if labels is not None and tuple(labels.shape) != tuple(input_ids.shape):
        raise ValueError("labels and input_ids shapes differ")
    if bool(((attention_mask != 0) & (attention_mask != 1)).any()):
        raise ValueError("attention_mask must contain only 0/1 values")
    replacements = modality_replacements or {}
    safe_ids = input_ids.clone()
    for token_id in replacements:
        if not isinstance(token_id, int):
            raise ValueError("modality replacement keys must be integer token IDs")
        safe_ids = safe_ids.masked_fill(input_ids.eq(token_id), 0)
    embeds = base_embedding(safe_ids)
    if embeds.ndim != 3 or tuple(embeds.shape[:2]) != (b, original_width):
        raise ValueError("base_embedding must produce [B,L,D]")
    device, dtype, dim = embeds.device, embeds.dtype, embeds.shape[-1]
    attention_mask = attention_mask.to(device)
    if labels is not None:
        labels = labels.to(device)
    active = torch.zeros(b, dtype=torch.bool, device=device)
    if memory_tokens is not None:
        if memory_tokens.ndim != 3 or memory_tokens.shape[0] != b or memory_tokens.shape[2] != dim:
            raise ValueError("memory_tokens must have shape [B,M,D]")
        memory_tokens = memory_tokens.to(device=device, dtype=dtype)
        active = torch.ones(b, dtype=torch.bool, device=device)
        if memory_enabled is not None:
            if tuple(memory_enabled.shape) != (b,):
                raise ValueError("memory_enabled must have shape [B]")
            active &= memory_enabled.to(device=device, dtype=torch.bool)
        if memory_tokens.shape[1] == 0:
            active[:] = False
    elif memory_enabled is not None:
        if tuple(memory_enabled.shape) != (b,):
            raise ValueError("memory_enabled must have shape [B]")
        if bool(memory_enabled.any()):
            raise ValueError("enabled memory requires memory_tokens")
    if bool(active.any()):
        if insert_indices is None or tuple(insert_indices.shape) != (b,):
            raise ValueError("enabled memory requires insert_indices with shape [B]")
        insert_indices = insert_indices.to(device=device, dtype=torch.long)
    for token_id, value in replacements.items():
        if not isinstance(token_id, int):
            raise ValueError("modality replacement keys must be integer token IDs")
        if value.ndim != 3 or value.shape[0] != b or value.shape[2] != dim:
            raise ValueError("modality replacements must have shape [B,K,D]")
    row_embeds, row_masks, row_labels, lengths = [], [], [], []
    for i in range(b):
        retained = attention_mask[i].bool()
        if labels is not None:
            retained = retained | labels[i].ne(-100)
        retained_positions = retained.nonzero(as_tuple=False).flatten()
        length = int(retained_positions[-1]) + 1 if retained_positions.numel() else 0
        row = embeds[i, :length].clone()
        row_ids = input_ids[i, :length]
        row_mask = attention_mask[i, :length]
        row_label = labels[i, :length] if labels is not None else None
        for token_id, value in replacements.items():
            positions = row_ids.eq(token_id).nonzero(as_tuple=False).flatten().to(device)
            if positions.numel() != value.shape[1]:
                raise ValueError(
                    f"row {i}: token {token_id} has {positions.numel()} occurrences; "
                    f"replacement supplies {value.shape[1]}")
            row[positions] = value[i].to(device=device, dtype=dtype)
        if bool(active[i]):
            index = int(insert_indices[i])
            if not 0 <= index <= length:
                raise ValueError(f"row {i}: memory insertion index outside retained sequence")
            memory = memory_tokens[i]
            row = torch.cat((row[:index], memory, row[index:]), dim=0)
            row_mask = torch.cat((row_mask[:index],
                                  row_mask.new_ones(memory.shape[0]), row_mask[index:]), dim=0)
            if row_label is not None:
                row_label = torch.cat((row_label[:index],
                                       row_label.new_full((memory.shape[0],), -100),
                                       row_label[index:]), dim=0)
        if max_length is not None and row.shape[0] > max_length:
            raise ValueError(f"row {i}: assembled length {row.shape[0]} exceeds max_length={max_length}")
        row_embeds.append(row)
        row_masks.append(row_mask)
        row_labels.append(row_label)
        lengths.append(row.shape[0])
    width = max(lengths, default=0)
    if b:
        output_embeds = torch.stack([F.pad(row, (0, 0, 0, width - row.shape[0]))
                                     for row in row_embeds])
        output_masks = torch.stack([F.pad(row, (0, width - row.shape[0]))
                                    for row in row_masks])
        output_labels = None if labels is None else torch.stack([
            F.pad(row, (0, width - row.shape[0]), value=-100) for row in row_labels])
    else:
        output_embeds = embeds[:, :0]
        output_masks = attention_mask[:, :0]
        output_labels = None if labels is None else labels[:, :0]
    length_tensor = torch.tensor(lengths, device=device, dtype=torch.long)
    # Legacy Qwen forward defaults to arange positions even at masked EOS tokens.
    positions = torch.arange(width, device=device).expand(b, -1).clone()
    positions = positions.masked_fill(
        torch.arange(width, device=device)[None] >= length_tensor[:, None], 0)
    return AssemblyOutput(output_embeds, output_masks, output_labels,
                          positions, active, length_tensor)

