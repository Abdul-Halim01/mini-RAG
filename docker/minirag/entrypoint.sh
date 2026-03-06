#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/models/db_schemas/minirag/
alembic upgrade head
cd /app

echo "Starting FastAPI server..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8001