# Bias validation: single seed 42

Source development only; the shared baseline already saw all source clips.
Stage A clears a learned bias at inference and is an out-of-distribution mechanism probe.
Stage B compares fresh matched Adapter starts; it does not reproduce the old unsaved initialization.
Zero initialization keeps the bias trainable. Final inference preserves learned biases.

| Run | Micro F1 | Sample macro F1 | Failed / 500 |
|---|---:|---:|---:|
| stage-a-zero-retrieval | 0.458674 | 0.489014 | 0 |
| stage-b-zero_init-retrieval | 0.463550 | 0.493905 | 0 |
| ref-random | 0.460733 | 0.490860 | 0 |
| ref-off | 0.463749 | 0.494842 | 0 |
| stage-a-zero-random | 0.457721 | 0.488442 | 0 |
| stage-b-control-retrieval | 0.459177 | 0.491382 | 0 |
| ref-off_trained | 0.464437 | 0.498531 | 0 |
| ref-normal | 0.460784 | 0.491463 | 0 |
| stage-b-zero_init-off | 0.466102 | 0.497181 | 0 |
| stage-b-control-off | 0.465298 | 0.496484 | 0 |
| stage-b-zero_init-random | 0.462292 | 0.492936 | 0 |
| stage-b-control-random | 0.460183 | 0.492620 | 0 |

| Comparison (current minus reference) | Micro F1 delta | Paired 95% CI |
|---|---:|---|
| stage-a-zero-retrieval-vs-ref-off | -0.005076 | [-0.016283, +0.004939] |
| stage-a-zero-retrieval-vs-stage-a-zero-random | +0.000952 | [-0.000141, +0.002820] |
| stage-a-zero-random-vs-ref-random | -0.003012 | [-0.007711, +0.001539] |
| stage-a-zero-retrieval-vs-ref-normal | -0.002111 | [-0.006293, +0.001823] |
| stage-b-zero_init-retrieval-vs-stage-b-control-retrieval | +0.004373 | [-0.000724, +0.010020] |
| stage-b-zero_init-retrieval-vs-ref-off_trained | -0.000886 | [-0.013134, +0.010478] |
| stage-b-control-retrieval-vs-ref-normal | -0.001607 | [-0.006537, +0.002966] |
| stage-b-control-retrieval-vs-stage-b-control-off | -0.006121 | [-0.016034, +0.003610] |
| stage-b-control-retrieval-vs-stage-b-control-random | -0.001006 | [-0.002664, +0.000000] |
| stage-b-zero_init-retrieval-vs-stage-b-zero_init-off | -0.002552 | [-0.012040, +0.007354] |
| stage-b-zero_init-retrieval-vs-stage-b-zero_init-random | +0.001258 | [+0.000145, +0.002993] |

Decision flags: {"zero_init_vs_control_positive_95ci": false, "zero_init_vs_control_gain_at_least_preset": false, "all_new_predictions_without_errors": true, "zero_init_retrieval_beats_off_95ci": false, "zero_init_retrieval_beats_random_95ci": true}
do_not_expand_graph_or_training_budget_on_this_evidence

These intervals measure sample uncertainty for this seed, not training-seed variability.
No heldout or target evaluation, full-data training, graph model or multi-seed jobs are scheduled.
