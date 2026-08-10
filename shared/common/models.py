from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "developer", "user", "assistant", "tool"]
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    reasoning_content: str | None = None


class ToolSchema(BaseModel):
    type: Literal["function"] = "function"
    function: dict[str, Any]


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class CompletionResult(BaseModel):
    text: str = ""
    finish_reason: str = "stop"
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: dict[str, int] = Field(default_factory=dict)


@dataclass(slots=True)
class SessionEnvelope:
    session_id: str
    state: dict[str, Any]
    usage: dict[str, int] = field(default_factory=dict)
