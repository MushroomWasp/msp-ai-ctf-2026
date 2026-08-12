from shared.common.testkit import bootstrap, make_client

from .cases import CASES


async def test_flag_is_not_exposed_trivially(case):
    async with await make_client(case["root"]) as client:
        index = await client.get("/")
        assert "MSP{" not in index.text
        assert case["expected_flag"] not in index.text
        payload = await bootstrap(client)
        assert payload["solved"] is False
        assert case["expected_flag"] not in str(payload)


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", CASES)
