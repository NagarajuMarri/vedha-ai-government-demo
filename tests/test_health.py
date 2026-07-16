"""Backend health endpoint tests."""

import asyncio

import httpx

from backend.app.main import app


def test_health_endpoint() -> None:
    async def request_health() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/api/v1/health")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "vedha-ai-government-demo-api",
        "version": "0.1.0",
    }
    assert response.headers["x-request-id"]
