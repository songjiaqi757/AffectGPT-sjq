# development: fixed-weight, three-seed method comparison

All percentages are means across three fixed generation seeds. Primary selection score: equally weighted categorical HIT and OV F. Polarity WAF is a separate harm guard. Bootstrap resamples samples identically across seeds; it does not certify source independence or represent training-seed uncertainty.

|Checkpoint|Arm|HIT|M|Polarity WAF|ACC|OV F|OV P|OV R|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|original_epoch40|A|72.007|51.025|79.826|79.904|46.436|52.920|41.468|
|original_epoch40|B|69.841|45.559|78.153|78.821|44.997|49.575|41.313|
|original_epoch40|C|73.256|46.936|80.468|81.107|50.760|53.890|48.183|
|original_epoch40|S|73.040|46.955|80.105|80.866|51.418|54.487|49.008|
|original_epoch40|P|74.866|47.921|80.034|80.385|52.891|56.707|49.689|
|fixed_graph45_to54|A|76.532|50.851|82.630|82.792|52.103|57.500|47.829|
|fixed_graph45_to54|B|75.361|50.786|82.066|82.190|50.130|54.732|46.399|
|fixed_graph45_to54|C|73.781|48.678|80.690|80.746|50.140|55.061|46.170|
|fixed_graph45_to54|S|74.572|49.280|80.804|80.866|50.388|55.212|46.472|
|fixed_graph45_to54|P|74.021|48.710|80.400|80.505|50.690|55.771|46.574|

Per-class effects, corrected/harmed counts and paired intervals: paired_analysis.json.
Source/video/speaker mapping remains unavailable. Near-video search covered selected media only; near-duplicate training videos and undocumented pretraining exposure remain unverified.

Frozen candidate: fixed_graph45_to54 / A. Confirmation outcomes must not alter this selection.
