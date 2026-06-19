#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

# Use WEB_CONCURRENCY env var to scale workers (default 1 for SQLite safety)
WORKERS="${WEB_CONCURRENCY:-1}"

echo "Starting SkillBridge API with ${WORKERS} worker(s)..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WORKERS}"
