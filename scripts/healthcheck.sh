#!/usr/bin/env bash
set -euo pipefail

proxy_port="${REVERSE_PROXY_PORT:-8180}"

PROXY_PORT="$proxy_port" python3 - <<'PY'
import os
from urllib.request import urlopen

targets = {
    "proxy": f"http://127.0.0.1:{os.environ['PROXY_PORT']}/health",
    "01": "http://127.0.0.1:8101/health",
    "02": "http://127.0.0.1:8102/health",
    "03": "http://127.0.0.1:8103/health",
    "04": "http://127.0.0.1:8104/health",
    "05": "http://127.0.0.1:8105/health",
    "06": "http://127.0.0.1:8106/health",
    "07": "http://127.0.0.1:8107/health",
    "08": "http://127.0.0.1:8108/health",
    "09": "http://127.0.0.1:8109/health",
    "10": "http://127.0.0.1:8110/health",
    "11": "http://127.0.0.1:8111/health",
    "12": "http://127.0.0.1:8112/health",
    "13": "http://127.0.0.1:8113/health",
    "14": "http://127.0.0.1:8114/health",
    "15": "http://127.0.0.1:8115/health"
}
for name, url in targets.items():
    with urlopen(url, timeout=5) as response:
        body = response.read().decode("utf-8").strip()
        print(f"{name}: {response.status} {body}")
PY
