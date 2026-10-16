# Fixed-checkpoint Memory interventions

All variants use the same retrieval-trained checkpoint, seed 42 and 500 source dev clips.
Normal retrieval predictions were reused after hash validation; no retraining.

|Memory mode|micro-F1|sample macro-F1|Failed|
|---|---:|---:|---:|
|retrieval|0.460784|0.491463|0|
|off|0.463749|0.494842|0|
|random|0.460733|0.490860|0|

|Left minus right|micro-F1 delta|95% paired interval|Same label sets|
|---|---:|---|---:|
|random-vs-off|-0.003016|[-0.014260, 0.007775]|376/500|
|retrieval-vs-off|-0.002965|[-0.014405, 0.007193]|378/500|
|retrieval-vs-random|0.000051|[-0.004376, 0.004429]|491/500|

Intervals use 1,000 paired group bootstrap resamples; current group IDs are clip IDs.
These are source development normalized label-set scores, not paper EW or target scores.
Interpret with cpu-diagnostics/ and the separate five-method training experiment.
