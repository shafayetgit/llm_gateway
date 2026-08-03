from httpx import AsyncClient


async def test_health_check_endpoint(client: AsyncClient):
    """Tests /health status endpoint."""
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"


async def test_unauthenticated_models_access(client: AsyncClient):
    """Tests /api/v1/models returns 401 when no token is provided."""
    res = await client.get("/api/v1/models")
    assert res.status_code == 401
