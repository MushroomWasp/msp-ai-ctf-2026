from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Request, Response


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def get_or_set_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get("ctf_session")
    if session_id:
        return session_id
    session_id = secrets.token_urlsafe(18)
    response.set_cookie(
        "ctf_session",
        session_id,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 8,
    )
    return session_id


async def with_rate_limit(
    limiter: Any,
    keys: str | list[str],
    handler: Callable[[], Awaitable[Any]],
) -> Any:
    key_list = [keys] if isinstance(keys, str) else keys
    if not await limiter.allow_all(key_list):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and retry.")
    return await handler()
