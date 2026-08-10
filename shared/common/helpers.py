from __future__ import annotations

import re
import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile


SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def safe_filename(name: str) -> str:
    cleaned = SAFE_NAME_RE.sub("-", name).strip("-")
    return cleaned or "upload.txt"


def server_upload_name(original_name: str) -> str:
    suffix = Path(original_name).suffix.lower() or ".txt"
    return f"{secrets.token_hex(8)}{suffix}"


async def read_text_upload(file: UploadFile, *, max_bytes: int = 100_000) -> str:
    if (file.content_type or "text/plain") not in {"text/plain", "application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Unsupported upload type.")
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="Upload is too large.")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Uploads must be UTF-8 text.") from exc
