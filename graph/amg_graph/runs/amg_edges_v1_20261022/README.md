# AMG statistical graph — engineering release

## 方案文档修订后的历史产物核验

当前图构建.md已更新为v2.7实施记录；原建图所用v2.6内容保存在manifest/source_graph_plan_v2_6.md，
原图协议和所有边/路径文件未修改。原输入指纹中的图构建.md指的是该历史版本。
文档修订后复核当前冻结产物请运行：

    PYTHONDONTWRITEBYTECODE=1 python -m amg_graph.verify_frozen_release

该命令显式核验历史方案SHA、当前文档修订记录、原声明代码指纹、全部图文件、
其他源输入及30,955条选定Appraisal记录摘要；不会把当前文档伪装成历史输入。
原verify.py对应建图当时的完整统计复算，结果仍保存在manifest/verification.json。
本次文档修订核验保存在manifest/document_revision_verification.json。


Release: amg_edges_v1_20261022
All computation and files are on this server. No model calls were made.

## Result
- Nodes: 42 Cue + 6 AppraisalDimension + 16 AppraisalState + 188 Emotion = 252.
- Statistical edges: 1,047 (Cue→Appraisal 176; Cue→Emotion 670; Appraisal→Emotion 201).
- Fixed HAS_STATE edges: 16; total graph edges including ontology: 1,063.
- Evaluated candidate edges: 11,576; estimable hypotheses: 10,982.
- Candidate two-hop paths with both edges admitted: 3,186; admitted paths: 2,785.
- Selected minimum pair support: 20 source groups; selected joint path support: 3 source groups.

## Data and boundaries
Only the current pseudo_train 27,879 rows contribute to all edge and joint-path counts.
The same existing pseudo_validation 3,076 IDs select the finite grid; gold_audit 300 and nine target datasets are excluded.
Source release and all fingerprints: manifest/protocol.json.
Emotion remains the 188 fine-grained case2 concepts. The conversation-authorized exact AffectGPT alphabetical choice/drop policy overrides the earlier semantic-review recommendation in 图构建.md §3.3.6; no new aliases or 6/7-class collapse were added.
Every edge has its own two-endpoint eligibility mask. Cue uncertain/unobservable, invalid Appraisal, and unsuccessful/OOV Emotion sets do not become negative observations.
Emotion absence is absence from the normalized source-description labels, not a psychological negative.

## Statistics
The current manifest has one training sample per source_group_id. Thus per-eligible-group weights equal 1.
This build fails closed if a future release contains multi-sample groups; it does not silently use sample-level permutation on such groups.
Smoothed 2×2 NPMI uses 0.5 in each cell. A shared set of 1,000 global train-group multinomial bootstrap resamples yields percentile 95% intervals and within-source/relation rank/top-5 stability.
All estimable hypotheses, including low-positive-support ones, enter the one-sided exact fixed-marginal permutation family (hypergeometric/Fisher upper tail); BH is applied separately to the complete family of each of the three relations.
Support filtering follows FDR. Admitted edges require support≥20, CI lower bound>0, q<0.05, and ≥950 nondegenerate bootstrap replicates.
Weight is the CI lower bound. Missing edges indicate insufficient evidence and are not negative edges.
For paths, the same train sample must contain all three positive annotations. Each source group contributes at most once.
Path bootstrap support counts unique original groups present in the resample, rather than counting repeated draws as additional independent original groups.

## Validation choice
The preregistered 12-point grid is min_support∈{5,10,20} × joint_support∈{0,1,3,5}.
Structural queries are held-out Cue Teacher positive flags; objective is the mean of macro Appraisal state Recall@1 and sample-macro Emotion Recall@5; λ=0.5 and K=5 are fixed for this structural comparison.
Ties favor larger support thresholds. Paths with zero joint support never enter the main graph.
Selected structural proxy scores: Appraisal macro state Recall@1=0.52828049; Emotion sample-macro Recall@5=0.33579098.
These scores are not Cue Student deployment performance or human psychological accuracy.
Existing validation.last probability files do not all match the corresponding best checkpoints, so they were not relabeled or mixed as best-model predictions.
Cue Student evidence/coverage thresholds, calibration, active/deferred decisions and final inference tuning remain separate follow-up work.

## Audit status
This is an engineering graph pending original-source/near-duplicate and human audits. Distinct manifest IDs do not prove independent original-video sources.
Human appraisal gold labels have not been supplied; no human agreement or causal claim is made.

## Files
- graph/graph.json: nodes, admitted statistical edges and fixed ontology relations.
- graph/edges_cue_appraisal.csv, edges_cue_emotion.csv, edges_appraisal_emotion.csv.
- graph/edges_has_state.csv and nodes_*.csv.
- graph/candidate_edge_audit.parquet and .csv: every candidate, tables, eligibility hashes, p/q values, confidence intervals, ranks and exclusion reasons.
- graph/candidate_path_audit.csv: all supported-edge paths including zero-joint-support rejected paths.
- graph/paths_cue_appraisal_emotion.csv: admitted paths and bootstrap support stability.
- edges_support_5.csv, edges_support_10.csv, edges_support_20.csv: finite grid alternatives.
- validation/grid_results.json: all 12 validation settings and the deterministic selection.
- bootstrap_npmi.npz: all 1,000×11,576 bootstrap NPMI values.
- train_joint_support.npz: the full 42×16×188 train-only joint count tensor.
- manifest/protocol.json, input_fingerprints.json, sample_roles.json, graph_build_report.json, verification.json.
- runs/current.json (parent directory): current frozen engineering release pointer.

## Verification
Seven statistical unit checks passed. Independent verification recomputed every candidate table and every path count, checked all full-family q values against SciPy, compared 140 exact tests to Fisher, verified all bootstrap intervals, positive weights, IDs, source hashes and split separation.
Run from /ai/sjq/AffectGPT-sjq:
    PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=8 python -m amg_graph.verify
    python -m unittest discover -s amg_graph/tests -v
The builder refuses to overwrite an existing frozen run.

References:
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html
- https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.multinomial.html
