from .config import CHALLENGE_ROOT
from shared.common.testkit import bootstrap, make_client


async def test_session_isolation():
    async with await make_client(CHALLENGE_ROOT) as client_a, await make_client(CHALLENGE_ROOT) as client_b:
        await client_a.post("/api/chat", json={"message": "yo 1v1 me", "request_id": "iso-1"})
        a_state = await bootstrap(client_a)
        b_state = await bootstrap(client_b)
        assert len(a_state["chat"]) == 2
        assert len(b_state["chat"]) == 0
