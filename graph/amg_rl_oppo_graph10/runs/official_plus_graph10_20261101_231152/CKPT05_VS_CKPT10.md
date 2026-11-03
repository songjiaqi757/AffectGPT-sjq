# AffectGPT-RL checkpoint 5 vs checkpoint 10, graph10

Both checkpoints: 12,799 samples across nine official test datasets, same frozen graph and evaluation protocol.

|Dataset|ckpt5|ckpt10|Delta (percentage points)|
|---|---:|---:|---:|
|CMUMOSI|76.20|68.60|-7.60|
|CMUMOSEI|71.64|70.73|-0.92|
|SIMS|86.12|84.70|-1.43|
|SIMSv2|83.22|82.78|-0.43|
|MER2023|77.73|81.42|+3.69|
|MER2024|87.32|87.43|+0.11|
|MELD|63.68|65.07|+1.39|
|IEMOCAPFour|75.52|74.21|-1.31|
|OVMERDPlus|61.76|62.20|+0.44|
|Mean|75.91|75.24|-0.67|

Mean = arithmetic mean of nine dataset main scores. Both are graph-enhanced; no matched no-graph control has been evaluated.
