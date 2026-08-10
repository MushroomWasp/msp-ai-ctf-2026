from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from shared.deepseek.config import get_settings
from shared.deepseek.exceptions import (
    DeepSeekRateLimitError,
    DeepSeekResponseError,
    DeepSeekTemporaryError,
)
from shared.common.models import ChatMessage, CompletionResult, ToolCall


logger = logging.getLogger("deepseek")


@dataclass(slots=True)
class MockResponse:
    text: str
    tool_calls: list[ToolCall]
    usage: dict[str, int]


class DeepSeekClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = httpx.AsyncClient(
            base_url=self.settings.deepseek_base_url.rstrip("/"),
            timeout=self.settings.llm_timeout_seconds,
            headers={
                "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def complete(
        self,
        *,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 500,
        temperature: float | None = None,
        mock_handler: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CompletionResult:
        if self.settings.llm_provider == "mock":
            if mock_handler is None:
                raise DeepSeekResponseError("Mock provider requires a mock handler.")
            return await mock_handler(messages=messages, tools=tools or [], metadata=metadata or {})

        payload: dict[str, Any] = {
            "model": self.settings.deepseek_model,
            "messages": [message.model_dump(exclude_none=True) for message in messages],
            "max_tokens": max_tokens,
            "temperature": temperature if temperature is not None else self.settings.llm_temperature,
        }
        if tools:
            payload["tools"] = tools

        delay = 0.5
        for attempt in range(self.settings.llm_max_retries):
            try:
                response = await self._client.post("/chat/completions", json=payload)
                if response.status_code == 429:
                    raise DeepSeekRateLimitError(response.text)
                if response.status_code >= 500:
                    raise DeepSeekTemporaryError(response.text)
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]["message"]
                tool_calls = []
                for item in choice.get("tool_calls", []):
                    arguments = item.get("function", {}).get("arguments", "{}")
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments or "{}")
                    tool_calls.append(
                        ToolCall(
                            id=item["id"],
                            name=item["function"]["name"],
                            arguments=arguments,
                        )
                    )
                return CompletionResult(
                    text=choice.get("content") or "",
                    finish_reason=data["choices"][0].get("finish_reason", "stop"),
                    tool_calls=tool_calls,
                    usage=data.get("usage", {}),
                )
            except DeepSeekRateLimitError:
                raise
            except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError) as exc:
                if attempt == self.settings.llm_max_retries - 1:
                    raise DeepSeekResponseError(str(exc)) from exc
                logger.warning("Transient LLM error", extra={"extra_data": {"attempt": attempt + 1}})
                await asyncio.sleep(delay)
                delay *= 2
        raise DeepSeekTemporaryError("LLM request failed after retries.")
