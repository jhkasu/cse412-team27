#!/usr/bin/env sh
set -eu

echo "Waiting for Postgres at ${PGHOST:-db}:${PGPORT:-5432}..."
until pg_isready -h "${PGHOST:-db}" -p "${PGPORT:-5432}" -U "${PGUSER:-postgres}" >/dev/null 2>&1; do
  sleep 1
done

echo "Postgres is ready. Preparing database..."
python setup_db.py

echo "Starting API server on port 5001..."
exec uvicorn app:app --host 0.0.0.0 --port 5001
