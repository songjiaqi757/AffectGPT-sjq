# confirmation: fixed-weight, three-seed method comparison

All percentages are means across three fixed generation seeds. Primary selection score: equally weighted categorical HIT and OV F. Polarity WAF is a separate harm guard. Bootstrap resamples samples identically across seeds; it does not certify source independence or represent training-seed uncertainty.

|Checkpoint|Arm|HIT|M|Polarity WAF|ACC|OV F|OV P|OV R|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|original_epoch40|A|70.637|48.279|82.779|82.818|49.642|54.812|45.592|
|original_epoch40|B|68.410|44.606|85.505|85.911|51.475|54.852|48.691|
|original_epoch40|C|74.003|47.071|84.719|85.223|54.923|58.100|52.415|
|original_epoch40|S|74.801|47.301|85.372|85.682|53.905|56.180|52.144|
|original_epoch40|P|73.417|46.083|83.931|84.078|53.158|55.097|51.537|
|fixed_graph45_to54|A|75.104|49.538|83.595|83.505|52.132|55.388|49.380|
|fixed_graph45_to54|B|74.823|49.617|83.208|83.162|50.436|54.490|47.060|
|fixed_graph45_to54|C|74.939|50.116|83.625|83.620|52.000|55.482|49.146|
|fixed_graph45_to54|S|74.798|49.776|83.347|83.276|51.831|55.485|48.889|
|fixed_graph45_to54|P|74.843|49.934|82.840|82.818|51.603|55.469|48.429|

Per-class effects, corrected/harmed counts and paired intervals: paired_analysis.json.
Source/video/speaker mapping remains unavailable. Near-video search covered selected media only; near-duplicate training videos and undocumented pretraining exposure remain unverified.

Decision: {"frozen_candidate": {"checkpoint": "fixed_graph45_to54", "condition": "A"}, "confirmation_passed": true, "adopt_provisionally": {"checkpoint": "fixed_graph45_to54", "condition": "A"}, "Appraisal_validated": false, "training_ready": false, "training_reason": "Original-source/speaker isolation remains unverified; current results support provisional inference-method choice only. No new graph/semantic supervision was independently validated.", "scope": "New sample/media-disjoint MER-only material, not source/speaker-independent validation or a new nine-benchmark claim.", "time_beijing": "2026-10-29T08:48:27.710393+08:00"}
