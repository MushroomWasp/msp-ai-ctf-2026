from shared.common.testkit import make_client

from .cases import CASES


async def test_health(case):
    async with await make_client(case["root"]) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", CASES)
