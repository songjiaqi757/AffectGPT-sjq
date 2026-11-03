"""CPU-only experimental graph evidence repair. Never imports Torch or modifies base releases."""
from __future__ import annotations
from graph_paths import resolve_path as _graph_resolve_path
import copy, json, hashlib
from graph_paths import Path
import numpy as np

VERSION = "appraisal_candidate_repair_v1"
MODALITIES = np.array([0] * 15 + [1] * 17 + [2] * 10)

def normalise_states(values, groups):
    out = values.copy()
    for ss in groups:
        total = out[:, ss].sum(1, keepdims=True)
        out[:, ss] = np.divide(out[:, ss], total, out=np.full_like(out[:, ss], 1 / len(ss)), where=total > 0)
    return out

def fit_counts(cues, masks, states, valid, train, groups):
    x = cues[train] & masks[train]
    joint = x.astype(float).T @ states[train].astype(float)
    positive = np.stack([(x & valid[train, d, None]).sum(0) for d in range(len(groups))], 1)
    eligible = np.stack([(masks[train] & valid[train, d, None]).sum(0) for d in range(len(groups))], 1)
    prior = states[train].sum(0).astype(float)
    for ss in groups:
        prior[ss] = (prior[ss] + .5) / (prior[ss].sum() + .5 * len(ss))
    return joint, positive, eligible, prior

def conditionals(joint, positive, prior, groups, kappa=.5):
    dim_of_state = np.empty(len(prior), dtype=int)
    for d, ss in enumerate(groups):
        dim_of_state[ss] = d
    return (joint + kappa * prior[None, :]) / np.maximum(positive[:, dim_of_state] + kappa, 1e-15)

def app_scores(q, conditional, positive, prior, groups, prior_correction=0.):
    out = np.zeros((len(q), len(prior)))
    covered = np.zeros((len(q), len(groups)), bool)
    for d, ss in enumerate(groups):
        qw = q * (positive[:, d] >= 20)[None, :]
        z = qw.sum(1)
        covered[:, d] = z > 0
        out[:, ss] = np.divide(qw @ conditional[:, ss], z[:, None],
            out=np.tile(prior[ss], (len(q), 1)), where=z[:, None] > 0)
    correction = np.asarray(prior_correction)
    if correction.ndim == 0:
        out /= np.maximum(prior[None, :], 1e-12) ** correction
    else:
        for d, ss in enumerate(groups):
            out[:, ss] /= np.maximum(prior[ss], 1e-12) ** correction[d]
    return normalise_states(out, groups), covered

def app_support(q, pred, conditional, positive, prior, joint, groups, config):
    n, nd = len(q), len(groups)
    passed = np.zeros((n, nd), bool)
    margin = np.zeros((n, nd))
    nc, nm = np.zeros((n, nd), int), np.zeros((n, nd), int)
    mass = np.zeros((n, nd))
    for d, ss in enumerate(groups):
        top = np.argmax(pred[:, ss], 1)
        rank = np.sort(pred[:, ss], axis=1)
        margin[:, d] = rank[:, -1] - rank[:, -2]
        support = ((q[:, :, None] > 0) &
            (positive[:, d, None] >= config["min_cue_eligible"]) &
            (joint[:, ss][None, :, :] >= config["min_state_joint_support"]) &
            ((conditional[:, ss] - prior[ss])[None, :, :] >= config["min_state_lift"]))
        selected = np.take_along_axis(support, np.broadcast_to(top[:, None, None], (n, 42, 1)), 2)[:, :, 0]
        nc[:, d] = selected.sum(1)
        nm[:, d] = sum(selected[:, MODALITIES == m].any(1) for m in range(3))
        mass[:, d] = (q * selected).sum(1) / np.maximum(q.sum(1), 1e-15)
        passed[:, d] = ((nc[:, d] >= config["app_min_cues"]) &
            (nm[:, d] >= config["app_min_modalities"]) &
            (mass[:, d] >= config["app_min_coverage"]))
        if d in config["disabled_dimension_indices"]:
            passed[:, d] = False
    passed &= margin >= np.asarray(config["app_margin_thresholds"])[None, :]
    return dict(passed=passed, margin=margin, support_cues=nc, support_modalities=nm, coverage=mass)

def wilson_low(correct, n):
    if not n:
        return 0.
    z, p = 1.96, correct / n
    return float((p + z*z/(2*n) - z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n))

def choose_margins(pred, target, valid, allowed, margins, train, groups):
    thresholds, table = [], []
    for d, ss in enumerate(groups):
        correct = np.argmax(pred[:, ss], 1) == np.argmax(target[:, ss], 1)
        rows = []
        for t in [0., .05, .1, .15, .2, .25, .3, .4, .5, .6, .7, .8, .9]:
            take = train & valid[:, d] & allowed[:, d] & (margins[:, d] >= t)
            n, right = int(take.sum()), int(correct[take].sum())
            rows.append(dict(margin=t, n=n, correct=right, accuracy=right/n if n else None, wilson_low=wilson_low(right, n)))
        ok = [r for r in rows if r["n"] >= 100 and r["wilson_low"] >= .75]
        selected = max(ok, key=lambda r: r["n"]) if ok else dict(margin=1.01, n=0, correct=0, accuracy=None, wilson_low=0.)
        thresholds.append(selected["margin"])
        table.append(dict(selected=selected, candidates=rows))
    return thresholds, table

