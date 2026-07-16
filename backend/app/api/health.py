"""Health-check endpoint for service verification."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Public health-check response contract."""

    status: Literal["ok"]
    service: str
    version: str


@router.get(
    "/health",
    operation_id="get_health",
    response_model=HealthResponse,
    summary="Check API health",
)
async def get_health() -> HealthResponse:
    """Report that the API process is accepting requests."""

    return HealthResponse(
        status="ok",
        service="vedha-ai-government-demo-api",
        version="0.1.0",
    )
