#!/usr/bin/env bash
set -euo pipefail

log_file="${RUNNER_TEMP:-/tmp}/secure-coding-daphne.log"
python manage.py collectstatic --noinput
daphne -b 127.0.0.1 -p 8000 config.asgi:application >"${log_file}" 2>&1 &
server_pid=$!

cleanup() {
  kill "${server_pid}" 2>/dev/null || true
  wait "${server_pid}" 2>/dev/null || true
}
trap cleanup EXIT

for _ in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/ >/dev/null; then
    python e2e/core_journey.py
    exit 0
  fi
  sleep 1
done

cat "${log_file}"
exit 1
