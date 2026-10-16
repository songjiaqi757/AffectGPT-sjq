# Semantic Memory value ablation

Fixed AV retrieval, original attention scale; semantic texts from fit only. All four arms share the same 2816-d value Adapter, initialization, LoRA start, 4 tokens and 4002-exposure training budget.

|GPU/slot|Arm|
|---|---|
|0/0|AV-only (zero semantic dimensions)|
|0/1|AV + historical subtitles|
|1/0|AV + historical captions|
|1/1|AV + shuffled historical captions|

First cache frozen BGE-M3 CLS features on both GPUs (max_length256), then launch all four training arms. Every model receives retrieval/off/random scoring. Four same-checkpoint content interventions follow.

Fit4000/dev500, seed42, base already supervised all31327. All artifacts remain on server. No query target description/labels consumed online. Captions are lawful historical fit Memory values; self/group access and shuffled donor safety enforced.

State: state.json; logs: logs/; final results: SUMMARY.md. No automatic target/holdout, full31327 or graph expansion.
