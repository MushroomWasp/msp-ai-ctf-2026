from .config import CHALLENGE_ROOT, EXPECTED_FLAG
from shared.common.testkit import bootstrap, make_client


async def test_flag_is_not_exposed_trivially():
    async with await make_client(CHALLENGE_ROOT) as client:
        index = await client.get("/")
        assert "AICTF{" not in index.text
        assert EXPECTED_FLAG not in index.text
        payload = await bootstrap(client)
        assert payload["solved"] is False
        assert EXPECTED_FLAG not in str(payload)
