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


def test_local_frontend_cors_preflight_is_allowed() -> None:
    async def request_preflight(origin: str) -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.options(
                "/api/v1/lessons/explain",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )

    for origin in ("http://127.0.0.1:5500", "http://localhost:5500"):
        response = asyncio.run(request_preflight(origin))
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
