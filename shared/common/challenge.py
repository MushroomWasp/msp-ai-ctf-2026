from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from shared.common.http import get_client_ip, get_or_set_session_id, with_rate_limit
from shared.common.logging import configure_logging
from shared.common.rate_limit import SessionRateLimiter
from shared.common.session_store import SQLiteSessionStore

MAX_CHAT_MESSAGE_LENGTH = 6000
MAX_REQUEST_BODY_BYTES = 2_000_000


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_CHAT_MESSAGE_LENGTH)
    request_id: str | None = None


class UploadResponse(BaseModel):
    ok: bool
    filename: str


MISSION_HELPER_SCRIPT = """
<script>
(() => {
  if (window.MspCtfUi) return;

  const state = { shown: false, latest: null };

  function fallbackRequestId() {
    return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function requestId() {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
      return globalThis.crypto.randomUUID();
    }
    return fallbackRequestId();
  }

  function ensureUi() {
    if (document.getElementById("mspMissionOverlay")) return;

    const style = document.createElement("style");
    style.textContent = `
      body.msp-mission-open { overflow: hidden; }
      .msp-mission-fab {
        position: fixed;
        right: 18px;
        bottom: 18px;
        z-index: 60;
        width: auto !important;
        margin: 0 !important;
        border: 0 !important;
        border-radius: 999px !important;
        padding: 12px 16px !important;
        background: #111827 !important;
        color: #fff !important;
        box-shadow: 0 16px 42px rgba(15, 23, 42, 0.28);
        font: inherit;
        cursor: pointer;
      }
      .msp-mission-overlay {
        position: fixed;
        inset: 0;
        z-index: 70;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 20px;
        background: rgba(15, 23, 42, 0.48);
        backdrop-filter: blur(6px);
      }
      .msp-mission-overlay.show { display: flex; }
      .msp-mission-card {
        width: min(580px, 100%);
        background: #fff;
        color: #0f172a;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 28px 80px rgba(15, 23, 42, 0.26);
      }
      .msp-mission-kicker {
        margin: 0 0 8px;
        font-size: 0.8rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748b;
      }
      .msp-mission-card h2 {
        margin: 0 0 10px;
        font-size: 1.95rem;
        line-height: 1.08;
      }
      .msp-mission-brand {
        margin: 0 0 14px;
        color: #334155;
        line-height: 1.5;
      }
      .msp-mission-callout {
        margin: 0 0 16px;
        padding: 16px 18px;
        border-radius: 18px;
        border: 1px solid #dbe4f0;
        background: #f8fafc;
      }
      .msp-mission-callout strong {
        display: block;
        margin-bottom: 6px;
        color: #0f172a;
      }
      .msp-mission-callout p,
      .msp-mission-note {
        margin: 0;
        color: #334155;
        line-height: 1.6;
      }
      .msp-mission-note { margin-top: 16px; }
      .msp-mission-actions {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 22px;
      }
      .msp-mission-actions button {
        width: auto !important;
        margin: 0 !important;
        border: 0 !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        background: #0f172a !important;
        color: #fff !important;
        font: inherit;
        cursor: pointer;
      }
      @media (max-width: 640px) {
        .msp-mission-card { padding: 20px; border-radius: 20px; }
        .msp-mission-card h2 { font-size: 1.55rem; }
        .msp-mission-fab { right: 14px; bottom: 14px; }
      }
    `;
    document.head.appendChild(style);

    const fab = document.createElement("button");
    fab.id = "mspMissionFab";
    fab.type = "button";
    fab.className = "msp-mission-fab";
    fab.textContent = "Mission";
    fab.addEventListener("click", () => {
      if (state.latest) openMission(state.latest);
    });
    document.body.appendChild(fab);

    const overlay = document.createElement("div");
    overlay.id = "mspMissionOverlay";
    overlay.className = "msp-mission-overlay";
    overlay.innerHTML = `
      <div class="msp-mission-card" role="dialog" aria-modal="true" aria-labelledby="mspMissionTitle">
        <p class="msp-mission-kicker">Mission Briefing</p>
        <h2 id="mspMissionTitle"></h2>
        <p id="mspMissionBrand" class="msp-mission-brand"></p>
        <div class="msp-mission-callout">
          <strong>Objective</strong>
          <p id="mspMissionObjective"></p>
        </div>
        <p class="msp-mission-note">
          Use the in-app controls already on this page. When you trigger the vulnerable AI workflow successfully,
          the app will reveal the challenge flag.
        </p>
        <div class="msp-mission-actions">
          <button type="button" data-close-mission>Start Challenge</button>
        </div>
      </div>
    `;
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay || event.target.closest("[data-close-mission]")) {
        closeMission();
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMission();
    });
    document.body.appendChild(overlay);
  }

  function openMission(data) {
    state.latest = data;
    ensureUi();
    document.getElementById("mspMissionTitle").textContent = data?.app?.name || "Challenge";
    document.getElementById("mspMissionBrand").textContent = data?.app?.brand || "";
    document.getElementById("mspMissionObjective").textContent =
      data?.app?.objective || "Interact with the application until you can reach the protected target.";
    document.getElementById("mspMissionOverlay").classList.add("show");
    document.body.classList.add("msp-mission-open");
  }

  function closeMission() {
    const overlay = document.getElementById("mspMissionOverlay");
    if (overlay) overlay.classList.remove("show");
    document.body.classList.remove("msp-mission-open");
  }

  function updateMission(data, options = {}) {
    state.latest = data;
    ensureUi();
    if (options.force || !state.shown) {
      openMission(data);
      state.shown = true;
    }
  }

  window.MspCtfUi = {
    requestId,
    updateMission,
    openMission: () => state.latest && openMission(state.latest),
    closeMission,
  };
})();
</script>
""".strip()

