from shared.common.testkit import make_client, run_actions

from .cases import CASES


async def test_solution_path_awards_flag(case):
    async with await make_client(case["root"]) as client:
        result = await run_actions(client, case["solution"])
        assert result["solved"] is True
        assert result["flag"] == case["expected_flag"]


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", CASES)
