# Trained Memory Adapter sensitivity

500 real source-dev queries; the same trained retrieval adapter and fixed original normal/random neighbors.
No training, Qwen load, text generation, holdout or target evaluation.

Encoder replay uses CUDA FP16 autocast then FP32 pooling; Adapter computations use FP32.
Token comparison additionally reports the FP16 cast used at LLM insertion.

Recomputed ordered top-5 exactly matched: 500/500.
Replayed gate absolute error <= 1e-5: normal 500/500, random 500/500.

|Diagnostic|Mean|Median|P95|Maximum|
|---|---:|---:|---:|---:|
|tokens.float32.cosine|0.999237|0.999277|0.999582|0.999683|
|tokens.float32.relative_l2|0.0384502|0.0380083|0.0501978|0.0751727|
|tokens.float32.left_norm|8.2368|8.23676|8.24522|8.25379|
|tokens.float32.right_norm|8.23609|8.23618|8.24383|8.24752|
|tokens.float16_cast.cosine|0.999237|0.999277|0.999582|0.999682|
|tokens.float16_cast.relative_l2|0.0384516|0.0380133|0.0502037|0.0751825|
|tokens.float16_cast.max_abs|0.00981632|0.00951433|0.0134918|0.0194473|
|value_sets.raw_mean.cosine|0.966772|0.968176|0.980597|0.986005|
|value_sets.raw_mean.relative_l2|0.253149|0.250612|0.324039|0.378365|
|value_sets.projected_mean.cosine|0.999192|0.999239|0.999546|0.999656|
|value_sets.projected_mean.relative_l2|0.0397925|0.0390996|0.0513075|0.0667968|
|attention.normal.normalized_entropy_mean|1|1|1|1|
|attention.random.normalized_entropy_mean|1|1|1|1|
|attention.normal.max_weight_mean|0.200006|0.200006|0.200008|0.200011|
|attention.random.max_weight_mean|0.200008|0.200008|0.200011|0.200015|
|attention.normal.forward_token_max_abs_error|7.65063e-08|7.45058e-08|8.9407e-08|1.19209e-07|
|attention.random.forward_token_max_abs_error|7.64742e-08|7.45058e-08|8.9407e-08|1.19209e-07|
|query_condition.query_mlp_norm|0.551181|0.551165|0.554488|0.557267|
|query_condition.query_to_mean_slot_norm_ratio|1.74412|1.74408|1.75459|1.76338|
|query_condition.removed_q_fixed_gate.normal_vs_random.cosine|0.999237|0.999278|0.999582|0.999682|
|query_condition.removed_q_fixed_gate.normal_vs_random.relative_l2|0.0384501|0.0380083|0.0501978|0.0751726|
|query_condition.removed_q_fixed_gate.normal_vs_original.relative_l2|3.94839e-07|3.85087e-07|5.32963e-07|8.47733e-07|
|query_condition.removed_q_fixed_gate.random_vs_original.relative_l2|6.51557e-07|6.20501e-07|9.70278e-07|1.91061e-06|
|replay_fidelity.normal_gate_abs_error|0|0|0|0|
|replay_fidelity.random_gate_abs_error|0|0|0|0|
|gate|0.119998|0.119999|0.120069|0.120114|

The query-branch deletion removes only Q_MLP(query), preserving learned query slots and original gate.
These measurements describe internal sensitivity and numerical replay, not proof of a training cause or a performance gain.
See summary.json limitations and per-worker rows.jsonl / queries.pt for all 500 cases.
