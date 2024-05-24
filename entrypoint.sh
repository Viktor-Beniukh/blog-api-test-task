#!/bin/bash
# entrypoint.sh

# Stop the script when an error occurs
set -e

# Waiting for database availability
/wait-for-it.sh postgres 5432

# Running migrations
alembic upgrade head

# Running your script to add data to the database
python /code/add_data_to_db.py

# Running Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
