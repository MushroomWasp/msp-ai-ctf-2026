from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from shared.common.http import get_or_set_session_id, with_rate_limit
from shared.common.logging import configure_logging
from shared.common.rate_limit import SessionRateLimiter
from shared.common.session_store import SQLiteSessionStore


class ChatRequest(BaseModel):
    message: str
    request_id: str | None = None


class UploadResponse(BaseModel):
    ok: bool
    filename: str


class ChallengeRuntime:
    def __init__(
        self,
        *,
        slug: str,
        title: str,
        data_dir: Path,
        frontend_dir: Path,
        build_initial_state: Callable[[], dict[str, Any]],
        bootstrap_payload: Callable[[dict[str, Any]], dict[str, Any]],
        handle_chat: Callable[[dict[str, Any], str], Awaitable[dict[str, Any]]],
        handle_upload: Callable[[dict[str, Any], UploadFile], Awaitable[dict[str, Any]]] | None = None,
        extra_routes: Callable[[FastAPI, SQLiteSessionStore], None] | None = None,
        admin_token: str = "local-admin",
        rate_limit_per_minute: int = 15,
        ) -> None:
        configure_logging()
        self.logger = logging.getLogger(slug)
        self.slug = slug
        self.title = title
        self.data_dir = Path(os.getenv("DATA_DIR", str(data_dir)))
        self.frontend_dir = frontend_dir
        self.build_initial_state = build_initial_state
        self.bootstrap_payload = bootstrap_payload
        self.handle_chat = handle_chat
        self.handle_upload = handle_upload
        self.extra_routes = extra_routes
        self.admin_token = admin_token
        self.store = SQLiteSessionStore(self.data_dir / f"{slug}.db")
        self.rate_limiter = SessionRateLimiter(rate_limit_per_minute, 60)
        self.inflight: dict[str, asyncio.Lock] = {}

    def _session_lock(self, session_id: str) -> asyncio.Lock:
        return self.inflight.setdefault(session_id, asyncio.Lock())

    async def _state_for(self, session_id: str) -> dict[str, Any]:
        state = await self.store.load(session_id)
        if state is None:
            state = self.build_initial_state()
            await self.store.save(session_id, state)
        return state

    def app(self) -> FastAPI:
        app = FastAPI(title=self.title)
        app.mount("/static", StaticFiles(directory=self.frontend_dir), name="static")

        @app.on_event("startup")
        async def startup() -> None:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            await self.store.init()

        @app.get("/")
        async def index() -> FileResponse:
            return FileResponse(self.frontend_dir / "index.html")

        @app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "ok", "challenge": self.slug}

        @app.get("/api/bootstrap")
        async def bootstrap(request: Request, response: Response) -> dict[str, Any]:
            session_id = get_or_set_session_id(request, response)
            state = await self._state_for(session_id)
            return {"session": session_id, **self.bootstrap_payload(state)}

        @app.post("/api/chat")
        async def chat(payload: ChatRequest, request: Request, response: Response) -> dict[str, Any]:
            session_id = get_or_set_session_id(request, response)

            async def run() -> dict[str, Any]:
                lock = self._session_lock(session_id)
                if lock.locked():
                    raise HTTPException(status_code=409, detail="A request is already running.")
                async with lock:
                    state = await self._state_for(session_id)
                    result = await self.handle_chat(state, payload.message)
                    await self.store.save(session_id, state)
                    usage = result.get("usage", {})
                    await self.store.record_usage(
                        session_id,
                        "/api/chat",
                        usage.get("input_tokens", 0),
                        usage.get("output_tokens", 0),
                        provider_errors=int(result.get("provider_error", False)),
                    )
                    return result

            return await with_rate_limit(self.rate_limiter, session_id, run)

        if self.handle_upload is not None:

            @app.post("/api/upload")
            async def upload(
                request: Request,
                response: Response,
                file: UploadFile = File(...),
            ) -> dict[str, Any]:
                session_id = get_or_set_session_id(request, response)
                state = await self._state_for(session_id)
                result = await self.handle_upload(state, file)
                await self.store.save(session_id, state)
                return result

        @app.post("/api/reset")
        async def reset(request: Request, response: Response) -> dict[str, Any]:
            session_id = get_or_set_session_id(request, response)
            state = self.build_initial_state()
            await self.store.save(session_id, state)
            return {"ok": True, "state": self.bootstrap_payload(state)}

        @app.get("/api/admin/usage")
        async def admin_usage(request: Request) -> dict[str, Any]:
            token = request.headers.get("x-admin-token", "")
            if token != self.admin_token:
                raise HTTPException(status_code=403, detail="Forbidden")
            return {"rows": await self.store.usage_summary()}

        if self.extra_routes:
            self.extra_routes(app, self.store)

        return app
