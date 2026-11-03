# G: Cue + explicit-alternative Appraisal; no Emotion candidates

Two frozen weights. Same graph, gate, decoding and per-sample random stream as A-F. Existing unified evaluation pipeline unchanged.
A-F values are read-only references from the completed experiment. G contains 1718 reused exact-prompt F answers and 1082 new answers.

|Weight|Condition|MER HIT|MER M|SIMS WAF|SIMS ACC|OV F|OV P|OV R|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|base35|A|70.817|50.115|86.179|86.082|61.405|61.772|61.190|
|base35|B|72.784|48.889|86.507|86.598|60.441|58.208|63.059|
|base35|C|72.339|47.804|85.716|85.825|60.757|58.029|64.045|
|base35|D|73.767|46.055|86.554|86.598|59.055|55.629|63.095|
|base35|E|73.971|44.191|84.512|84.536|59.103|54.349|64.936|
|base35|F|74.845|48.299|86.260|86.340|59.804|56.439|63.712|
|base35|G|72.452|48.038|86.482|86.598|60.358|58.258|62.807|
|graph40|A|75.774|51.399|84.257|84.021|59.825|58.204|61.649|
|graph40|B|75.453|51.408|84.765|84.536|59.554|57.809|61.529|
|graph40|C|73.778|50.087|84.765|84.536|60.621|59.238|62.205|
|graph40|D|75.388|51.590|83.997|83.763|59.775|58.183|61.555|
|graph40|E|74.281|50.541|82.994|82.732|60.476|59.436|61.689|
|graph40|F|75.712|52.327|83.027|82.732|60.232|58.722|61.947|
|graph40|G|75.526|51.710|83.017|82.732|60.714|59.054|62.584|

## Paired point differences

base35 MER2023 G-A: HIT +1.635, M -2.076
base35 MER2023 G-B: HIT -0.332, M -0.850
base35 MER2023 G-C: HIT +0.113, M +0.234
base35 MER2023 G-E: HIT -1.519, M +3.847
base35 MER2023 G-F: HIT -2.393, M -0.260
base35 OVMERDPlus G-A: F_s -1.047, P_s -3.513, R_s +1.617
base35 OVMERDPlus G-B: F_s -0.084, P_s +0.050, R_s -0.252
base35 OVMERDPlus G-C: F_s -0.399, P_s +0.229, R_s -1.238
base35 OVMERDPlus G-E: F_s +1.255, P_s +3.909, R_s -2.129
base35 OVMERDPlus G-F: F_s +0.554, P_s +1.819, R_s -0.905
base35 SIMS G-A: WAF +0.303, ACC +0.515
base35 SIMS G-B: WAF -0.025, ACC +0.000
base35 SIMS G-C: WAF +0.767, ACC +0.773
base35 SIMS G-E: WAF +1.971, ACC +2.062
base35 SIMS G-F: WAF +0.222, ACC +0.258
graph40 MER2023 G-A: HIT -0.248, M +0.311
graph40 MER2023 G-B: HIT +0.073, M +0.302
graph40 MER2023 G-C: HIT +1.748, M +1.623
graph40 MER2023 G-E: HIT +1.246, M +1.169
graph40 MER2023 G-F: HIT -0.186, M -0.617
graph40 OVMERDPlus G-A: F_s +0.888, P_s +0.850, R_s +0.935
graph40 OVMERDPlus G-B: F_s +1.159, P_s +1.245, R_s +1.055
graph40 OVMERDPlus G-C: F_s +0.093, P_s -0.184, R_s +0.379
graph40 OVMERDPlus G-E: F_s +0.238, P_s -0.382, R_s +0.895
graph40 OVMERDPlus G-F: F_s +0.482, P_s +0.333, R_s +0.637
graph40 SIMS G-A: WAF -1.241, ACC -1.289
graph40 SIMS G-B: WAF -1.748, ACC -1.804
graph40 SIMS G-C: WAF -1.748, ACC -1.804
graph40 SIMS G-E: WAF +0.023, ACC +0.000
graph40 SIMS G-F: WAF -0.010, ACC +0.000

Exploratory target-test results. Point differences do not establish uncertainty or multi-seed robustness. No parameter training, graph fitting or target-driven prompt adjustment.
