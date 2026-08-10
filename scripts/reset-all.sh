#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
from urllib.request import Request, urlopen

for port in range(8101, 8111):
    req = Request(f"http://127.0.0.1:{port}/api/reset", method="POST")
    with urlopen(req, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
        print(f"{port}: reset={payload['ok']}")
PY
