# Trained Adapter attention: independent CPU audit

Uses all 500 real cached dev queries, fixed original normal/random neighbor IDs and the exact trained checkpoint.
No GPU, Qwen, generation, training, source modification, initial-weight reconstruction, or scoring changes.

|Mode|Logits neighbor std mean|Logits neighbor range max|FP64 max weight deviation from 0.2|Uniform token relative L2 mean|
|---|---:|---:|---:|---:|
|normal|2.0622918e-05|0.000183281983|2.45272052e-05|5.74789878e-07|
|random|2.812624e-05|0.000278914231|4.09805299e-05|8.35123489e-07|

All attention tensors have shape [500,4 heads,4 slots,5 neighbors]; softmax is over the last axis, masks retain all five, and heads are not averaged.
Manual Q/K input projection, scaled dot products and softmax match nn.MultiheadAttention; CPU weights also match the saved GPU diagnostic within reported numerical error.
FP64 recomputation distinguishes near uniform weights from exactly uniform weights. Original FP32 normalized entropy=1 is rounding at very small entropy deficit, not proof of exact equality.
The key projection bias cancels as a common softmax logit shift. Neighbor-centered key variation and query/head scale jointly bound the small logit differences.
The uniform-aggregation comparison measures the functional contribution of query-dependent attention at these fixed weights.
A minimal future selectivity test is a single logit-temperature change with all other factors fixed; no task gain follows from this audit.
See summary.json for geometry, FP64 entropy/KL, implementation error bounds and each mode's complete distributions.
