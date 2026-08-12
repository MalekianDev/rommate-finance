#!/usr/bin/env bash
# Per-boot reconciliation: start PostgreSQL, ensure the app role/database exist,
# create a local .env if missing, and apply migrations. Idempotent and safe to
# re-run; it must terminate so the agent can proceed.
set -euo pipefail

cd "$(dirname "$0")/.."

# 1. Start the PostgreSQL cluster (tolerate an already-running cluster).
sudo pg_ctlcluster 16 main start 2>/dev/null || true

# 2. Wait for the server to accept connections.
for _ in $(seq 1 30); do
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

# 3. Ensure the app role password and database exist (idempotent).
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "ALTER USER postgres WITH PASSWORD 'postgres';"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='sample_db'" | grep -q 1; then
    sudo -u postgres createdb sample_db
fi

# 4. Provide local defaults via .env when absent. Real credentials supplied as
#    Cloud Agent Secrets are injected as environment variables and take
#    precedence over these placeholders (pydantic-settings reads env vars first).
if [ ! -f .env ]; then
    cat > .env <<'EOF'
debug_mode=False
bot_token=DUMMY_LOCAL_BOT_TOKEN
gemini_api_key=DUMMY_LOCAL_GEMINI_KEY
db_host=localhost
db_port=5432
db_user=postgres
db_password=postgres
db_name=sample_db
EOF
fi

# 5. Apply database migrations (idempotent; only unapplied revisions run).
./.venv/bin/alembic upgrade head

echo "start: PostgreSQL is up and migrations are applied."
