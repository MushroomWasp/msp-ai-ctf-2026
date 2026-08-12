from shared.common.testkit import bootstrap, make_client, run_actions, strip_volatile

from .cases import CASES


async def test_sessions_are_isolated(case):
    async with await make_client(case["root"]) as client_a, await make_client(case["root"]) as client_b:
        before = strip_volatile(await bootstrap(client_b))
        await run_actions(client_a, case["solution"])
        after = strip_volatile(await bootstrap(client_b))
        assert after == before


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", CASES)
