"""Binary supervision; semantic unknowns never become negative labels."""
import numpy as np
import torch
from sklearn.metrics import average_precision_score, precision_recall_fscore_support

def masked_bce_sum(logits, targets, mask, pos_weight=None):
    if logits.shape != targets.shape or logits.shape != mask.shape:
        raise ValueError("logits, targets and mask must have identical shapes")
    mask = mask.bool()
    safe = torch.where(mask, targets, torch.zeros_like(targets)).float()
    if not torch.isfinite(safe).all(): raise ValueError("Non-finite supervised target")
    if ((safe[mask] != 0) & (safe[mask] != 1)).any(): raise ValueError("Only binary supervised targets")
    loss = torch.nn.functional.binary_cross_entropy_with_logits(logits.float(), safe, pos_weight=pos_weight, reduction="none")
    return loss.masked_select(mask).sum(), int(mask.sum())

def training_weights(targets, mask, weighted):
    positives = ((targets == 1) & mask).sum(0).astype(int)
    negatives = ((targets == 0) & mask).sum(0).astype(int)
    weights = np.ones(targets.shape[1], dtype=np.float32)
    good = (positives > 0) & (negatives > 0)
    if weighted: weights[good] = np.clip(np.sqrt(negatives[good] / positives[good]), 1, 20)
    return weights, positives, negatives

def binary_metrics(targets, scores, mask, cue_ids, thresholds=None, eligible=None):
    thresholds = np.full(len(cue_ids), .5) if thresholds is None else np.asarray(thresholds)
    if thresholds.shape != (len(cue_ids),) or not np.isfinite(thresholds).all():
        raise ValueError("One finite threshold per cue required")
    if eligible is None:
        eligible = [k for k in range(len(cue_ids)) if np.any(mask[:, k] & (targets[:, k] == 1)) and np.any(mask[:, k] & (targets[:, k] == 0))]
    per = {}; aps = []; fs = []
    for k, cue in enumerate(cue_ids):
        valid = mask[:, k].astype(bool); y = targets[valid, k]; p = scores[valid, k]
        pos, neg = int((y == 1).sum()), int((y == 0).sum())
        ap = float(average_precision_score(y, p)) if pos and neg else None
        if len(y):
            precision, recall, f1, _ = precision_recall_fscore_support(y, p >= thresholds[k], average="binary", zero_division=0)
        else: precision = recall = f1 = 0.
        per[cue] = dict(positive=pos, negative=neg, masked=int((~valid).sum()), coverage=float(valid.mean()) if len(valid) else 0.,
                        ap=ap, precision=float(precision), recall=float(recall), f1=float(f1), threshold=float(thresholds[k]),
                        evaluable=pos > 0 and neg > 0)
        if k in eligible:
            if ap is None: raise ValueError("The fixed evaluation cue set changed")
            aps.append(ap); fs.append(float(f1))
    flat = mask.astype(bool)
    if flat.any():
        pred = scores >= thresholds[None, :]
        pr, re, f1, _ = precision_recall_fscore_support(targets[flat], pred[flat], average="binary", zero_division=0)
    else: pr = re = f1 = 0.
    return dict(per_cue=per, eligible_cue_ids=[cue_ids[k] for k in eligible],
                macro_ap=float(np.mean(aps)) if aps else None, macro_f1=float(np.mean(fs)) if fs else None,
                micro_precision=float(pr), micro_recall=float(re), micro_f1=float(f1),
                threshold_status="uncalibrated_0.5" if np.all(thresholds == .5) else "provided_thresholds",
                reference="Teacher pseudo-labels; not human accuracy")

def group_bootstrap(targets, scores, mask, groups, cue_ids, repeats=200, seed=42):
    """Optional independent evaluation intervals; omitted when a bootstrap draw has no two-class support."""
    rng = np.random.default_rng(seed); unique = sorted(set(groups)); groups = np.asarray(groups)
    values = {c: [] for c in cue_ids}
    if not unique: raise ValueError("No groups")
    for _ in range(repeats):
        chosen = rng.choice(unique, len(unique), replace=True)
        idx = np.concatenate([np.flatnonzero(groups == g) for g in chosen])
        metrics = binary_metrics(targets[idx], scores[idx], mask[idx], cue_ids)
        for cue, row in metrics["per_cue"].items():
            if row["ap"] is not None: values[cue].append(row["ap"])
    return {c: dict(ap_95ci=np.percentile(v, [2.5, 97.5]).tolist() if v else None, valid_draws=len(v)) for c, v in values.items()}
