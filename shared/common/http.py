from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Request, Response


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
    session_id: str,
    handler: Callable[[], Awaitable[Any]],
) -> Any:
    if not await limiter.allow(session_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and retry.")
    return await handler()
