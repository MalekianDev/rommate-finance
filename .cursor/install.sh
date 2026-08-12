#!/usr/bin/env bash
# Idempotent dependency refresh. Runs after the repository is checked out.
# Keeps only durable, source-derived setup here; runtime services and migrations
# live in ./.cursor/start.sh.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "install: Python environment ready."
