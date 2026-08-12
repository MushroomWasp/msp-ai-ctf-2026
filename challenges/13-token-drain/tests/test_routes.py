from .config import CHALLENGE_ROOT
from shared.common.testkit import bootstrap, make_client, strip_volatile


async def test_index_and_bootstrap():
    async with await make_client(CHALLENGE_ROOT) as client:
        index = await client.get("/")
        assert index.status_code == 200
        payload = await bootstrap(client)
        assert payload["app"]["name"] == "Token Drain"
        assert payload["solved"] is False
        assert payload["total_tokens"] == 0


async def test_reset_restores_initial_state():
    async with await make_client(CHALLENGE_ROOT) as client:
        initial = strip_volatile(await bootstrap(client))
        await client.post("/api/chat", json={"message": "expand this", "request_id": "reset-check"})
        response = await client.post("/api/reset")
        assert response.status_code == 200
        after = strip_volatile(await bootstrap(client))
        assert after == initial
