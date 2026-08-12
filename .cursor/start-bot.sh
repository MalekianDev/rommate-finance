#!/usr/bin/env bash
# Runs the Telegram bot in a visible terminal. The live bot requires a real
# Telegram token (and a Gemini key for expense parsing). When no token secret is
# present, idle with guidance instead of crash-looping so the rest of the dev
# environment (Postgres, migrations, tests) stays usable.
set -euo pipefail

cd "$(dirname "$0")/.."

# Ensure PostgreSQL is up and migrations are applied before the app runs. This is
# idempotent and makes the dev database self-healing even if the boot-time start
# phase was skipped (e.g. when booting from a prebuilt snapshot).
./.cursor/start.sh

token="${BOT_TOKEN:-${bot_token:-}}"
if [ -z "$token" ]; then
    echo "[bot] No BOT_TOKEN secret detected."
    echo "[bot] The dev database, migrations, and tests are ready to use."
    echo "[bot] To run the live bot, add BOT_TOKEN and GEMINI_API_KEY in Cloud Agent"
    echo "[bot] Secrets, then restart this terminal."
    exec sleep infinity
fi

exec ./.venv/bin/python src/telegram/main.py
