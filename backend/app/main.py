"""FastAPI application factory and process entry point."""

from collections.abc import Awaitable, Callable
import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.app.api.router import api_router
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import configure_logging


logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach an opaque correlation identifier to every response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exception: RequestValidationError,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        details = [
            {
                "location": list(error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exception.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Please correct the invalid request data and try again.",
                    "details": details,
                    "request_id": request_id,
                }
            },
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exception: Exception,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.exception(
            "Unhandled application error",
            extra={"request_id": request_id, "path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "The service could not complete the request.",
                    "details": [],
                    "request_id": request_id,
                }
            },
            headers={"X-Request-ID": request_id},
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured FastAPI application instance."""

    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)

    app = FastAPI(
        title=resolved_settings.project_name,
        version="0.1.0",
        description="Backend foundation for the Vedha AI Government Demo.",
    )
    app.state.settings = resolved_settings
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type", "X-Request-ID"],
    )
    _register_exception_handlers(app)
    app.include_router(api_router, prefix=resolved_settings.api_v1_prefix)
    return app


app = create_app()
