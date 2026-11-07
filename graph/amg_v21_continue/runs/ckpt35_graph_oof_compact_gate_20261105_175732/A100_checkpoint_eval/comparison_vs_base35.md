# Five continuation checkpoints versus original checkpoint35

Same prior v2.1/P4 inputs; official three-dataset scores. Percentages. Mean is the simple equal-weight mean of MER HIT, SIMS WAF and OV F_s.

|Checkpoint|MER HIT|SIMS WAF|OV F_s|Three-metric mean|
|---:|---:|---:|---:|---:|
|35 baseline|71.7200|86.4292|57.8334|71.9942|
|36|74.0657|86.7224|61.9066|74.2316|
|37|74.5903|84.7267|60.7387|73.3519|
|38|75.4498|87.0115|61.3822|74.6145|
|39|75.0383|84.4493|60.9854|73.4910|
|40|75.9015|85.6847|63.6346|75.0736|

Best mean checkpoint: 40
Its deltas versus checkpoint35, percentage points: {"MER2023_HIT": 4.181495203776075, "SIMS_WAF": -0.7445449438378104, "OVMERDPlus_F_s": 5.801183188010994}

Three datasets only; checkpoint comparison uses exact prior v2.1/P4 prompts. Descriptive results, not an independent statistical confirmation.
