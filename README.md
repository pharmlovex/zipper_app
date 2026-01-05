# Zipper App

A batch folder zipping service using Celery and Redis. Submit folders containing subfolders, and each subfolder gets zipped asynchronously by Celery workers.

## Architecture

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│   CLI   │────▶│  Redis  │◀────│  Worker  │
└─────────┘     └─────────┘     └──────────┘
                    ▲
                    │
              ┌─────────┐
              │ Flower  │ (monitoring)
              └─────────┘
```

- **CLI**: Typer-based command-line interface to submit zipping tasks
- **Redis**: Message broker and result backend for Celery
- **Worker**: Celery worker that processes zip tasks
- **Flower**: Web UI for monitoring Celery tasks (port 5555)

## Requirements

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Quick Start with Docker

### 1. Build the image

```bash
docker build -t ghcr.io/pharmlovex/zipper_app:latest .
```

### 2. Prepare directories

```bash
mkdir -p /path/to/input /path/to/output
chmod 777 /path/to/output  # Ensure worker can write
```

### 3. Update docker-compose.yml volumes

Edit `docker-compose.yml` to point to your directories:

```yaml
volumes:
  - /path/to/input:/app/to_zip
  - /path/to/output:/app/zipped_outputs
```

### 4. Start services

```bash
# Start Redis and Worker
docker compose up -d redis worker flower

```

### 5. Run the CLI

```bash
docker compose run --rm cli
```

Or with custom arguments:

```bash
docker compose run --rm cli zipper /app/to_zip --output-dir /app/zipped_outputs
```

## CLI Usage

```bash
# Show help
docker run --rm ghcr.io/pharmlovex/zipper_app:latest zipper --help

# Zip all subfolders in a directory
docker run --rm \
  -v /path/to/folders:/data \
  -v /path/to/output:/output \
  ghcr.io/pharmlovex/zipper_app:latest \
  zipper /data --output-dir /output
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output-dir` | `-o` | Directory where zipped files will be saved |
| `--help` | | Show help message |

## Monitoring with Flower

Access the Flower web UI at http://localhost:5555 to monitor:

- Active workers
- Task progress
- Task history
- Failed tasks

## Local Development

### Prerequisites

- [uv](https://github.com/astral-sh/uv) package manager
- Redis running locally

### Setup

```bash
# Install dependencies
uv sync

# Start Redis (or use Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Start a worker
uv run celery -A src.worker.celery_app.celery_app worker --loglevel=info

# Run the CLI
uv run zipper /path/to/folders --output-dir /path/to/output
```

## Project Structure

```
zipper_app/
├── src/
│   ├── worker/
│   │   ├── celery_app.py    # Celery configuration
│   │   └── tasks.py         # Zip task definition
│   └── zipper/
│       └── cli.py           # Typer CLI
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Redis result backend URL |

## License

MIT
