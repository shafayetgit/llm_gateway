#!/bin/sh
set -e

# Run database migrations
python -m alembic upgrade head

# Start the FastAPI application
fastapi run --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips '*'
