from .config import CHALLENGE_ROOT, EXPECTED_FLAG, SOLUTION
from shared.common.testkit import make_client, run_actions


async def test_solution_path_awards_flag():
    async with await make_client(CHALLENGE_ROOT) as client:
        result = await run_actions(client, SOLUTION)
        assert result["solved"] is True
        assert result["flag"] == EXPECTED_FLAG
