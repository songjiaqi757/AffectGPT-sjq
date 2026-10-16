#!/bin/bash
set -euo pipefail
cd /ai/sjq/AffectGPT-sjq/AffectGPT
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONUNBUFFERED=1
exec /ai/sjq/miniconda3/envs/vllm/bin/python -B -c 'import torch,runpy; torch.cuda.set_per_process_memory_fraction(0.12,0); runpy.run_module("amg.build_memory",run_name="__main__")' --config train_configs/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz.yaml --manifest amg/artifacts/manifests/fit.jsonl --output amg/artifacts/m0-bank-face-fit.pt --device cuda:0
