#!/usr/bin/env bash
set -euo pipefail

# Activate virtual environment
source "$(dirname "$0")/.venv/bin/activate"

if [[ -f .env ]]; then
  # shellcheck disable=SC2046
  export $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | xargs)
fi

exec mitmdump -s llm_capture_addon.py --listen-host 127.0.0.1 --listen-port 8080 --set block_global=false
