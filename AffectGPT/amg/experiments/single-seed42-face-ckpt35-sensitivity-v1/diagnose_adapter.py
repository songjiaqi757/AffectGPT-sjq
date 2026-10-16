# Replay the trained M0 adapter on real dev queries without loading Qwen.
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback

ROOT = Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
sys.path.insert(0, str(ROOT))
SCHEMA = "amg-adapter-sensitivity-row-v1"
META_KEYS = ("amg_sha256", "base_sha256", "memory_sha256", "manifest_sha256",
             "trained_mode", "dataset", "task", "question", "seed", "face_or_frame",
             "config_sha256", "infer_sha256", "base_dataset_sha256",
             "budget_source_sha256", "prompt_sha256", "decoding")

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text())

def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def write_json(path, payload):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")

def require(value, message):
    if not value:
        raise ValueError(message)

def finite_tree(value, prefix="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            finite_tree(item, prefix + "." + str(key))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            finite_tree(item, prefix + "[" + str(index) + "]")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        require(math.isfinite(value), "Nonfinite diagnostic: " + prefix)

def tensor_comparison(left, right):
    import torch
    a, b = left.detach().float().reshape(-1), right.detach().float().reshape(-1)
    require(a.shape == b.shape, "Comparison tensor shapes differ")
    require(bool(torch.isfinite(a).all() and torch.isfinite(b).all()), "Nonfinite tensors")
    an, bn = float(a.norm()), float(b.norm())
    delta = float((a-b).norm())
    cosine = float(torch.dot(a, b) / (a.norm() * b.norm())) if an and bn else float(an == bn)
    return {"cosine": min(1.0, max(-1.0, cosine)), "relative_l2": delta / max(an, 1e-12),
            "l2": delta, "max_abs": float((a-b).abs().max()) if a.numel() else 0.0,
            "left_norm": an, "right_norm": bn}

def _attention_diagnostic(adapter, query, values, mask, reference, gate):
    import torch
    q = adapter.query_projection(query)[:, None, :] + adapter.queries[None]
    v = adapter.value_projection(values)
    attended, weights = adapter.attention(q, v, v, key_padding_mask=~mask,
                                         need_weights=True, average_attn_weights=False)
    diagnostic_tokens = adapter.output_projection(attended) * gate[:, None, :]
    entropy = -(weights.float() * weights.float().clamp_min(1e-30).log()).sum(-1)
    candidates = mask.sum(-1).float().clamp_min(2).log()[:, None, None]
    return {"weights": weights[0].detach().cpu().tolist(),
            "entropy_per_head_slot": entropy[0].detach().cpu().tolist(),
            "normalized_entropy_mean": float((entropy/candidates).mean()),
            "max_weight_mean": float(weights.max(-1).values.float().mean()),
            "forward_token_max_abs_error": float((diagnostic_tokens-reference).abs().max())}

def _without_query_condition(adapter, query, values, mask, fixed_gate):
    # Delete only the additive Q_MLP(query) branch; keep learned slots, values,
    # original query-conditioned gate, and all trained weights unchanged.
    q = adapter.queries[None].expand(query.shape[0], -1, -1)
    v = adapter.value_projection(values)
    attended, _ = adapter.attention(q, v, v, key_padding_mask=~mask, need_weights=False)
    return adapter.output_projection(attended) * fixed_gate[:, None, :]

def diagnose(adapter, query, normal_values, random_values, normal_mask, random_mask):
    import torch
    require(not adapter.training, "Adapter must be in eval mode")
    normal = adapter(query, normal_values, normal_mask, dropout_p=0.0)
    random = adapter(query, random_values, random_mask, dropout_p=0.0)
    require(bool(normal.enabled.all() and random.enabled.all()), "Inactive memory in diagnostic")
    require(torch.equal(normal.gate, random.gate), "Same query produced different gates")
    n_queryless = _without_query_condition(adapter, query, normal_values, normal_mask, normal.gate)
    r_queryless = _without_query_condition(adapter, query, random_values, random_mask, normal.gate)
    condition = adapter.query_projection(query)
    slots = adapter.queries.float().norm(dim=-1)
    result = {
        "tokens": {"float32": tensor_comparison(normal.tokens, random.tokens),
                   "float16_cast": tensor_comparison(normal.tokens.half(), random.tokens.half())},
        "value_sets": {"raw_mean": tensor_comparison(normal_values.mean(1), random_values.mean(1)),
                       "projected_mean": tensor_comparison(adapter.value_projection(normal_values).mean(1),
                                                           adapter.value_projection(random_values).mean(1))},
        "attention": {
            "normal": _attention_diagnostic(adapter, query, normal_values, normal_mask, normal.tokens, normal.gate),
            "random": _attention_diagnostic(adapter, query, random_values, random_mask, random.tokens, normal.gate)},
        "query_condition": {"query_mlp_norm": float(condition.norm()),
                            "learned_slot_norms": slots.detach().cpu().tolist(),
                            "query_to_mean_slot_norm_ratio": float(condition.norm()/slots.mean().clamp_min(1e-12)),
                            "removed_q_fixed_gate": {
                                "normal_vs_random": tensor_comparison(n_queryless, r_queryless),
                                "normal_vs_original": tensor_comparison(normal.tokens, n_queryless),
                                "random_vs_original": tensor_comparison(random.tokens, r_queryless)}},
        "gate": float(normal.gate.reshape(-1)[0]),
    }
    finite_tree(result)
    return result

def _trace_table(path, expected_names):
    records = rows(path)
    require([r["name"] for r in records] == expected_names, "Trace ordered IDs differ: " + str(path))
    result = {}
    for record in records:
        require(not record.get("error"), "Trace contains an error")
        trace = record["retrieval"]
        require(trace["memory_enabled"] == [True], "Trace has disabled memory")
        ids = trace["retrieved_ids"][0]
        require(len(ids) == len(set(ids)) == 5 and all(isinstance(n, str) for n in ids), "Invalid fixed neighbors")
        require(len(trace["gate"]) == 1 and len(trace["gate"][0]) == 1, "Invalid gate trace shape")
        require(math.isfinite(float(trace["gate"][0][0])), "Invalid gate")
        result[record["name"]] = record
    return result

def _validate_protocol(p):
    normal, random = read(p["normal_metadata"]), read(p["random_metadata"])
    for key in META_KEYS:
        require(normal.get(key) == random.get(key), "Inference metadata mismatch: " + key)
    require(normal["trained_mode"] == random["trained_mode"] == "retrieval", "Wrong trained mode")
    require(normal["memory_mode"] == "retrieval" and random["memory_mode"] == "random", "Wrong intervention modes")
    require(normal["seed"] == p["seed"] == 42, "Seed must be 42")
    for meta in (normal, random):
        require(meta["successes"] == 500 and meta["errors"] == 0 and meta["selected_clips"] == 500,
                "Incomplete original inference")
    for field, expected in (("amg_checkpoint", normal["amg_sha256"]),
                            ("bank", normal["memory_sha256"]),
                            ("manifest", normal["manifest_sha256"]),
                            ("base_config", normal["config_sha256"])):
        require(sha(p[field]) == expected, "Artifact hash mismatch: " + field)
    require(sha(ROOT/"amg/infer.py") == normal["infer_sha256"], "Original inference source changed")
    return normal, random

def worker(args):
    import torch
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    current = None
    started = utcnow()
    try:
        p = read(args.protocol)
        require(args.device.startswith("cuda"), "Worker requires a CUDA device")
        require(0 <= args.start < args.end <= 500, "Invalid shard interval")
        torch.cuda.set_per_process_memory_fraction(0.20, device=torch.device(args.device))
        torch.set_num_threads(2)
        from amg.runtime import load_config, seed_all, media_sample
        from amg.build_memory import load_media_reader, load_extractor
        from amg.memory import MemoryAdapter, MemoryBank
        seed_all(p["seed"])
        normal_meta, random_meta = _validate_protocol(p)
        records = rows(p["manifest"])
        names = [r["name"] for r in records]
        require(len(names) == len(set(names)) == 500, "Dev manifest must contain 500 unique IDs")
        ntrace, rtrace = _trace_table(p["normal_trace"], names), _trace_table(p["random_trace"], names)
        checkpoint = torch.load(p["amg_checkpoint"], map_location="cpu", weights_only=True, mmap=True)
        saved = checkpoint["config"]
        require(checkpoint["schema"] == "amg-m0-train-v1" and saved["mode"] == "retrieval", "Wrong checkpoint")
        require(saved["base_sha256"] == normal_meta["base_sha256"] and
                saved["memory_sha256"] == normal_meta["memory_sha256"], "Checkpoint provenance differs")
        cfg = load_config(p["base_config"], face_or_frame=saved["face_or_frame"])
        require(str(cfg.datasets.mercaptionplus.face_or_frame) == normal_meta["face_or_frame"], "Wrong face/frame")
        bank_meta = read(str(p["bank"]) + ".json")
        require(bank_meta["complete"] and bank_meta["records"] == bank_meta["total_manifest_records"] == 4000,
                "Bank must be the complete 4K fit bank")
        require(bank_meta["bank_sha256"] == normal_meta["memory_sha256"], "Bank metadata hash differs")
        require(sha(bank_meta["manifest_path"]) == bank_meta["manifest_sha256"], "Fit manifest changed")
        fit_names = {r["name"] for r in rows(bank_meta["manifest_path"])}
        require(len(fit_names) == 4000 and not (fit_names & set(names)), "Fit/dev leakage or count mismatch")
        reader = load_media_reader(cfg)
        extractor, artifacts = load_extractor(cfg, reader.needed_data, args.device)
        require(artifacts == bank_meta.get("encoder_artifacts"), "Frozen encoder artifact bytes/path/version changed")
        require(str(cfg.model.visual_encoder) == bank_meta["visual_encoder"] and
                str(cfg.model.acoustic_encoder) == bank_meta["acoustic_encoder"] and
                int(cfg.model.vis_processor.train.n_frms) == bank_meta["num_frames"] and
                str(cfg.datasets.mercaptionplus.face_or_frame) == bank_meta["face_or_frame"], "Feature contract changed")
        bank = MemoryBank.load(p["bank"], expected_version=bank_meta["version"]).to(args.device)
        require(len(bank) == 4000 and set(bank.clip_ids) == fit_names, "Loaded bank IDs differ from fit")
        state = {key[len("memory_adapter."):]:value for key,value in checkpoint["model"].items()
                 if key.startswith("memory_adapter.")}
        require(state, "Checkpoint has no trained adapter")
        adapter = MemoryAdapter(d_query=1792, d_value=1792, d_hidden=int(saved["hidden_dim"]),
                                llm_dim=int(state["output_projection.1.weight"].shape[0]),
                                num_tokens=int(saved["num_tokens"])).float()
        adapter.load_state_dict(state, strict=True)
        adapter = adapter.requires_grad_(False).to(args.device).eval()
        require(all(bool(torch.isfinite(t).all()) for t in adapter.state_dict().values()), "Nonfinite adapter")
        del checkpoint, state
        lookup = {name:index for index,name in enumerate(bank.clip_ids)}
        cache = {"clip_ids":[], "visual":[], "audio":[], "visual_valid":[], "audio_valid":[],
                 "query":[], "normal_neighbor_ids":[], "random_neighbor_ids":[]}
        with (out/"rows.jsonl").open("x", encoding="utf-8") as stream, torch.inference_mode():
            for index in range(args.start, args.end):
                record = records[index]
                current = record["name"]
                media = media_sample(reader, record)
                # Match original encode_*_merge: FP16 autocast encoders, then FP32 pooling.
                with torch.autocast("cuda", dtype=torch.float16):
                    visual, audio, vv, av = extractor(media, args.device)
                del media
                visual_gpu, audio_gpu = visual[None].to(args.device), audio[None].to(args.device)
                vmask = torch.tensor([vv], device=args.device, dtype=torch.bool)
                amask = torch.tensor([av], device=args.device, dtype=torch.bool)
                replay = bank.retrieve(visual_gpu, audio_gpu, visual_valid=vmask, audio_valid=amask,
                                       clip_ids=[current], group_ids=[record["group_id"]],
                                       training=False, k=5, mode="retrieval")
                query = replay.query_features
                normal_ids = ntrace[current]["retrieval"]["retrieved_ids"][0]
                random_ids = rtrace[current]["retrieval"]["retrieved_ids"][0]
                fixed = []
                for ids in (normal_ids, random_ids):
                    require(all(name in lookup and name != current for name in ids), "Neighbor outside fit/self")
                    positions = torch.tensor([lookup[name] for name in ids], device=args.device)
                    values = bank.features[positions][None]
                    masks = (bank.valid_mask[positions] & replay.query_mask[0]).any(-1)[None]
                    require(bool(masks.all()), "A fixed neighbor has no shared valid modality")
                    fixed.append((values, masks))
                diagnostic = diagnose(adapter, query, *[fixed[0][0],fixed[1][0],fixed[0][1],fixed[1][1]])
                old_n = float(ntrace[current]["retrieval"]["gate"][0][0])
                old_r = float(rtrace[current]["retrieval"]["gate"][0][0])
                new_ids = replay.ids[0]
                diagnostic.update(schema=SCHEMA, index=index, name=current, group_id=record["group_id"],
                                  normal_neighbor_ids=normal_ids, random_neighbor_ids=random_ids,
                                  recomputed_neighbor_ids=new_ids,
                                  replay_fidelity={"ordered_top5_exact": new_ids == normal_ids,
                                      "top5_set_overlap":len(set(new_ids)&set(normal_ids)),
                                      "old_normal_gate":old_n,"old_random_gate":old_r,
                                      "normal_gate_abs_error":abs(diagnostic["gate"]-old_n),
                                      "random_gate_abs_error":abs(diagnostic["gate"]-old_r)})
                finite_tree(diagnostic)
                stream.write(json.dumps(diagnostic, ensure_ascii=False, allow_nan=False)+"\n")
                stream.flush()
                cache["clip_ids"].append(current)
                for key, value in (("visual",visual),("audio",audio),("query",query[0].cpu())):
                    cache[key].append(value.detach().float().cpu().clone())
                cache["visual_valid"].append(vv);cache["audio_valid"].append(av)
                cache["normal_neighbor_ids"].append(normal_ids);cache["random_neighbor_ids"].append(random_ids)
                if (index-args.start+1)%25 == 0 or index == args.end-1:
                    print(json.dumps({"completed":index-args.start+1,"requested":args.end-args.start,"clip_id":current}),flush=True)
        for key in ("visual","audio","query"):
            cache[key]=torch.stack(cache[key])
        for key in ("visual_valid","audio_valid"):
            cache[key]=torch.tensor(cache[key],dtype=torch.bool)
        cache.update(schema="amg-real-dev-query-cache-v1",start=args.start,end=args.end,
                     amg_sha256=normal_meta["amg_sha256"],bank_sha256=normal_meta["memory_sha256"],
                     manifest_sha256=normal_meta["manifest_sha256"],
                     encoder_compute="cuda_autocast_float16_then_float32_pooling",
                     adapter_compute="float32_then_output_cast_float16")
        torch.save(cache,out/"queries.pt")
        done={"schema":"amg-adapter-sensitivity-worker-v1","status":"complete","started_at":started,
              "completed_at":utcnow(),"start":args.start,"end":args.end,"N":args.end-args.start,
              "device":args.device,"physical_gpu":os.environ.get("CUDA_VISIBLE_DEVICES"),
              "amg_sha256":normal_meta["amg_sha256"],"bank_sha256":normal_meta["memory_sha256"],
              "manifest_sha256":normal_meta["manifest_sha256"],"encoder_artifacts_verified":True,
              "diagnostic_source_sha256":sha(__file__),"protocol_sha256":sha(args.protocol),
              "rows_sha256":sha(out/"rows.jsonl"),"queries_sha256":sha(out/"queries.pt")}
        write_json(out/"worker_done.json",done)
        print(json.dumps(done),flush=True)
    except BaseException as error:
        write_json(out/"worker_error.json",{"status":"failed","clip_id":current,"error":repr(error),
                   "traceback":traceback.format_exc(),"failed_at":utcnow(),"start":args.start,"end":args.end})
        raise

def distribution(values):
    values=sorted(float(x) for x in values)
    require(values and all(math.isfinite(x) for x in values),"Empty/nonfinite distribution")
    def percentile(p):
        position=(len(values)-1)*p
        left=int(position);right=min(left+1,len(values)-1)
        return values[left]+(values[right]-values[left])*(position-left)
    return {"N":len(values),"min":values[0],"mean":sum(values)/len(values),
            "p05":percentile(.05),"p50":percentile(.5),"p95":percentile(.95),"max":values[-1]}

def aggregate(root):
    import torch
    root=Path(root).resolve()
    p=read(root/"protocol.json")
    normal,_=_validate_protocol(p)
    expected=rows(p["manifest"])
    parts=[]
    for directory in (root/"worker0",root/"worker1"):
        done=read(directory/"worker_done.json")
        require(done["status"]=="complete", "Worker incomplete")
        require(done["rows_sha256"]==sha(directory/"rows.jsonl") and
                done["queries_sha256"]==sha(directory/"queries.pt"),"Worker artifact hash changed")
        require(done["amg_sha256"]==normal["amg_sha256"] and done["bank_sha256"]==normal["memory_sha256"] and
                done["manifest_sha256"]==normal["manifest_sha256"],"Worker provenance differs")
        require(done["diagnostic_source_sha256"]==sha(__file__) and done["protocol_sha256"]==sha(root/"protocol.json"),
                "Worker diagnostic/protocol version changed")
        records=rows(directory/"rows.jsonl")
        cache=torch.load(directory/"queries.pt",map_location="cpu",weights_only=True)
        require(len(records)==done["N"]==done["end"]-done["start"]==len(cache["clip_ids"]),"Shard counts differ")
        require(cache["clip_ids"]==[r["name"] for r in records],"Cache and rows IDs differ")
        for key,dim in (("visual",768),("audio",1024),("query",1792)):
            require(tuple(cache[key].shape)==(done["N"],dim) and bool(torch.isfinite(cache[key]).all()),
                    "Invalid/nonfinite cache: "+key)
        require(tuple(cache["visual_valid"].shape)==tuple(cache["audio_valid"].shape)==(done["N"],),"Mask shape differs")
        for record in records:
            finite_tree(record)
        parts.append((done["start"],done["end"],records))
    parts.sort()
    require(parts[0][0]==0 and parts[0][1]==parts[1][0] and parts[1][1]==500,"Shards must cover exact [0,500)")
    records=parts[0][2]+parts[1][2]
    require([r["name"] for r in records]==[r["name"] for r in expected] and
            [r["index"] for r in records]==list(range(500)),"Final ordered IDs/indices differ")
    paths=[
        "tokens.float32.cosine","tokens.float32.relative_l2","tokens.float32.left_norm","tokens.float32.right_norm",
        "tokens.float16_cast.cosine","tokens.float16_cast.relative_l2","tokens.float16_cast.max_abs",
        "value_sets.raw_mean.cosine","value_sets.raw_mean.relative_l2",
        "value_sets.projected_mean.cosine","value_sets.projected_mean.relative_l2",
        "attention.normal.normalized_entropy_mean","attention.random.normalized_entropy_mean",
        "attention.normal.max_weight_mean","attention.random.max_weight_mean",
        "attention.normal.forward_token_max_abs_error","attention.random.forward_token_max_abs_error",
        "query_condition.query_mlp_norm","query_condition.query_to_mean_slot_norm_ratio",
        "query_condition.removed_q_fixed_gate.normal_vs_random.cosine",
        "query_condition.removed_q_fixed_gate.normal_vs_random.relative_l2",
        "query_condition.removed_q_fixed_gate.normal_vs_original.relative_l2",
        "query_condition.removed_q_fixed_gate.random_vs_original.relative_l2",
        "replay_fidelity.normal_gate_abs_error","replay_fidelity.random_gate_abs_error","gate"]
    def get(record,path):
        for key in path.split("."):record=record[key]
        return record
    stats={path:distribution([get(r,path) for r in records]) for path in paths}
    fidelity={"ordered_top5_exact":sum(r["replay_fidelity"]["ordered_top5_exact"] for r in records),
              "ordered_top5_exact_fraction":sum(r["replay_fidelity"]["ordered_top5_exact"] for r in records)/500,
              "top5_set_overlap":distribution([r["replay_fidelity"]["top5_set_overlap"] for r in records]),
              "gate_abs_error_tolerance":1e-5,
              "normal_gate_within_tolerance":sum(r["replay_fidelity"]["normal_gate_abs_error"]<=1e-5 for r in records),
              "random_gate_within_tolerance":sum(r["replay_fidelity"]["random_gate_abs_error"]<=1e-5 for r in records)}
    summary={"schema":"amg-adapter-sensitivity-summary-v1","status":"complete","completed_at":utcnow(),
             "N":500,"amg_sha256":normal["amg_sha256"],"bank_sha256":normal["memory_sha256"],
             "manifest_sha256":normal["manifest_sha256"],"real_queries":True,"no_training":True,
             "no_qwen_or_text_generation":True,"replay_fidelity":fidelity,"distributions":stats,
             "limitations":["Adapter-internal diagnostic; it does not measure generation quality or causal task improvement.",
                            "Original normal/random neighbors are held fixed even when recomputed top-5 differs.",
                            "Q-branch deletion preserves the original gate and is not a task-performance ablation.",
                            "Attention weights are diagnostic need_weights=True; main tokens use original forward need_weights=False.",
                            "FP16 encoder replay and gate/top-5 audits quantify fidelity; no bitwise guarantee across devices.",
                            "Single trained seed and source dev already seen by the base checkpoint."]}
    finite_tree(summary)
    write_json(root/"summary.json",summary)
    lines=["# Trained Memory Adapter sensitivity","",
           "500 real source-dev queries; the same trained retrieval adapter and fixed original normal/random neighbors.",
           "No training, Qwen load, text generation, holdout or target evaluation.","",
           "Encoder replay uses CUDA FP16 autocast then FP32 pooling; Adapter computations use FP32.",
           "Token comparison additionally reports the FP16 cast used at LLM insertion.","",
           f"Recomputed ordered top-5 exactly matched: {fidelity['ordered_top5_exact']}/500.",
           f"Replayed gate absolute error <= 1e-5: normal {fidelity['normal_gate_within_tolerance']}/500, random {fidelity['random_gate_within_tolerance']}/500.","",
           "|Diagnostic|Mean|Median|P95|Maximum|","|---|---:|---:|---:|---:|"]
    for path in paths:
        d=stats[path];lines.append(f"|{path}|{d['mean']:.6g}|{d['p50']:.6g}|{d['p95']:.6g}|{d['max']:.6g}|")
    lines.extend(["","The query-branch deletion removes only Q_MLP(query), preserving learned query slots and original gate.",
                  "These measurements describe internal sensitivity and numerical replay, not proof of a training cause or a performance gain.",
                  "See summary.json limitations and per-worker rows.jsonl / queries.pt for all 500 cases."])
    with (root/"SUMMARY.md").open("x",encoding="utf-8") as stream:stream.write("\n".join(lines)+"\n")
    print(json.dumps({"status":"complete","N":500,"summary":str(root/"summary.json"),"replay_fidelity":fidelity}),flush=True)

def main():
    parser=argparse.ArgumentParser(description="Replay frozen AV queries and trained Memory Adapter without Qwen.")
    parser.add_argument("--protocol",type=Path)
    parser.add_argument("--start",type=int)
    parser.add_argument("--end",type=int)
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--device",default="cuda:0")
    parser.add_argument("--aggregate",type=Path)
    args=parser.parse_args()
    if args.aggregate:
        return aggregate(args.aggregate)
    if args.protocol is None or args.start is None or args.end is None or args.output_dir is None:
        parser.error("worker requires --protocol, --start, --end and --output-dir")
    worker(args)

if __name__=="__main__":
    main()
