# OPPO + Cue/Appraisal/10-emotion graph results

All inference and official scoring complete: 12799 samples across 9 datasets.
Nine-dataset arithmetic mean: 81.2180%.

|Dataset|Metric|Paper values provided by user|OPPO + graph|Change (percentage points)|
|---|---|---:|---:|---:|
|CMUMOSI|WAF|86.50|83.88|-2.62|
|CMUMOSEI|WAF|84.63|84.03|-0.60|
|SIMS|WAF|86.22|88.35|+2.13|
|SIMSv2|WAF|88.26|87.71|-0.55|
|MER2023|HIT|87.73|88.25|+0.52|
|MER2024|HIT|90.34|91.12|+0.78|
|MELD|HIT|64.06|67.36|+3.30|
|IEMOCAPFour|HIT|73.60|75.38|+1.78|
|OVMERDPlus|F_s|67.16|64.88|-2.28|

The nine paper values supplied in chat average 80.9444%, while the separately supplied paper mean is 81.05%; these do not agree and need checking against the original table.
Compared numerically with the supplied reported mean 81.05, the graph run mean differs by +0.1680 percentage points. Compared with the arithmetic mean of the supplied nine entries, it differs by +0.2735.
No same-checkpoint, same-environment no-graph control has been run; differences from paper values do not isolate graph effects.
Official OPPO evaluation.py; answer_selection=full, use_answer_openset=True. Sentiment=WAF, basic emotion=HIT, open vocabulary=F_s.
Original OPPO source and weights unchanged.
