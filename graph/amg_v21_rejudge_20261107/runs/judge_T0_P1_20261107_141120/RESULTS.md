# Re-evaluation with greedy Qwen25 judge

Frozen original AffectGPT predictions. Only judge temperature 0.7 -> 0 and top_p 0.8 -> 1 changed. Official metrics, prompts, repetition_penalty 1.05, max_tokens 512, labels and test memberships preserved.

Scored dataset jobs: 225/225.
Original dataset-wise best mean: 75.485540%.

New mean at the FIXED original nine winning checkpoints: 75.536508% (delta +0.050968 percentage points).
New dataset-wise reselected best mean after all 225 scores: 75.536508% (delta +0.050968 percentage points).

|Dataset|Metric|Original best (%)|New best (%)|New base -> epoch|Compared checkpoints|
|---|---|---:|---:|---|---:|
|MER2023|HIT|78.67|78.67|35 -> 40|25/25|
|MER2024|HIT|78.75|78.75|50 -> 55|25/25|
|MELD|HIT|58.34|58.34|40 -> 45|25/25|
|IEMOCAPFour|HIT|62.29|62.24|50 -> 55|25/25|
|CMUMOSI|WAF|82.42|82.57|50 -> 53|25/25|
|CMUMOSEI|WAF|79.74|79.76|35 -> 39|25/25|
|SIMS|WAF|88.93|88.93|45 -> 47|25/25|
|SIMSv2|WAF|86.40|86.73|35 -> 38|25/25|
|OVMERDPlus|F_s|63.86|63.86|40 -> 45|25/25|
