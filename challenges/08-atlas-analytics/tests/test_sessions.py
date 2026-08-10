from .config import CHALLENGE_ROOT, SOLUTION
from shared.common.testkit import bootstrap, make_client, run_actions, strip_volatile


async def test_sessions_are_isolated():
    async with await make_client(CHALLENGE_ROOT) as client_a, await make_client(CHALLENGE_ROOT) as client_b:
        before = strip_volatile(await bootstrap(client_b))
        await run_actions(client_a, SOLUTION)
        after = strip_volatile(await bootstrap(client_b))
        assert after == before
