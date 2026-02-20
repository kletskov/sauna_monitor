#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-}:src"
python -m sauna_monitor.main
