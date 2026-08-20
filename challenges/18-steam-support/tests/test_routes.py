from .config import CHALLENGE_ROOT
from shared.common.testkit import bootstrap, make_client, strip_volatile


async def test_index_and_bootstrap():
    async with await make_client(CHALLENGE_ROOT) as client:
        index = await client.get("/")
        assert index.status_code == 200
        payload = await bootstrap(client)
        assert "profile" in payload or "app" in payload
        assert payload["solved"] is False


async def test_reset_restores_initial_state():
    async with await make_client(CHALLENGE_ROOT) as client:
        initial = strip_volatile(await bootstrap(client))
        await client.post("/api/chat", json={"message": "hello gamer", "request_id": "reset-check"})
        response = await client.post("/api/reset")
        assert response.status_code == 200
        after = strip_volatile((await bootstrap(client)))
        assert after == initial