CHAT_LIMIT_SCRIPT = f"""
<script>
(() => {{
  const LIMIT = {MAX_CHAT_MESSAGE_LENGTH};

  function wire() {{
    const textarea = document.getElementById("prompt");
    if (!textarea || textarea.dataset.mspLimitWired) return;
    textarea.dataset.mspLimitWired = "1";
    textarea.setAttribute("maxlength", String(LIMIT));

    const counter = document.createElement("div");
    counter.className = "msp-char-counter";
    counter.style.cssText = "font-size:0.78rem;color:#a4a6b6;text-align:right;margin-top:4px;";
    textarea.insertAdjacentElement("afterend", counter);

    function update() {{
      const len = textarea.value.length;
      counter.textContent = `${{len}} / ${{LIMIT}}`;
      counter.style.color = len >= LIMIT ? "#ff6b6b" : "#a4a6b6";
    }}
    textarea.addEventListener("input", update);
    update();
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", wire);
  }} else {{
    wire();
  }}
}})();
</script>
""".strip()


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

        @app.middleware("http")
        async def limit_body_size(request: Request, call_next):
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    too_large = int(content_length) > MAX_REQUEST_BODY_BYTES
                except ValueError:
                    too_large = False
                if too_large:
                    return JSONResponse({"detail": "Request body too large."}, status_code=413)
            return await call_next(request)

        @app.on_event("startup")
        async def startup() -> None:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            await self.store.init()

        @app.get("/")
        async def index() -> HTMLResponse:
            html = (self.frontend_dir / "index.html").read_text(encoding="utf-8")
            injected = f"{MISSION_HELPER_SCRIPT}\n{CHAT_LIMIT_SCRIPT}"
            if "</head>" in html:
                html = html.replace("</head>", f"{injected}\n</head>")
            elif "</body>" in html:
                html = html.replace("</body>", f"{injected}\n</body>")
            else:
                html = f"{html}\n{injected}"
            return HTMLResponse(html)

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
            client_ip = get_client_ip(request)

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

            return await with_rate_limit(self.rate_limiter, [session_id, client_ip], run)

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
