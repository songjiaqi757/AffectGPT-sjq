# Reader validation

Two A800 80GB GPUs, two independent jobs per GPU. All files on this server.

Phase A: old/zero-init retrieval checkpoint x zero/bank-mean prefix, 4 x 500 source-dev inference. Reuse on/off/random references.

Phase B: scale1/50000 x retrieval/random training, four common zero-bias starts, seed42, 1334 iterations and 4002 exposures each. Every trained model then runs on/off/random inference and scoring.

State: state.json. Logs: logs/. Outputs: predictions/, training/, reports/. Final report: SUMMARY.md.

Base already supervised on all source31327. No automatic full-data/HGT expansion.
