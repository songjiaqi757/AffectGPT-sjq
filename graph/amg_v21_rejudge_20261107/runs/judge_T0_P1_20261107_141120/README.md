# Greedy Qwen25 re-evaluation of unchanged AffectGPT predictions
Only the evaluation judge sampling settings change: temperature 0.7 -> 0; top_p 0.8 -> 1.
Model Qwen25, repetition_penalty 1.05, max_tokens 512, official evaluation functions, extraction prompts, label mappings and test memberships remain unchanged.
All 225 original raw prediction archives were checked byte-for-byte and every one of 319975 sample names was checked. New score_inputs folders contain only name2reason.npz; original openset/sentiment extraction caches were not copied.
A800 and A100 each run one persistent evaluator and claim exclusive dataset jobs from the shared queue. Supervisors recover worker exits and clean up only their own judge process groups. Transient shared-filesystem reads/writes use bounded retries.
Original prediction archives, extracted caches and all 225 original scores remain in the source run.
The nine original dataset-wise winning checkpoint/dataset pairs are prioritized to provide a fixed-checkpoint comparison first. Remaining jobs cover all 25 checkpoints x all nine datasets.
RESULTS.md and summary.json show both the mean with the original nine checkpoint choices fixed and the mean after reselecting dataset-wise winners over all 25 checkpoints. The latter is finalized only when all 225 jobs finish.
Inspect workers/A800.json, workers/A100.json, supervisor_A800.json, supervisor_A100.json, metrics_all.csv, paired_comparison_all.csv, fixed_original_winners_comparison.csv, best_by_dataset.csv and per_checkpoint_summary.csv.
All files and processes stay on the servers.
