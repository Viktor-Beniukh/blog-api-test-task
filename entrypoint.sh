#!/bin/bash
# entrypoint.sh

# Stop the script when an error occurs
set -e

# Waiting for database availability
/wait-for-it.sh postgres 5432

# Running migrations
alembic upgrade head

# Running Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
