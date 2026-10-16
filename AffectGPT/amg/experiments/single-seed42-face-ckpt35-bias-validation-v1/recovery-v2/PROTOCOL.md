# Evaluation recovery v2

Both seed42 training arms are complete. The original pipeline stopped because
its off-mode validator iterated over the intentional retrieved_ids=null trace.
The one-line normalization fix changes validation only; model, training,
inference, decoding, budget and scoring sources remain unchanged.

Reuse both trained checkpoints, all complete normal predictions/reports and the
complete zero_init/off500 output. Preserve the partial control/off495 output as
failure evidence; generate a fresh complete500 in this directory. GPU0 runs
control/off then control/random; GPU1 runs zero_init/random. No training occurs.

Exact initial states and all4002 training exposures are revalidated before GPU
work. Completed predictions and metadata are fingerprinted; partial495 is never
silently scored as a complete run. Final paired scoring and SUMMARY.md contain
the same predeclared11 comparisons and exploratory decision rules.

All files remain on server. Original state.json/FAILURE.txt/READY.json are
preserved. Current progress is recovery-v2/state.json; completed output is
recovery-v2/SUMMARY.md and summary.json. End assistant turn after launch checks.
