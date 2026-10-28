# AMG statistical graph — current engineering release

Current run: amg_edges_v2_restore_diagnostic_20261022
All computation and files remain on this server; this revision made no model calls.

The original 200 diagnostic_reserved members are restored. Only pseudo_train 27,679 contributes to node discovery, edge weights and joint support.
The unchanged pseudo_validation 3,076 selects the preregistered finite grid; gold_audit 300, diagnostic_reserved 200 and all target datasets are excluded from fitting.

- Nodes: 42 Cue + 6 AppraisalDimension + 16 AppraisalState + 188 Emotion = 252.
- Statistical edges: 1,048 (Cue→Appraisal 177; Cue→Emotion 670; Appraisal→Emotion 201).
- Fixed HAS_STATE edges: 16; total graph edges: 1,064.
- Candidate edges: 11,576; estimable: 10,977.
- Candidate two-hop paths: 3,209; admitted: 2,595.
- Validation-selected pair support: 20 groups; joint path support: 5 groups.
- Structural Teacher proxy Recall@1: 0.5268405413; Emotion Recall@5: 0.3351689648.

Weights are the 95% bootstrap NPMI lower bounds. Complete-family FDR precedes positive-support filtering.
The run README, frozen protocol and full candidate audits describe the 1,000 shared group bootstrap replicates, exact singleton-group permutation test and endpoint-specific eligibility.
These proxy scores are not Student deployment performance or human psychological accuracy. Human and original-source/near-duplicate audits remain pending.

Current pointer: runs/current.json. Full results: runs/amg_edges_v2_restore_diagnostic_20261022/.
Independent verification from project root:

    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m amg_graph.verify
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m amg_graph.verify_frozen_release

The input plan is frozen in manifest/source_graph_plan.md. 图构建.md v2.8 records current results separately.
The historical merged-200 run amg_edges_v1_20261022 is retained with its original data, frozen plan and declared code snapshots; it is not the current graph.
Migration audit: data_migrations/restore_diagnostic_20261022/.
