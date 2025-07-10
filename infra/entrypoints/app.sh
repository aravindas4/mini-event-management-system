#!/bin/bash
set -e

# Function to handle shutdown signals
shutdown() {
    echo "Received shutdown signal, stopping server..."
    if [ -n "$PID" ]; then
        kill -TERM "$PID" 2>/dev/null || true
        wait "$PID"
    fi
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import time
import sys
from sqlalchemy import create_engine
from config.database import db_settings

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(db_settings.primary.url())
        connection = engine.connect()
        connection.close()
        print('Database connection successful')
        break
    except Exception as e:
        retry_count += 1
        print(f'Database connection failed (attempt {retry_count}/{max_retries}): {e}')
        time.sleep(2)
else:
    print('Failed to connect to database after maximum retries')
    sys.exit(1)
"

# Run database migrations
echo "Running database migrations..."
python3.12 -m alembic upgrade head

echo "Starting uvicorn server..."
# Run uvicorn in background with proper logging
uvicorn main:app \
    --host "0.0.0.0" \
    --port "8000" \
    --log-level "${LOG_LEVEL:-info}" \
    --access-log 2>&1 | tee -a "${LOG_FILE:-/dev/stdout}" &

PID=$!

# Wait for the process
wait "$PID"