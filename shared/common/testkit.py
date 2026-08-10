from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import httpx

from shared.common.testing import load_module_from_path


def load_app(challenge_root: Path):
    os.environ.setdefault("LLM_PROVIDER", "mock")
    os.environ.setdefault("ADMIN_TOKEN", "local-admin")
    module = load_module_from_path(challenge_root / "app" / "backend" / "main.py")
    return module.app


async def make_client(challenge_root: Path) -> httpx.AsyncClient:
    app = load_app(challenge_root)
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


async def bootstrap(client: httpx.AsyncClient) -> dict[str, Any]:
    response = await client.get("/api/bootstrap")
    response.raise_for_status()
    return response.json()


async def run_actions(client: httpx.AsyncClient, actions: list[dict[str, Any]]) -> dict[str, Any]:
    last: dict[str, Any] = {}
    for action in actions:
        kind = action["kind"]
        if kind == "chat":
            response = await client.post("/api/chat", json={"message": action["message"], "request_id": action.get("request_id", "test")})
        elif kind == "post":
            response = await client.post(action["path"], json=action["json"])
        elif kind == "upload":
            files = {"file": (action["filename"], action["content"], "text/plain")}
            response = await client.post("/api/upload", files=files)
        else:
            raise ValueError(f"Unknown action kind: {kind}")
        response.raise_for_status()
        last = response.json()
    return last


def strip_volatile(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned = deepcopy(payload)
    cleaned.pop("session", None)
    return cleaned
