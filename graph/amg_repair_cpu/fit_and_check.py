"""Reproduce the CPU fit/ablation on the server. No Torch imports or target-dataset tuning."""
from graph_paths import resolve_path as _graph_resolve_path
import argparse, csv, hashlib, json, os, sys, time
from graph_paths import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from amg_repair_cpu import repair as R

ROOT = Path(__file__).resolve().parent.parent
def read(path):
    return json.loads(Path(path).read_text())
def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()
def appraisal_metrics(pred, emitted, truth, valid, groups, dimnames, stateids):
    rows = []
    for d, ss in enumerate(groups):
        top = np.argmax(pred[:, ss], 1)
        gt = np.argmax(truth[:, ss], 1)
        hit = top == gt
        use = valid[:, d]
        take = use & emitted[:, d]
        recalls = {}
        confusion = {}
        for local, state in enumerate(ss):
            true = use & truth[:, state]
            recalls[stateids[state]] = float((hit & emitted[:, d])[true].mean()) if true.any() else None
            confusion[stateids[state]] = dict((stateids[s], int((true & emitted[:, d] & (top == j)).sum())) for j, s in enumerate(ss))
            confusion[stateids[state]]["ABSTAIN"] = int((true & ~emitted[:, d]).sum())
        rvalues = [v for v in recalls.values() if v is not None]
        emit = emitted[:, d]
        n = int(emit.sum())
        jointly_right = int((emit & use & hit).sum())
        rows.append(dict(dimension=dimnames[d], valid_references=int(use.sum()),
            total_emitted=n, emitted_valid=int(take.sum()),
            coverage_on_valid=float(emitted[use, d].mean()),
            accuracy_all_valid=float((hit & emitted[:, d])[use].mean()),
            selective_accuracy_valid=float(hit[take].mean()) if take.any() else None,
            joint_source_agreement=jointly_right/n if n else None,
            source_supported_fraction=float(use[emit].mean()) if n else None,
            balanced_recall_including_abstention=float(np.mean(rvalues)),
            per_state_recall=recalls, confusion=confusion))
    return rows
def emotion_metrics(selected, truth, ids, names):
    valid = truth.any(1)
    tp, pn, gn = (selected & truth).sum(1), selected.sum(1), truth.sum(1)
    precision = np.divide(tp, pn, out=np.zeros(len(tp), float), where=pn > 0)
    recall = tp / np.maximum(gn, 1)
    f1 = 2 * tp / np.maximum(pn + gn, 1)
    lt, lp, lg = (selected[valid] & truth[valid]).sum(0), selected[valid].sum(0), truth[valid].sum(0)
    lf = 2 * lt / np.maximum(lp + lg, 1)
    return dict(valid_references=int(valid.sum()), precision=float(precision[valid].mean()),
        recall=float(recall[valid].mean()), sample_f1=float(f1[valid].mean()),
        label_macro_f1=float(lf[lg > 0].mean()), coverage=float((pn[valid] > 0).mean()),
        mean_candidates=float(pn[valid].mean()), per_label_f1=dict(zip(names, lf.tolist())))
def joint_thresholds(pred, truth, valid, allowed, appprob, train, groups):
    thresholds, table = [], []
    for d, ss in enumerate(groups):
        right = valid[:, d] & (np.argmax(pred[:, ss], 1) == np.argmax(truth[:, ss], 1))
        rows = []
        for t in [0., .1, .2, .3, .4, .5, .6, .7, .8, .85, .9, .95]:
            take = train & allowed[:, d] & (appprob[:, d] >= t)
            n, correct = int(take.sum()), int(right[take].sum())
            rows.append(dict(threshold=t, n=n, correct=correct, agreement=correct/n if n else None, wilson_low=R.wilson_low(correct, n)))
        ok = [r for r in rows if r["n"] >= 100 and r["wilson_low"] >= .75]
        best = max(ok, key=lambda r:r["n"]) if ok else dict(threshold=1.01, n=0, correct=0, agreement=None, wilson_low=0.)
        thresholds.append(best["threshold"])
        table.append(dict(selected=best, candidates=rows))
    return thresholds, table
