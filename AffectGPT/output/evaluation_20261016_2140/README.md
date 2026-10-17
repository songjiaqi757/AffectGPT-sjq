# Two-run evaluation queue

All work and artifacts stay on the server.

- Face run: physical GPU 0, epochs 30/35/40/45/50/55/60.
- Frame run: physical GPU 1, same seven epochs.
- Each GPU: 63 checkpoint/dataset combinations; three concurrent inference processes, then one scoring process.
- Verified test sizes: MER2023 411; MER2024 1169; MELD 2610; IEMOCAPFour 1241; CMUMOSI 686; CMUMOSEI 4659; SIMS 457; SIMSv2 1034; OVMERDPlus 532.
- Workload: 89593 sample passes per GPU. LPT static estimates: 29985 / 29834 / 29774 sample passes; the actual queue allocates dynamically based on worker completion.

## Pipeline

1. Three native inference_hybird.py subprocesses per GPU generate outputs. Each process handles one checkpoint and one dataset, then automatically claims the next job. Original prompts, sampling parameters, and generation limits are preserved.
2. After a GPU completes its own 63 generation tasks, it immediately starts one persistent Qwen/vLLM scoring worker to extract labels/polarity and call the original per-checkpoint metric functions. The two GPUs progress independently. Native resources and sampling parameters are preserved. Judge initialization uses the repository loader with all original vLLM defaults and no overrides.
3. Results for all seven checkpoints are written separately. No test-selected checkpoint replaces the full table.

Each GPU starts label extraction and scoring after its own generation queue and bounded recovery attempts finish. It does not wait for the other GPU. If a generation task fails after all retries, it is reported explicitly and only available outputs are scored; the final batch is marked ATTENTION rather than complete.

## Files

- checkpoint_cleanup.json: exact retained/deleted files and reclaimed bytes. The historical reference directory was not modified.
- plan.json: all 126 jobs, sample counts, paths, configurations, and known protocol limitations.
- state.json: current stage, per-job status, worker PIDs, and update time.
- events.jsonl: append-only task events.
- logs/face/raw and logs/frame/raw: per-job native inference logs.
- logs/{variant}/score_lane_*.log: scoring worker logs.
- face/results-* and frame/results-*: generated NPZ files and subsequent openset/sentiment caches.
- metrics/{variant}/epoch_*_{dataset}.json: complete per-job metrics.
- metrics_all.csv: all completed rows, scores on the 0..1 scale.
- per_checkpoint_summary.json: dataset-wise means only after all nine datasets for that checkpoint have scores.
- COMPLETED.json: written only when all 126 evaluations have metrics.
- ATTENTION.json: written if bounded retries leave any task incomplete.

## Resume and integrity

Generation and scoring skip completed valid artifacts. Each task has bounded retries; a serial recovery pass handles worker failure. Logs and state retain failures. A process lock prevents accidentally running a second controller for this batch. The native generator saves at dataset completion, so an interrupted unfinished dataset is regenerated.

## Protocol notes

Current repository wheel mappings, including the previously documented fear/fearless issue, are unchanged. The 99 train/OVMERDPlus duplicate videos are also unchanged. These results describe the current released-data protocol, not a newly deduplicated benchmark.

调度更新：每张 GPU 独立完成本卡全部 63 项推理后立即自动评测；两张卡之间不等待。

### Exact differences from the repository entry point

The native inference_hybird.py and evaluation.calculate_*_zeroshot functions are called without editing their source. Prompts, wheel resources, ground truth processing and SamplingParams are preserved. The wrapper changes task ordering, GPU masking, input checkpoint/config/output paths and result aggregation. Each checkpoint is recorded independently instead of returning only the test-set argmax from main_zeroshot_scores.

The judge is initialized by evaluation.func_read_batch_calling_model('Qwen25') directly. LLM(model=model_path), tokenizer and SamplingParams all use the repository code with no overrides. No explicit dtype, memory, KV-cache, context, batching, eager-mode, swap-space or seed settings are applied by this wrapper.

Concurrency update: inference remains three processes per GPU. Scoring uses exactly one judge process per GPU, with the unchanged repository loader and defaults. Each GPU switches independently after its own generation queue finishes.
