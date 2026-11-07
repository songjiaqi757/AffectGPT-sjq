# Fixed best checkpoint evaluation: repetition penalty 1.0

Exactly nine previously chosen dataset/checkpoint pairs. Raw predictions, physical GPU assignment, prompts, metrics and labels preserved. The only change from the previous greedy evaluation is repetition_penalty 1.05 -> 1.0.

Scored pairs: 9/9.
Original stochastic judge reference: 75.485540%.
Previous T0/P1 with RP1.05: 75.536508%.

Current T0/P1 with RP1.0: 75.397779% (delta -0.138729 percentage points vs RP1.05).

|Dataset|Metric|Base -> epoch|Previous RP1.05 (%)|New RP1.0 (%)|Delta (pp)|
|---|---|---|---:|---:|---:|
|MER2023|HIT|35 -> 40|78.67|78.67|+0.0000|
|MER2024|HIT|50 -> 55|78.75|78.72|-0.0226|
|MELD|HIT|40 -> 45|58.34|58.32|-0.0148|
|IEMOCAPFour|HIT|50 -> 55|62.24|62.24|+0.0000|
|CMUMOSI|WAF|50 -> 53|82.57|82.42|-0.1526|
|CMUMOSEI|WAF|35 -> 39|79.76|79.71|-0.0460|
|SIMS|WAF|45 -> 47|88.93|88.68|-0.2490|
|SIMSv2|WAF|35 -> 38|86.73|85.96|-0.7636|
|OVMERDPlus|F_s|40 -> 45|63.86|63.86|+0.0000|
