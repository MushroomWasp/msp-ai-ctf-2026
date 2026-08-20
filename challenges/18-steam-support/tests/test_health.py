from .config import CHALLENGE_ROOT
from shared.common.testkit import make_client


async def test_health_endpoint():
    async with await make_client(CHALLENGE_ROOT) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