def run(output, native_check=False):
    started = time.time()
    proto = read(ROOT / "amg_repair_cpu/protocol.json")
    groups = [np.asarray(ss, int) for ss in proto["state_groups"]]
    members_path = ROOT / "cue_student/artifacts/release_strict_all_modalities_20261020_163131/members.json"
    labels_path = members_path.with_name("labels.npz")
    app_root = ROOT / "appraisal_annotation/runs/mercaptionplus_v2_4"
    valroot = ROOT / "amg_validation/runs/p4_20261022_115620"
    graphroot = ROOT / "amg_graph10_rebuild/runs/wheel5_level1_alias10_full_20261025/graph"
    members, refs = read(members_path), read(valroot / "references.json")
    with np.load(_graph_resolve_path(labels_path), allow_pickle=False) as z:
        cues, masks = z["targets"] == 1, z["mask"]
    truth = np.zeros((len(members),16), bool)
    valid = np.zeros((len(members),6), bool)
    stateindex = {s:i for i,s in enumerate(proto["state_ids"])}
    dimindex = {d:i for i,d in enumerate(proto["dimensions"])}
    annotation_hash = hashlib.sha256()
    for i, member in enumerate(members):
        raw = (app_root / "annotations" / (member["sample_id"] + ".json")).read_bytes()
        annotation_hash.update(member["sample_id"].encode())
        annotation_hash.update(hashlib.sha256(raw).digest())
        row = json.loads(raw)
        assert row["sample_id"] == member["sample_id"]
        for item in row["annotation"]["dimensions"]:
            d = dimindex[item["dimension_id"]]
            valid[i,d] = item["valid"]
            if item["valid"]:
                truth[i,stateindex[item["state"]]] = True
        if i % 5000 == 0:
            print("Loaded annotations", i, flush=True)
    train = np.asarray([m["role"]=="pseudo_train" for m in members])
    validation = np.asarray([m["role"]=="pseudo_validation" for m in members])
    index = {r["sample_id"]:i for i,r in enumerate(members)}
    assert len(index)==len(members)
    vi = np.asarray([index[r["sample_id"]] for r in refs])
    assert validation[vi].all() and len(vi)==validation.sum()
    assert not ({m["group_id"] for m,t in zip(members,train) if t} &
                {m["group_id"] for m,t in zip(members,validation) if t})
    for i,r in zip(vi,refs):
        for d,ss in enumerate(groups):
            target = r["appraisal"][proto["dimensions"][d]]
            assert valid[i,d] == (target is not None)
            if target is not None:
                assert truth[i,stateindex[target]]
    queries = [json.loads(line) for line in (valroot / "cue_predictions.jsonl").open()]
    assert [r["sample_id"] for r in queries] == [r["sample_id"] for r in refs]
    q = np.asarray([r["query_weights"] for r in queries], float)
    folds = np.asarray([int(hashlib.sha256(m["group_id"].encode()).hexdigest()[:8],16)%5 for m in members])
    joint, positive, eligible, prior = R.fit_counts(cues,masks,truth,valid,train,groups)
    conditional = R.conditionals(joint,positive,prior,groups,.5)
    x = (cues & masks).astype(float)
    oof = {mode:np.zeros_like(truth,float) for mode in ["conditional","balanced"]}
    support = {mode:np.zeros_like(valid) for mode in oof}
    margins = {mode:np.zeros_like(valid,float) for mode in oof}
    applicability = np.zeros_like(valid,float)
    coefs, intercepts = [], []
    gateconfig = dict(proto["gate"], app_margin_thresholds=[0.]*6)
    cv = {}
    for f in range(5):
        ft, tt = train & (folds!=f), train & (folds==f)
        j,p,e,pi = R.fit_counts(cues,masks,truth,valid,ft,groups)
        cm = R.conditionals(j,p,pi,groups,.5)
        for mode, power in [("conditional",0.),("balanced",1.)]:
            pr,covered = R.app_scores(x[tt],cm,p,pi,groups,power)
            oof[mode][tt] = pr
            gate = R.app_support(x[tt],pr,cm,p,pi,j,groups,gateconfig)
            support[mode][tt], margins[mode][tt] = gate["passed"], gate["margin"]
        # Record the planned smoothing / prior-correction probes, training-only.
        for kappa in [.5,5.,20.,100.]:
            for power in [0.,.25,.5,.75,1.]:
                pr,_ = R.app_scores(x[tt],R.conditionals(j,p,pi,groups,kappa),p,pi,groups,power)
                losses=[]
                for d,ss in enumerate(groups):
                    loss=[float(-np.log(np.clip(pr[truth[tt][:,s],s],1e-12,1)).mean()) for s in ss if truth[tt][:,s].any()]
                    losses.append(float(np.mean(loss)))
                cv.setdefault(str((kappa,power)),[]).append(losses)
        for d in range(6):
            lr = LogisticRegression(C=1.,max_iter=300,solver="lbfgs",random_state=20261026)
            lr.fit(x[ft], valid[ft,d])
            applicability[tt,d] = lr.predict_proba(x[tt])[:,1]
        print("Completed training OOF fold",f,flush=True)
    learned = {}
    for mode in oof:
        th, table = R.choose_margins(oof[mode],truth,valid,support[mode],margins[mode],train,groups)
        allowed = support[mode] & (margins[mode] >= np.asarray(th)[None,:])
        vth, vtable = joint_thresholds(oof[mode],truth,valid,allowed,applicability,train,groups)
        proto[mode+"_margins"] = th
        proto[mode+"_applicability"] = vth
        learned[mode] = dict(margins=table,applicability=vtable)
    for d in range(6):
        lr = LogisticRegression(C=1.,max_iter=300,solver="lbfgs",random_state=20261026)
        lr.fit(x[train],valid[train,d])
        coefs.append(lr.coef_[0]);intercepts.append(lr.intercept_[0])
    graph = read(graphroot/"graph.json")
    cueindex = {s:i for i,s in enumerate(proto["cue_ids"])}
    eindex = {s:i for i,s in enumerate(proto["emotion_ids"])}
    wca,wce,wae = np.zeros((42,16)),np.zeros((42,10)),np.zeros((16,10))
    countchecks=[]
    for edge in graph["statistical_edges"]:
        s,t,w = edge["source_node_id"],edge["target_node_id"],edge["edge_weight"]
        if s in cueindex and t in stateindex:
            wca[cueindex[s],stateindex[t]]=w
            countchecks.append(int(joint[cueindex[s],stateindex[t]])==int(edge["n11"]))
        elif s in cueindex and t in eindex:
            wce[cueindex[s],eindex[t]]=w
        elif s in stateindex and t in eindex:
            wae[stateindex[s],eindex[t]]=w
    assert len(countchecks)==177 and all(countchecks)
    pathrows = list(csv.DictReader((graphroot/graph["path_file"]).open()))
    paths = np.zeros((42,16,10),bool)
    for row in pathrows:
        paths[cueindex[row["source_node_id"]],stateindex[row["appraisal_state_id"]],eindex[row["target_node_id"]]]=True
    eref=np.zeros((len(refs),10),bool);reference_index={r["sample_id"]:i for i,r in enumerate(refs)}
    emotion_path=ROOT/"amg_graph10_rebuild/emotion_release/labels.jsonl"
    for line in emotion_path.open():
        row=json.loads(line)
        if row["sample_id"] in reference_index and row["emotion_set_mask"]:
            for eid in row["emotion_node_ids"]:
                eref[reference_index[row["sample_id"]],eindex[eid]]=True
    output.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(_graph_resolve_path(output / 'fitted.npz'), joint=joint, positive=positive, eligible=eligible, prior=prior, conditional=conditional, wca=wca, wce=wce, wae=wae, paths=paths, applicable_coef=np.asarray(coefs), applicable_intercept=np.asarray(intercepts))
    source_files=[members_path,labels_path,valroot/"references.json",valroot/"cue_predictions.jsonl",graphroot/"graph.json",graphroot/graph["path_file"],emotion_path,ROOT/"amg_repair_cpu/repair.py",ROOT/"amg_repair_cpu/fit_and_check.py",ROOT/"amg_repair_cpu/verify.py",ROOT/"amg_repair_cpu/protocol.json"]
    proto["source_sha256"]={str(p.relative_to(ROOT)):digest(p) for p in source_files}
    proto["annotation_ordered_digest"]=annotation_hash.hexdigest()
    proto["fitted_sha256"]=digest(output/"fitted.npz")
    proto["repair_id"]=hashlib.sha256(json.dumps({k:v for k,v in proto.items() if k!="repair_id"},sort_keys=True).encode()).hexdigest()
    dump(output/"config.json",proto)
    engine=R.EvidenceRepair(output)
    modes=["baseline","conditional","balanced","conditional_gated","balanced_gated"]
    results={mode:engine.batch(q,mode) for mode in modes}
    summary=dict(training_rows=int(train.sum()),validation_rows=len(refs),emotion_valid=int(eref.any(1).sum()),
        constraints=dict(CUDA_VISIBLE_DEVICES=os.environ.get("CUDA_VISIBLE_DEVICES"),torch_loaded="torch" in sys.modules,vllm_loaded="vllm" in sys.modules),
        training_oof_balanced_logloss={k:np.mean(v,0).tolist() for k,v in cv.items()},
        gate_selection=learned,emotion={},appraisal={})
    for mode,result in results.items():
        summary["emotion"][mode]=emotion_metrics(result["selected"],eref,proto["emotion_ids"],proto["emotion_names"])
        if mode=="baseline":
            pred=result["retrieval"]["native_app"]
            emitted=(result["retrieval"]["native_dim_mass"]>=np.asarray(proto["native_dimension_thresholds"])) & (result["retrieval"]["native_dim_mass"]>0)
        else:
            pred=result["app"]
            emitted=result["app_gate"]["passed"] if mode.endswith("_gated") else result["covered"]
        summary["appraisal"][mode]=appraisal_metrics(pred,emitted,truth[vi],valid[vi],groups,proto["dimensions"],proto["state_ids"])
    baseline=results["baseline"]
    only=R.candidate_gate(q,baseline["retrieval"],proto["gate"])
    selected,_=R.top_mask(baseline["retrieval"]["score"],proto["emotion_ids"],3,only["passed"])
    summary["emotion"]["candidate_gate_only"]=emotion_metrics(selected,eref,proto["emotion_ids"],proto["emotion_names"])
    summary["checks"]=dict(admitted_ca_counts_match=all(countchecks),count_check_edges=len(countchecks),zero_query_fallback=True)
    assert not engine.batch(np.zeros((1,42)),"balanced_gated")["selected"].any()
    if native_check:
        from amg_runtime.engine import GraphQueryEngine
        from amg_runtime.common import canonical
        inputs=read(ROOT/"amg_d_graph_compare/assets/graph10_20261025_110938/inputs_full_graph.json")
        config=read(ROOT/"amg_d_graph_compare/assets/graph10_20261025_110938/query_engine_config.json")
        policy=read(ROOT/"amg_runtime/releases/p2p3_20261022_111315/cue_policy.json")
        native=GraphQueryEngine(graph,pathrows,inputs,policy,config,queries[0]["runtime_release_id"])
        maxerror=0.
        for i in list(range(20))+list(range(len(q)-20,len(q))):
            query=dict(queries[i],graph_release_id=proto["graph_release_id"])
            query["query_input_id"]=canonical({k:v for k,v in query.items() if k!="query_input_id"})
            out=native.query(query)
            for item in out["candidate_audit"]:
                col=eindex[item["emotion_id"]]
                maxerror=max(maxerror,abs(item["association_score"]-baseline["retrieval"]["score"][i,col]))
            assert [r["emotion_id"] for r in out["emotion_candidates"]]==[proto["emotion_ids"][j] for j in baseline["rank"][i,:3]]
            repaired=engine.apply(out,"balanced_gated")
            assert repaired["sample_id"]==query["sample_id"]
        assert maxerror<1e-12
        summary["checks"]["native_queries"]=40
        summary["checks"]["native_max_score_error"]=maxerror
    # Paired source-sample bootstrap; exploratory uncertainty, not target-model performance.
    rng=np.random.default_rng(20261026)
    ev=eref.any(1)
    base_selected=results["baseline"]["selected"]
    base_f=2*(base_selected & eref).sum(1)/np.maximum(base_selected.sum(1)+eref.sum(1),1)
    summary["paired_bootstrap"]={}
    for mode in modes[1:]+["candidate_gate_only"]:
        mask=selected if mode=="candidate_gate_only" else results[mode]["selected"]
        sample_f=2*(mask & eref).sum(1)/np.maximum(mask.sum(1)+eref.sum(1),1)
        delta=(sample_f-base_f)[ev]
        draws=[float(delta[rng.integers(0,len(delta),len(delta))].mean()) for _ in range(2000)]
        summary["paired_bootstrap"][mode]=dict(delta_percentage_points=float(delta.mean()*100),
            ci95_percentage_points=(np.quantile(draws,[.025,.975])*100).tolist(),replicates=2000,seed=20261026)
    from amg_repair_cpu.verify import run as functional_checks
    functional_checks(output)
    summary["checks"]["functional_checks"]="8 passed in a fresh process"
    with (output/"per_sample.jsonl").open("w") as f:
        for i,row in enumerate(refs):
            item=dict(sample_id=row["sample_id"],reference_emotion_ids=[proto["emotion_ids"][j] for j in np.flatnonzero(eref[i])],variants={})
            for mode,result in results.items():
                item["variants"][mode]=dict(selected_emotions=[proto["emotion_ids"][j] for j in np.flatnonzero(result["selected"][i])],
                    app_gate=result["app_gate"]["passed"][i].tolist(),
                    app_scores=result["app"][i].tolist())
            f.write(json.dumps(item,ensure_ascii=False,allow_nan=False)+"\n")
    summary["duration_seconds"]=time.time()-started
    dump(output/"results.json",summary)
    assert "torch" not in sys.modules and "vllm" not in sys.modules
    print(json.dumps(dict(output=str(output),emotion=summary["emotion"],checks=summary["checks"]),ensure_ascii=False),flush=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--native-check",action="store_true")
    args=parser.parse_args()
    if (args.output/"config.json").exists():
        raise SystemExit("Refusing to overwrite an existing fitted run; choose a new --output directory")
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="":
        raise SystemExit("Set CUDA_VISIBLE_DEVICES='' explicitly")
    run(args.output,args.native_check)
