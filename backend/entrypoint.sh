#!/usr/bin/env bash
set -euo pipefail

wait_for_postgres() {
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
  until PGPASSWORD="${POSTGRES_PASSWORD}" pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -q; do
    sleep 1
  done
  echo "PostgreSQL is up."
}

wait_for_redis() {
  local host port
  host=$(python3 -c "from urllib.parse import urlparse; print(urlparse('${REDIS_URL}').hostname)")
  port=$(python3 -c "from urllib.parse import urlparse; print(urlparse('${REDIS_URL}').port or 6379)")
  echo "Waiting for Redis at ${host}:${port}..."
  until python3 -c "import socket; socket.create_connection(('${host}', ${port}), timeout=2)" 2>/dev/null; do
    sleep 1
  done
  echo "Redis is up."
}

wait_for_postgres
wait_for_redis

if [[ "$*" == *"gunicorn"* || "$*" == *"runserver"* ]]; then
  echo "Running database migrations..."
  python manage.py migrate --noinput

  if [[ "${DJANGO_SETTINGS_MODULE:-}" == *"production"* ]]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
  fi
fi

exec "$@"
