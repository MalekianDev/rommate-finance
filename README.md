# Roommate Finance Bot

Shared expense tracker for roommates. Core domain logic (DB, repositories, services, schemas) is interface-agnostic; **Telegram** is the first client.

## Features

- User registration via Telegram
- Room create / invite / join
- Natural-language expense entry (Gemini → structured draft)
- Confirm / cancel before save
- Split payments across room members

## Stack

- Python 3.14+
- aiogram 3 (Telegram)
- SQLAlchemy 2 + asyncpg / Alembic
- PostgreSQL 16
- Google Gemini (`google-genai`)
- Docker Compose

## Project layout

```text
src/
  db/             # models, connection, session context & etc.
  repositories/   # data access
  schemas/        # Pydantic DTOs
  services/       # domain / AI helpers
  telegram/       # Telegram interface (handlers, keyboards, FSM)
  settings.py
tests/            # mirrors src/ (unit tests with mocked session)
migrations/       # Alembic
requirements/
  prod.txt        # runtime
  dev.txt         # pytest, pre-commit
  all.txt         # prod + dev
```



## Configuration

Copy the sample env and fill in secrets:

```bash
cp sample.env .env
```


| Variable                              | Description                                    |
| ------------------------------------- | ---------------------------------------------- |
| `bot_token`                           | Telegram bot token                             |
| `gemini_api_key`                      | Gemini API key                                 |
| `db_host`                             | `localhost` locally; Compose overrides to `db` |
| `db_port`                             | Postgres port (default `5432`)                 |
| `db_user` / `db_password` / `db_name` | Database credentials                           |
| `debug_mode`                          | SQLAlchemy echo when `True`                    |




## Run with Docker (recommended)

Requires Docker Desktop (or another Docker engine) and a filled `.env`.

```bash
docker compose up --build
```

This starts:

1. **db** — Postgres (published on host **5433** by default so it does not clash with a local `:5432`)
2. **migrate** — `alembic upgrade head`
3. **telegram** — `python -m telegram.main`

App containers talk to Postgres on the Compose network as `db:5432`.

```bash
# different host port for Postgres
DB_PUBLISH_PORT=5434 docker compose up --build

# background
docker compose up --build -d

# logs / stop
docker compose logs -f telegram
docker compose down
```



### Adding another interface later

Use the same image and a new Compose service (example):

```yaml
api:
  <<: *app
  command: ["python", "-m", "api.main"]
  ports:
    - "8000:8000"
```



## Local development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements/all.txt
cp sample.env .env          # then edit values
```

Point `.env` at a local Postgres (`db_host=localhost`), then:

```bash
alembic upgrade head
PYTHONPATH=src python -m telegram.main
```

Optional pre-commit:

```bash
pre-commit install
```



## Tests

```bash
pip install -r requirements/all.txt
pytest
pytest -q tests/repositories/
pytest -s tests/repositories/test_account.py   # show prints
```

Repository tests mock the DB session and assert SQL/session usage; they do not hit a real database.

## License

[GNU GPL v3](LICENSE)