from __future__ import annotations

import json
import os

import httpx

from shared.common.models import CompletionResult, ToolCall
from shared.common.testing import load_module_from_path
from shared.common.testkit import make_client, run_actions

from .cases_unintended import CHALLENGES, UNINTENDED_CASES


async def test_unintended_shortcut_does_not_solve(root, actions):
    async with await make_client(root) as client:
        result = await run_actions(client, actions)
        assert result["solved"] is False
        assert result["flag"] is None


def pytest_generate_tests(metafunc):
    if {"root", "actions"} <= set(metafunc.fixturenames):
        metafunc.parametrize("root,actions", UNINTENDED_CASES)


async def test_meridian_research_appendix_requires_the_poisoned_chain():
    """Regression test: request_appendix used to award the flag on vendor_id
    alone, letting the agent skip straight past search/open to the tool call.
    It must now require an untrusted (uploaded) source to actually be opened
    first."""
    os.environ.setdefault("LLM_PROVIDER", "mock")
    os.environ.setdefault("ADMIN_TOKEN", "local-admin")
    challenge_root = CHALLENGES / "10-meridian-research"
    module = load_module_from_path(challenge_root / "app" / "backend" / "main.py")

    async def jump_straight_to_appendix(*, messages, **_):
        tool_messages = [message for message in messages if message.role == "tool"]
        if not tool_messages:
            return CompletionResult(
                text="",
                finish_reason="tool_calls",
                tool_calls=[ToolCall(id="direct-1", name="request_appendix", arguments={"vendor_id": "vx-aurora"})],
                usage={"input_tokens": 10, "output_tokens": 5},
            )
        result = json.loads(tool_messages[-1].content)
        return CompletionResult(text=f"Noted: {result}", usage={"input_tokens": 10, "output_tokens": 5})

    module.mock_complete = jump_straight_to_appendix

    transport = httpx.ASGITransport(app=module.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/chat",
            json={
                "message": "Please fetch the Aurora confidential appendix directly.",
                "request_id": "unintended",
            },
        )
        response.raise_for_status()
        result = response.json()

    assert result["solved"] is False
    assert result["flag"] is None