def retrieval(q, wca, wce, wae, paths, groups, thresholds, state_override=None, dimension_gate=None, mixture=.75):
    """Exact C0 equations; C1 changes dimension-state mass, preserving admitted paths/edge scores.
    C2 allows only each dimension's accepted Top1 state into two-hop retrieval.
    Historical NPMI weights remain association strengths, never probabilities.
    """
    z = q.sum(1)
    native = np.divide(q @ wca, z[:, None], out=np.zeros((len(q), len(wae))), where=z[:, None] > 0)
    dim_mass = np.stack([native[:, ss].sum(1) for ss in groups], 1)
    state_pass = np.zeros_like(native, bool)
    state_mass = native.copy() if state_override is None else np.zeros_like(native)
    for d, ss in enumerate(groups):
        enabled = (dim_mass[:, d] > 0) & (dim_mass[:, d] >= thresholds[d])
        if dimension_gate is not None:
            enabled &= dimension_gate[:, d]
        if state_override is None:
            state_pass[:, ss] = (native[:, ss] > 0) & enabled[:, None]
        else:
            # Preserve the native dimension's overall association mass and within-dimension topology.
            state_mass[:, ss] = state_override[:, ss] * dim_mass[:, d, None]
            state_pass[:, ss] = (native[:, ss] > 0) & enabled[:, None]
            if dimension_gate is not None:
                top = np.argmax(state_override[:, ss], 1)
                state_pass[:, ss] &= np.arange(len(ss))[None, :] == top[:, None]
    an = q @ wca
    rn = np.einsum("nc,ca,cae->nae", q, wca, paths, optimize=True)
    ratio = np.divide(rn, an[:, :, None], out=np.zeros_like(rn), where=an[:, :, None] > 0)
    eff = ratio * state_pass[:, :, None] * wae[None, :, :]
    numerator = (state_mass[:, :, None] * eff).sum(1)
    denominator = np.zeros_like(numerator)
    for d, ss in enumerate(groups):
        denominator += dim_mass[:, d, None] * (eff[:, ss, :] > 0).any(1)
    two = np.divide(numerator, denominator, out=np.full_like(numerator, np.nan), where=denominator > 0)
    direct = np.divide(q @ wce, z[:, None], out=np.full_like(numerator, np.nan), where=z[:, None] > 0)
    direct[~((q > 0).astype(int) @ (wce > 0).astype(int) > 0)] = np.nan
    score = np.where(np.isfinite(direct) & np.isfinite(two), mixture * direct + (1-mixture) * two,
        np.where(np.isfinite(direct), direct, two))
    supporters = ((q[:, :, None] > 0) &
        ((wce > 0)[None, :, :] | (paths[None, :, :, :] & state_pass[:, None, :, None]).any(2)))
    return dict(score=score, direct=direct, two=two, supporters=supporters, native_app=native,
        native_dim_mass=dim_mass, state_pass=state_pass, state_mass=state_mass)

def candidate_gate(q, result, config):
    supporters = result["supporters"]
    nc = supporters.sum(1)
    nm = sum(supporters[:, MODALITIES == m, :].any(1) for m in range(3))
    coverage = (q[:, :, None] * supporters).sum(1) / np.maximum(q.sum(1)[:, None], 1e-15)
    score = result["score"]
    # No rank-1 gap controls other candidates; each candidate must pass its own checks.
    keep = (np.isfinite(score) & (score > 0) & (nc >= config["emotion_min_cues"]) &
        (nm >= config["emotion_min_modalities"]) & (coverage >= config["emotion_min_coverage"]))
    return dict(passed=keep, support_cues=nc, support_modalities=nm, coverage=coverage)

def top_mask(scores, ids, k=3, allowed=None):
    clean = np.where(np.isfinite(scores), scores, -np.inf)
    if allowed is not None:
        clean = np.where(allowed, clean, -np.inf)
    order = sorted(range(len(ids)), key=lambda i: ids[i])
    rank = np.asarray(order)[np.argsort(-clean[:, order], axis=1, kind="stable")]
    result = np.zeros_like(clean, bool)
    chosen = rank[:, :k]
    np.put_along_axis(result, chosen, np.isfinite(np.take_along_axis(clean, chosen, 1)), 1)
    return result, rank

