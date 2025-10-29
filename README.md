# INVILSO Landing Queue Service# INVILSO Landing Queue Service



[![CI](https://github.com/invil/invilso-landing/actions/workflows/ci.yml/badge.svg)](https://github.com/invil/invilso-landing/actions/workflows/ci.yml)FastAPI application that serves the marketing landing page and enqueues contact requests to an ARQ/Redis worker that forwards them to Telegram via HTTPX.

![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

## Requirements

FastAPI application that powers the INVILSO marketing landing, renders templated pages, and enqueues contact requests to an ARQ/Redis worker which forwards them to Telegram via HTTPX. The project bundles all static assets locally, features an interactive hero terminal, and keeps the worker layer extensible through a small registry framework.- Python 3.10+

- [uv](https://docs.astral.sh/uv/) package manager

## Highlights- Redis 7+

- **FastAPI + Jinja2** application factory with shared templates, legal pages, and locally hosted Bootstrap/Font Awesome assets.- Docker & Docker Compose (optional, recommended)

- **Contact queueing pipeline** that validates submissions, pushes ARQ jobs, and posts to Telegram using async HTTPX.

- **Worker registry framework** (see `app/workers/`) that auto-registers jobs, lifecycle hooks, and names without boilerplate.## Configuration

- **Docker Compose stack** for the API, worker, and Redis based on uv-driven images.Provide the following environment variables (in a `.env` file or directly in the environment):

- **Tests with 100% coverage** enforced by `pytest` and `--cov-fail-under=100`.- `TELEGRAM_BOT_TOKEN`: Bot token used to call the Telegram Bot API.

- `TELEGRAM_CHAT_ID`: Destination chat ID that receives contact notifications.

## Architecture Overview- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD` (optional): Redis connection details.

- `app/factory.py` builds the FastAPI app, mounts static assets, and wires routers.

- `app/routers/pages.py` serves the landing and legal pages via templates under `app/templates/`.## Local Development

- `app/routers/contact.py` accepts contact submissions and enqueues the Telegram notification job.1. Install uv (once):

- `app/services/telegram.py` contains the ARQ job plus startup/shutdown hooks for the HTTP client and Redis connection.   ```bash

- `app/workers/registry.py` exposes decorators used by both the API and the worker (`app/worker.py`).   curl -LsSf https://astral.sh/uv/install.sh | sh

- Static assets (Bootstrap, Font Awesome, custom CSS, fonts) live in `static/` and can be offloaded to Nginx if desired.   ```

2. Sync dependencies (creates `.venv/`):

## Requirements   ```bash

- Python 3.10+   uv sync --dev

- [uv](https://docs.astral.sh/uv/) package manager   ```

- Redis 7+3. Launch the FastAPI server:

- Docker & Docker Compose (optional but recommended)   ```bash

   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

## Environment Variables   ```

Provide the following (via `.env` or the shell):4. Start a worker in another terminal:

   ```bash

- `TELEGRAM_BOT_TOKEN`: Telegram bot token used to post messages.   uv run arq app.worker.WorkerSettings

- `TELEGRAM_CHAT_ID`: Chat or channel receiving notifications.   ```

- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD` (optional): Redis connection details.5. Open `http://localhost:8000` to view the landing page served from `static/index.html`.



Tests stub these values automatically, but the running app/worker expect them.## Testing

`pytest` is configured to require 100% coverage:

## Local Development```bash

1. Install uv (one-time):uv run pytest

   ```bash```

   curl -LsSf https://astral.sh/uv/install.sh | shCoverage reports appear in the terminal; the run fails if coverage drops below 100%.

   ```

2. Sync dependencies and create `.venv/`:## Docker Compose

   ```bashA production-like stack is available:

   uv sync --dev```bash

   ```docker compose up --build

3. Start the API (hot reload enabled):```

   ```bashThis starts:

   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload- `app`: FastAPI + Uvicorn via uv (port `8000` exposed) with the static directory bind-mounted (read-only).

   ```- `worker`: ARQ worker (launched through uv) processing queued jobs.

4. Launch the ARQ worker in another terminal:- `redis`: Redis instance used by both services.

   ```bash

   uv run arq app.worker.WorkerSettingsAdjust the environment variables in `docker-compose.yml` or provide a `.env` file before starting the stack.

   ```

5. Open `http://localhost:8000` to explore the landing page, legal pages, and faux terminal.## Static Assets

Static files live in `static/` and are mounted into the container at `/app/static`. Configure your host Nginx to serve this directory directly if desired.

## Running Tests

`pytest` is configured to fail if coverage drops under 100%:## Extending Workers

```bashWorker logic is orchestrated by a lightweight framework in `app/workers/`:

uv run pytest- Jobs register themselves via `@registry.job()`.

```- Shared startup/shutdown hooks use `@registry.on_startup` and `@registry.on_shutdown`.

Coverage output is shown inline in the terminal.- `WorkerSettings.functions` is populated automatically from the registry; no extra boilerplate per job.



## Docker ComposeTo add a new worker job:

A production-like stack is provided:1. Create a module (e.g. `app/services/email.py`).

```bash2. Import the shared `registry` and decorate your lifecycle hooks and job handler.

docker compose up --build3. Ensure the module import is wired in `app/workers/__init__.py` so registration happens at startup.

```4. Enqueue the job from the API by asking the registry for its name: `registry.job_name(send_email)`. 

This launches:Additional worker modules follow the same pattern without touching the core infrastructure.

- `app`: FastAPI + Uvicorn serving the site and API on port `8000`.
- `worker`: ARQ worker consuming the same codebase.
- `redis`: Redis instance used by both services.

To rebuild from scratch:
```bash
docker compose down --volumes --remove-orphans
```
then run `docker compose up --build` again.

## Front-End Notes
- Templates live in `app/templates/`; `base.html` provides navigation/footer, while `home.html` and `legal.html` extend it.
- Static assets under `static/` are bundled locally so the site can run without external CDNs.
- The hero terminal features a sinusoidal typewriter effect and a sandboxed prompt with playful commands (`help`, `stack`, `projects`, `quote`, etc.).

## Worker Framework
Add new background jobs by:
1. Creating a module (for example `app/services/email.py`).
2. Decorating the job with `@registry.job()` and optional lifecycle hooks.
3. Importing the module in `app/workers/__init__.py` so registration occurs on startup.
4. Using `registry.job_name(your_job)` when enqueuing from the API.

The ARQ worker automatically loads all jobs registered with the framework.

## Continuous Integration
The GitHub Actions workflow (`.github/workflows/ci.yml`) checks out the code, installs uv, syncs dependencies, and runs `uv run pytest`. The CI badge above reflects the latest build status, and coverage remains at 100% thanks to the pytest threshold.

## Project Structure
```
app/
  config.py
  factory.py
  routers/
    contact.py
    pages.py
  services/telegram.py
  templates/
  workers/
main.py
static/
tests/
docker-compose.yml
Dockerfile
```

Happy hacking! Contributions, suggestions, or new worker ideas are always welcome.
