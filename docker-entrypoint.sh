#!/bin/bash
set -e

echo "Waiting for database to be ready..."

# Wait for MySQL to be ready
# Using the DATABASE_URL from environment or construct from individual vars
DB_USER="${MYSQL_USER:-hr_user}"
DB_PASS="${MYSQL_PASSWORD:-abc123}"
DB_NAME="${MYSQL_DATABASE:-employees}"
DB_HOST="${MYSQL_HOST:-mysql}"

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if python3 -c "
import pymysql
import sys
try:
    conn = pymysql.connect(
        host='$DB_HOST',
        user='$DB_USER',
        password='$DB_PASS',
        database='$DB_NAME',
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        echo "Database is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "Waiting for MySQL... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Failed to connect to MySQL after $max_attempts attempts"
    exit 1
fi

echo "Creating database tables if they don't exist..."
# Import models to register them with Base.metadata, then create tables
python3 -c "from app.db import Base, engine; import app.models; Base.metadata.create_all(bind=engine); print('Tables created successfully')" || {
    echo "WARNING: Failed to create tables (might already exist)"
}

echo "Running backfill scripts..."

# Run backfill scripts (they are idempotent - safe to re-run)
echo "Running backfill_auth_users..."
python3 -m scripts.backfill_auth_users 2>&1 || {
    echo "WARNING: backfill_auth_users failed (might already be populated)"
}

echo "Running backfill_leave_quotas..."
python3 -m scripts.backfill_leave_quotas 2>&1 || {
    echo "WARNING: backfill_leave_quotas failed (might already be populated)"
}

echo "Backfill scripts execution completed."

echo "Backfill scripts completed. Starting API server..."

# Start the API server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