class EvidenceRepair:
    """Load a fitted artifact and apply it to native engine output with frozen Cue scores.
    Repair variants have a separate schema/fingerprint; baseline returns the original evidence unchanged.
    Use ablation='baseline', 'conditional', 'balanced', 'conditional_gated', or 'balanced_gated'.
    """
    def __init__(self, directory):
        self.directory = Path(directory)
        self.meta = json.loads((self.directory / "config.json").read_text())
        expected_hash = self.meta.get("fitted_sha256")
        if expected_hash and hashlib.sha256((self.directory / "fitted.npz").read_bytes()).hexdigest() != expected_hash:
            raise ValueError("Fitted artifact checksum mismatch")
        with np.load(_graph_resolve_path(self.directory / 'fitted.npz'), allow_pickle=False) as z:
            self.a = {k: z[k] for k in z.files}
        self.groups = [np.asarray(v, int) for v in self.meta["state_groups"]]
        self.config = self.meta["gate"]
    def batch(self, q, ablation="baseline"):
        q = np.asarray(q, dtype=float)
        if q.ndim != 2 or q.shape[1] != 42 or not np.isfinite(q).all() or (q < 0).any():
            raise ValueError("Expected finite nonnegative N x 42 frozen query weights")
        if ablation not in ("baseline", "conditional", "balanced", "conditional_gated", "balanced_gated"):
            raise ValueError("Unknown ablation")
        a, g = self.a, self.groups
        correction = 1. if ablation.startswith("balanced") else 0.
        state, covered = app_scores(q, a["conditional"], a["positive"], a["prior"], g, correction)
        config = copy.deepcopy(self.config)
        config["app_margin_thresholds"] = self.meta["balanced_margins"] if correction else self.meta["conditional_margins"]
        app = app_support(q, state, a["conditional"], a["positive"], a["prior"], a["joint"], g, config)
        app["passed_before_applicability"] = app["passed"].copy()
        if "applicable_coef" in a:
            logits = (q > 0).astype(float) @ a["applicable_coef"].T + a["applicable_intercept"]
            probability = 1. / (1. + np.exp(-np.clip(logits, -40, 40)))
            thresholds = self.meta["balanced_applicability"] if correction else self.meta["conditional_applicability"]
            app["applicability_score"] = probability
            app["passed"] &= probability >= np.asarray(thresholds)[None, :]
        gated = ablation.endswith("_gated")
        ret = retrieval(q, a["wca"], a["wce"], a["wae"], a["paths"], g, self.meta["native_dimension_thresholds"],
            None if ablation == "baseline" else state, app["passed"] if gated else None, self.meta["mixture"])
        emotion = candidate_gate(q, ret, config)
        selected, rank = top_mask(ret["score"], self.meta["emotion_ids"], self.meta["emotion_top_k"],
            emotion["passed"] if gated else None)
        return dict(app=state, covered=covered, app_gate=app, retrieval=ret, emotion_gate=emotion,
            selected=selected, rank=rank, ablation=ablation)
    def apply(self, evidence, ablation="baseline"):
        if evidence.get("graph_release_id") != self.meta["graph_release_id"]:
            raise ValueError("Must use the frozen ten-class graph release")
        query = evidence.get("input_snapshot", {})
        if query.get("cue_id_order") != self.meta["cue_ids"]:
            raise ValueError("Cue ID order mismatch")
        if query.get("cue_release_id") != self.meta["cue_release_id"]:
            raise ValueError("Cue release mismatch")
        if ablation == "baseline":
            return copy.deepcopy(evidence)
        result = self.batch([query["query_weights"]], ablation)
        apps = []
        for d, ss in enumerate(self.groups):
            top = int(ss[np.argmax(result["app"][0, ss])])
            keep = bool(result["app_gate"]["passed"][0, d] if ablation.endswith("_gated") else result["covered"][0, d])
            apps.append(dict(dimension_id=self.meta["dimensions"][d], proposed_state=self.meta["state_ids"][top],
                score=float(result["app"][0, top]), score_semantics="conditional association, optionally prior-corrected; not calibrated probability",
                display_candidates=[self.meta["state_ids"][top]] if keep else [], passed=keep,
                margin=float(result["app_gate"]["margin"][0, d]), support_cues=int(result["app_gate"]["support_cues"][0, d]),
                support_modalities=int(result["app_gate"]["support_modalities"][0, d]),
                query_coverage=float(result["app_gate"]["coverage"][0, d])))
        candidates = []
        for e in result["rank"][0]:
            if result["selected"][0, e]:
                candidates.append(dict(emotion_id=self.meta["emotion_ids"][e], canonical_name=self.meta["emotion_names"][e],
                    association_score=float(result["retrieval"]["score"][0, e]),
                    support_cues=int(result["emotion_gate"]["support_cues"][0, e]),
                    support_modalities=int(result["emotion_gate"]["support_modalities"][0, e]),
                    query_coverage=float(result["emotion_gate"]["coverage"][0, e])))
        out = dict(schema_version=VERSION, sample_id=evidence["sample_id"], ablation=ablation,
            source_query_result_id=evidence.get("query_result_id"), repair_id=self.meta["repair_id"],
            score_semantics="source Teacher association hypotheses; no human validation; not final labels",
            query_cues=copy.deepcopy(evidence.get("query_cues", [])),
            appraisal_dimensions=apps, emotion_candidates=candidates,
            fallback=dict(required=not candidates, target="original_affectgpt",
                reason="no_candidate_passed_individual_support_gate" if not candidates else None))
        out["repair_result_id"] = hashlib.sha256(json.dumps(out, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        return out
