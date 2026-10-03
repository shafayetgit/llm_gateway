#!/bin/sh
set -e

# Run database migrations
python -m alembic upgrade head

# Seed / sync default models in PostgreSQL
python -m scripts.seed_models

# Start the FastAPI application
fastapi run --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips '*'
