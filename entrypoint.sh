#!/bin/bash

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Now, run the FastAPI application using uvicorn
echo "Starting FastAPI application..."
exec "$@"
