#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -e '.[dev]'
else
  . .venv/bin/activate
fi

pytest -q
