# G extension

Only G is new: Cue plus F-style alternative Appraisal, no Emotion candidates or paths.
Two fixed weights and three datasets, 6 scored jobs / 2800 merged answers,1718 exact-prompt F answers reused and1082 fresh.
Same per-sample seed,media,graph,gate,decode and unified evaluator.
Two A800 GPUs,4 inference processes per GPU,exclusive64-sample shards;all inference exits before one judge per GPU.
No training; source A-F records are read-only references.
