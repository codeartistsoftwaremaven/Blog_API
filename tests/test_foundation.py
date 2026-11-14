from datetime import timedelta
from unittest.mock import AsyncMock

import jwt
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.exceptions import BusinessException, register_exception_handlers
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.main import create_app
from app.utils.redis_cache import get_cached_json, set_cached_json


def test_password_and_tokens():
    hashed = hash_password("a good password")
    assert hashed.startswith("$argon2")
    assert verify_password("a good password", hashed)
    assert not verify_password("wrong password", hashed)
    first, second = create_access_token("42"), create_access_token("42")
    assert decode_token(first)["sub"] == "42"
    assert decode_token(first)["jti"] != decode_token(second)["jti"]
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(create_access_token("42", timedelta(seconds=-10)))
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(jwt.encode({"sub": "42"}, "wrong-secret-" + "x" * 40, algorithm="HS256"))


def test_startup_without_redis_and_openapi(monkeypatch):
    import app.main as main
    redis = AsyncMock()
    redis.ping.side_effect = RedisConnectionError("offline")
    monkeypatch.setattr(main.Redis, "from_url", lambda *args, **kwargs: redis)
    app = create_app()

    @app.get("/unexpected")
    async def unexpected():
        raise RuntimeError("private detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        health = client.get("/health")
        assert health.json() == {"status": "ok", "version": "1.0.0", "redis": False}
        assert len(health.headers["X-Request-ID"]) == 32
        assert client.get("/docs").status_code == 200
        paths = client.get("/openapi.json").json()["paths"]
        for path in ("/api/v1/auth/login", "/api/v1/users/me", "/api/v1/articles",
                     "/api/v1/categories", "/api/v1/tags", "/api/v1/comments"):
            assert path in paths
        skeleton = client.get("/api/v1/articles")
        assert skeleton.status_code == 501
        assert skeleton.json()["code"] == 50100
        assert client.get("/missing").json()["code"] == 40400
        response = client.get("/unexpected")
        assert response.status_code == 500
        assert len(response.headers["X-Request-ID"]) == 32
        assert "private detail" not in response.text
        assert client.get("/health", headers={"host": "untrusted.invalid"}).status_code == 400
    redis.aclose.assert_awaited_once()


def test_redis_health_tracks_outage(monkeypatch):
    import app.main as main
    redis = AsyncMock()
    redis.ping.return_value = True
    monkeypatch.setattr(main.Redis, "from_url", lambda *args, **kwargs: redis)
    with TestClient(create_app()) as client:
        assert client.get("/health").json()["redis"] is True
        redis.ping.side_effect = RedisConnectionError("connection lost")
        assert client.get("/health").json()["redis"] is False


def test_four_exception_handlers():
    app = FastAPI(debug=False)
    register_exception_handlers(app)

    class Input(BaseModel):
        count: int

    @app.get("/business")
    async def business():
        raise BusinessException(40900, "conflict", 409)

    @app.get("/http")
    async def http():
        raise HTTPException(401, "login required", headers={"WWW-Authenticate": "Bearer"})

    @app.post("/validation")
    async def validation(body: Input):
        return body

    @app.get("/unexpected")
    async def unexpected():
        raise RuntimeError("private detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.get("/business").status_code == 409
        response = client.get("/http")
        assert response.headers["WWW-Authenticate"] == "Bearer"
        assert response.json()["code"] == 40100
        response = client.post("/validation", json={"count": "bad"})
        assert response.status_code == 422
        assert response.json()["errors"][0]["field"] == "count"
        response = client.get("/unexpected")
        assert response.status_code == 500
        assert set(response.json()) == {"code", "message", "data", "errors"}
        assert "private detail" not in response.text


@pytest.mark.asyncio
async def test_cache_falls_back():
    assert await get_cached_json(None, "missing") is None
    assert not await set_cached_json(None, "key", {}, 10)
    redis = AsyncMock()
    redis.get.side_effect = RedisConnectionError("offline")
    redis.set.side_effect = RedisConnectionError("offline")
    assert await get_cached_json(redis, "key") is None
    assert not await set_cached_json(redis, "key", {}, 10)
