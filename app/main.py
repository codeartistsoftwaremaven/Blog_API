import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text

from app.api.v1 import articles, auth, categories, comments, users
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings.DEBUG)
    logger.info("%s v%s starting (DEBUG=%s)", settings.APP_NAME, settings.VERSION, settings.DEBUG)
    app.state.redis = None
    client = Redis.from_url(
        settings.REDIS_URL, decode_responses=True,
        socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
        socket_timeout=settings.REDIS_CONNECT_TIMEOUT,
    )
    try:
        # Database is required; Redis can degrade independently.
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        try:
            await client.ping()
            app.state.redis = client
            logger.info("Redis connected")
        except (RedisError, OSError):
            logger.warning("Redis unavailable; continuing with database fallback")
        yield
    finally:
        app.state.redis = None
        await client.aclose()
        await engine.dispose()
        logger.info("Application stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.APP_NAME, version=settings.VERSION,
                  debug=settings.DEBUG, lifespan=lifespan)
    register_exception_handlers(app)
    for module in (auth, users, articles, categories, comments):
        app.include_router(module.router, prefix="/api/v1")

    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                       allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
                       allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
                       expose_headers=["X-Request-ID"])
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        # Generate our own ID so untrusted input cannot forge log entries.
        request.state.request_id = uuid4().hex
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_id=%s %s %s failed", request.state.request_id,
                             request.method, request.url.path)
            raise
        response.headers["X-Request-ID"] = request.state.request_id
        logger.info("request_id=%s %s %s status=%s duration_ms=%.1f",
                    request.state.request_id, request.method, request.url.path,
                    response.status_code, (perf_counter() - started) * 1000)
        return response

    @app.get("/health", tags=["运维"])
    async def health(request: Request):
        redis_ok = False
        client = getattr(request.app.state, "redis", None)
        if client is not None:
            try:
                redis_ok = bool(await client.ping())
            except (RedisError, OSError):
                logger.warning("Redis health check failed")
        return {"status": "ok", "version": settings.VERSION, "redis": redis_ok}

    return app


app = create_app()
