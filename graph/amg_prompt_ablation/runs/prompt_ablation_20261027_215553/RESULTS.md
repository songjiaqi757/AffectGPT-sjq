# Frozen graph prompt ablation: MER2023 / SIMS / OV-MERD+
Two fixed weights; six prompt settings. No training. Same decoding, per-sample random seed and frozen gate.
E/F have the same retained semantic fields. All conditions omit explanation paths.
Exploratory target-test comparisons; no per-dataset prompt or checkpoint tuning.

|Weight|Condition|MER2023 HIT|MER2023 M|SIMS WAF|SIMS ACC|OV F|OV P|OV R|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|base35|A|70.817|50.115|86.179|86.082|61.405|61.772|61.190|
|base35|B|72.784|48.889|86.507|86.598|60.441|58.208|63.059|
|base35|C|72.339|47.804|85.716|85.825|60.757|58.029|64.045|
|base35|D|73.767|46.055|86.554|86.598|59.055|55.629|63.095|
|base35|E|73.971|44.191|84.512|84.536|59.103|54.349|64.936|
|base35|F|74.845|48.299|86.260|86.340|59.804|56.439|63.712|
|graph40|A|75.774|51.399|84.257|84.021|59.825|58.204|61.649|
|graph40|B|75.453|51.408|84.765|84.536|59.554|57.809|61.529|
|graph40|C|73.778|50.087|84.765|84.536|60.621|59.238|62.205|
|graph40|D|75.388|51.590|83.997|83.763|59.775|58.183|61.555|
|graph40|E|74.281|50.541|82.994|82.732|60.476|59.436|61.689|
|graph40|F|75.712|52.327|83.027|82.732|60.232|58.722|61.947|

## Paired metric changes

- base35 MER2023: B - A = +1.967 points
- base35 SIMS: B - A = +0.328 points
- base35 OVMERDPlus: B - A = -0.964 points
- base35 MER2023: C - B = -0.444 points
- base35 SIMS: C - B = -0.792 points
- base35 OVMERDPlus: C - B = +0.316 points
- base35 MER2023: D - B = +0.983 points
- base35 SIMS: D - B = +0.047 points
- base35 OVMERDPlus: D - B = -1.386 points
- base35 MER2023: E - C = +1.632 points
- base35 SIMS: E - C = -1.204 points
- base35 OVMERDPlus: E - C = -1.654 points
- base35 MER2023: E - D = +0.204 points
- base35 SIMS: E - D = -2.043 points
- base35 OVMERDPlus: E - D = +0.048 points
- base35 MER2023: F - E = +0.874 points
- base35 SIMS: F - E = +1.749 points
- base35 OVMERDPlus: F - E = +0.701 points
- graph40 MER2023: B - A = -0.321 points
- graph40 SIMS: B - A = +0.508 points
- graph40 OVMERDPlus: B - A = -0.271 points
- graph40 MER2023: C - B = -1.675 points
- graph40 SIMS: C - B = +0.000 points
- graph40 OVMERDPlus: C - B = +1.067 points
- graph40 MER2023: D - B = -0.066 points
- graph40 SIMS: D - B = -0.768 points
- graph40 OVMERDPlus: D - B = +0.221 points
- graph40 MER2023: E - C = +0.503 points
- graph40 SIMS: E - C = -1.771 points
- graph40 OVMERDPlus: E - C = -0.145 points
- graph40 MER2023: E - D = -1.107 points
- graph40 SIMS: E - D = -1.003 points
- graph40 OVMERDPlus: E - D = +0.701 points
- graph40 MER2023: F - E = +1.431 points
- graph40 SIMS: F - E = +0.033 points
- graph40 OVMERDPlus: F - E = -0.244 points
