# Adapter layer and bias audit

500 saved real dev queries; CPU only; same trained retrieval Adapter; no model or score changes.

Forward replay error: {'normal_max_abs_error': 1.862645149230957e-07, 'random_max_abs_error': 1.9371509552001953e-07}

|Value stage|Normal/random mean cosine|Relative L2|Common energy over full bank|
|---|---:|---:|---:|
|input|0.96677226|0.253149|0.901252|
|linear1_no_bias|0.97237432|0.231809|0.915768|
|linear1_with_bias|0.98137057|0.190893|0.942183|
|gelu|0.98136634|0.190930|0.942198|
|linear2_no_bias|0.98274642|0.184657|0.945827|
|linear2_with_bias|0.99919176|0.039793|0.997440|

|Internal probe|Token cosine|Token relative L2|Normal max attention weight|
|---|---:|---:|---:|
|original|0.99923730|0.038450|0.200006|
|remove_value_second_linear_bias_only|0.98822170|0.151465|0.200006|
|remove_both_value_linear_biases|0.98402768|0.176229|0.200006|
|layernorm_attention_inputs|0.99920952|0.039136|0.204195|

These probes are mechanistic diagnostics; no generation quality or improvement is inferred.
All model/source weights remain unchanged. See summary.json for geometry, linear bias scales and limitations.
