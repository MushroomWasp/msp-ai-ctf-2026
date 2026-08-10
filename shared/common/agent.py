from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from shared.common.models import ChatMessage, CompletionResult
from shared.deepseek.client import DeepSeekClient


ToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


async def run_tool_agent(
    *,
    client: DeepSeekClient,
    messages: list[ChatMessage],
    tools: list[dict[str, Any]],
    handlers: dict[str, ToolHandler],
    max_tokens: int = 500,
    mock_handler: Any | None = None,
    metadata: dict[str, Any] | None = None,
    max_rounds: int = 3,
) -> CompletionResult:
    working_messages = list(messages)
    for _ in range(max_rounds):
        completion = await client.complete(
            messages=working_messages,
            tools=tools,
            max_tokens=max_tokens,
            mock_handler=mock_handler,
            metadata=metadata,
        )
        if not completion.tool_calls:
            return completion
        assistant_content = completion.text or ""
        if assistant_content:
            working_messages.append(ChatMessage(role="assistant", content=assistant_content))
        for call in completion.tool_calls:
            handler = handlers[call.name]
            tool_result = await handler(call.arguments)
            working_messages.append(
                ChatMessage(
                    role="tool",
                    content=json.dumps(tool_result),
                    name=call.name,
                    tool_call_id=call.id,
                )
            )
    return CompletionResult(
        text="The assistant could not complete that workflow cleanly. Please try again.",
        finish_reason="max_rounds",
        usage={},
    )
