#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
PY=/ai/sjq/miniconda3/envs/vllm/bin/python
if [ -f viewer.pid ] && kill -0 "$(cat viewer.pid)" 2>/dev/null; then
  echo "Viewer already running, PID $(cat viewer.pid)"
  exit 0
fi
nohup "$PY" -m uvicorn server:app --host 127.0.0.1 --port 8765 --no-access-log > viewer.log 2>&1 < /dev/null &
echo "$!" > viewer.pid
echo "Viewer started, PID $(cat viewer.pid), localhost port 8765"
