from shared.common.testkit import bootstrap, make_client, strip_volatile

from .cases import CASES


async def test_index_and_bootstrap(case):
    async with await make_client(case["root"]) as client:
        index = await client.get("/")
        assert index.status_code == 200
        payload = await bootstrap(client)
        assert "app" in payload
        assert "name" in payload["app"]
        assert payload["solved"] is False


async def test_reset_restores_initial_state(case):
    async with await make_client(case["root"]) as client:
        initial = strip_volatile(await bootstrap(client))
        await client.post("/api/chat", json={"message": "hello", "request_id": "reset-check"})
        response = await client.post("/api/reset")
        assert response.status_code == 200
        after = strip_volatile(await bootstrap(client))
        assert after == initial


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", CASES)
