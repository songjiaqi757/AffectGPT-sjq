"""Read-only functional checks for the CPU repair interface and gates."""
import argparse, copy, json
from graph_paths import Path
import numpy as np
from amg_repair_cpu.repair import EvidenceRepair, candidate_gate, app_support
def run(directory):
    repair=EvidenceRepair(directory)
    a,meta=repair.a,repair.meta
    query=dict(cue_id_order=meta["cue_ids"],cue_release_id=meta["cue_release_id"],query_weights=[0.]*42)
    native=dict(sample_id="functional_check",graph_release_id=meta["graph_release_id"],input_snapshot=query,
        query_cues=[],appraisal_dimensions=[],emotion_candidates=[],query_result_id="fixture")
    before=copy.deepcopy(native)
    assert repair.apply(native)==before and native==before
    assert repair.apply(native) is not native
    zero=repair.batch(np.zeros((1,42)),"balanced_gated")
    assert not zero["selected"].any() and not zero["app_gate"]["passed"].any()
    assert repair.apply(native,"balanced_gated")["fallback"]["required"]
    for malformed in [np.ones((1,41)),np.full((1,42),np.nan),-np.ones((1,42))]:
        try:repair.batch(malformed)
        except ValueError:pass
        else:raise AssertionError("Malformed query accepted")
    bad=copy.deepcopy(native);bad["graph_release_id"]="wrong"
    try:repair.apply(bad)
    except ValueError:pass
    else:raise AssertionError("Wrong graph accepted")
    # The first candidate must not grant support to a separate unsupported candidate.
    q=np.zeros((1,42));q[0,[0,15]]=1.
    support=np.zeros((1,42,2),bool)
    support[0,[0,15],0]=True;support[0,0,1]=True
    gate=candidate_gate(q,dict(score=np.array([[.5,.49]]),supporters=support),meta["gate"])
    assert gate["passed"].tolist()==[[True,False]]
    # Equal scores with independent per-candidate supports are not all rejected by a rank-1 gap.
    support[0,15,1]=True
    gate=candidate_gate(q,dict(score=np.array([[.5,.5]]),supporters=support),meta["gate"])
    assert gate["passed"].tolist()==[[True,True]]
    # A high prior with no Cue lift cannot generate an accepted Appraisal state.
    prior_only=np.tile(a["prior"],(1,1))
    conditional=np.tile(a["prior"],(42,1))
    out=app_support(q,prior_only,conditional,a["positive"],a["prior"],a["joint"],repair.groups,
        dict(meta["gate"],app_margin_thresholds=[0.]*6))
    assert not out["passed"].any()
    # Removing a modality must remove all its support; it cannot survive in a cached display list.
    missing=q.copy();missing[:,15:32]=0
    gate=candidate_gate(missing,dict(score=np.array([[.5,.5]]),
        supporters=support & (missing[:,:,None]>0)),meta["gate"])
    assert not gate["passed"].any()
    print(json.dumps(dict(status="PASS",checks=[
        "baseline pass-through and no mutation","zero-query fallback","invalid query rejection",
        "graph binding","candidate-specific support","equal-score candidates",
        "prior-only appraisal rejected","missing-modality support removed"]),ensure_ascii=False))
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--run",type=Path,required=True)
    run(parser.parse_args().run)
