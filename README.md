# Roommate Finance Bot

Shared expense tracker for roommates. Core domain logic (DB, repositories, services, schemas) is interface-agnostic; **Telegram** is the first client.



## Motivation

I started this project as a way to get back into software development after being away from technical work for several months due to the prolonged internet shutdowns in Iran.

During that time, software development continued to evolve rapidly. New AI-assisted development workflows and tools, including coding agents such as Cursor, became increasingly integrated into the software development lifecycle. Being disconnected from the internet meant that I had very little opportunity to experience these changes firsthand or incorporate them into my own development workflow.

After moving to Armenia, I decided to use this project as a practical way to bridge that gap.

At the same time, I needed a simple way to keep track of shared expenses with my roommate. Rather than building a one-off personal tool, I decided to turn it into a proper open-source project and use it as an opportunity to:

- Get back into hands-on software development and refresh technical knowledge I hadn't used recently.
- Revisit modern Python backend development through a real-world project.
- Explore how AI can be integrated into the software development lifecycle and my own development workflow.
- Experiment with AI-assisted development and natural-language expense entry using Gemini.
- Build something that solves a real problem in my day-to-day life.
- Add a complete, practical open-source project to my GitHub.

The goal isn't to build the most sophisticated expense tracker. Instead, this project is a practical way for me to get back to building software, catch up with changes in modern development practices, experiment with AI-assisted development, and learn by working on a real problem.

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