#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  echo "DEEPSEEK_API_KEY is not set; skipping live check."
  exit 0
fi

python3 - <<'PY'
import json
import os
import urllib.request

payload = json.dumps(
    {
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "messages": [{"role": "user", "content": "Reply with exactly: DeepSeek OK"}],
        "max_tokens": 12,
        "temperature": 0,
    }
).encode("utf-8")

request = urllib.request.Request(
    os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/") + "/chat/completions",
    data=payload,
    method="POST",
    headers={
        "Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}",
        "Content-Type": "application/json",
    },
)

with urllib.request.urlopen(request, timeout=20) as response:
    body = json.loads(response.read().decode("utf-8"))
    print(body["choices"][0]["message"]["content"])
PY
