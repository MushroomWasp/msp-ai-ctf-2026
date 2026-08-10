from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite


class SQLiteSessionStore:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    route TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    provider_errors INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    async def load(self, session_id: str) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT state_json FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = await cursor.fetchone()
        if not row:
            return None
        return json.loads(row[0])

    async def save(self, session_id: str, state: dict[str, Any]) -> None:
        payload = json.dumps(state)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO sessions (session_id, state_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id)
                DO UPDATE SET state_json = excluded.state_json, updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, payload),
            )
            await db.commit()

    async def delete(self, session_id: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            await db.commit()

    async def record_usage(
        self,
        session_id: str,
        route: str,
        input_tokens: int,
        output_tokens: int,
        request_count: int = 1,
        provider_errors: int = 0,
    ) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO usage_metrics (
                    session_id,
                    route,
                    input_tokens,
                    output_tokens,
                    request_count,
                    provider_errors
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, route, input_tokens, output_tokens, request_count, provider_errors),
            )
            await db.commit()

    async def usage_summary(self) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT
                    session_id,
                    SUM(input_tokens) AS input_tokens,
                    SUM(output_tokens) AS output_tokens,
                    SUM(request_count) AS request_count,
                    SUM(provider_errors) AS provider_errors
                FROM usage_metrics
                GROUP BY session_id
                ORDER BY request_count DESC
                """
            )
            rows = await cursor.fetchall()
        return [dict(row) for row in rows]
