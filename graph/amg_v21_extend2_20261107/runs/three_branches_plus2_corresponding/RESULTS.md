# Two additional logical epochs; corresponding datasets only

Completed 10/10 dataset evaluations.

Frozen judge: temperature=0, top_p=1, repetition_penalty=1.05, max_tokens=512.

|Original branch|Parent|Added epoch|Dataset|Score (%)|Parent (%)|Change (pp)|
|---:|---:|---:|---|---:|---:|---:|
|35|40|41|MER2023|74.63|78.67|-4.04|
|35|40|42|MER2023|74.90|78.67|-3.77|
|40|45|46|MELD|54.69|58.34|-3.65|
|40|45|46|OVMERDPlus|62.56|63.86|-1.30|
|40|45|47|MELD|55.65|58.34|-2.69|
|40|45|47|OVMERDPlus|60.01|63.86|-3.84|
|50|55|56|IEMOCAPFour|57.99|62.24|-4.25|
|50|55|56|MER2024|74.75|78.75|-3.99|
|50|55|57|IEMOCAPFour|57.62|62.24|-4.62|
|50|55|57|MER2024|74.97|78.75|-3.78|

Previous dataset-wise best mean across nine datasets: 75.536508%.
Retained best mean including these new artifacts: 75.536508%.
Four datasets outside the assigned set keep their previous scores. Different dataset winners may use different checkpoints. New scores are single inference runs under the preserved stochastic generation settings.
