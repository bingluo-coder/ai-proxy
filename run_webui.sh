#!/usr/bin/env bash
set -euo pipefail

# Activate virtual environment
source "$(dirname "$0")/.venv/bin/activate"

if [[ -f .env ]]; then
  # shellcheck disable=SC2046
  export $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | xargs)
fi

exec python3 webui.py
