#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=/ai/sjq/AffectGPT-sjq/graph
cd "$(dirname "$0")/.."
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
if [ -f human_annotation/viewer.pid ] && kill -0 "$(cat human_annotation/viewer.pid)" 2>/dev/null; then
 echo "Human viewer already running, PID $(cat human_annotation/viewer.pid)"; exit 0
fi
nohup /ai/sjq/miniconda3/envs/vllm/bin/python -m uvicorn human_annotation.server:app --host 127.0.0.1 --port 8766 --no-access-log > human_annotation/viewer.log 2>&1 < /dev/null &
echo "$!" > human_annotation/viewer.pid
echo "Human annotation viewer started, PID $(cat human_annotation/viewer.pid), server loopback port 8766"
