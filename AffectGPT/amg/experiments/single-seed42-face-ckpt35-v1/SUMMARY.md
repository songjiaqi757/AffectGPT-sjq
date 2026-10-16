# Single-seed M0 source development results

Seed 42; GPUs 0/1; fit 4000, dev 500; fixed final checkpoint.

Baseline: /ai/sjq/AffectGPT-sjq/AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230/checkpoint_000035_loss_0.723.pth
Baseline SHA256: 0d0fa91f579d2540bf321630aeb05b35c2c919bb792800813968fc8352870a4e

|Method|microF1|sample macroF1|Failed|Unmapped clips|Exposure|Covered IDs|Optimizer updates|
|---|---:|---:|---:|---:|---:|---:|---:|
|off|0.464437|0.498531|0|15|4002|4000|1332|
|retrieval|0.460784|0.491463|0|20|4002|4000|1332|
|learned|0.458374|0.489995|0|20|4002|4000|1332|
|current|0.459680|0.490651|0|21|4002|4000|1332|
|random|0.457031|0.488871|0|19|4002|4000|1332|

|Retrieval minus baseline|microF1 delta|95% paired group interval|Negative per-clip gain fraction|
|---|---:|---|---:|
|off|-0.003652|[-0.016927388962642585, 0.00811106883248151]|0.1160|
|random|0.003753|[-0.007781309050623002, 0.013899414227910753]|0.0640|
|current|0.001104|[-0.0038575782832435, 0.00579026541716112]|0.0160|
|learned|0.002410|[-0.0020472031843443744, 0.006777998603471411]|0.0200|

These source normalized open-label-set scores are exploratory and differ from paper EW.
Bootstrap describes sample uncertainty for this seed. The shared baseline had supervision on all 31K source clips.
Exposure alignment passed for requested IDs, actual IDs, task types and budgets. group_id is currently clip ID.
All prediction failures remain in the full dev denominator. Holdout and target sets remain unscored.
