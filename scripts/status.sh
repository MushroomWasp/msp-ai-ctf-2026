#!/usr/bin/env bash
set -euo pipefail

proxy_port="${REVERSE_PROXY_PORT:-8180}"

docker compose ps
echo
echo "Proxy:     http://127.0.0.1:${proxy_port}/"
for port in {8101..8111}; do
  echo "Challenge: http://127.0.0.1:${port}/"
done
for port in {8112..8115}; do
  echo "Challenge: http://127.0.0.1:${port}/"
done
