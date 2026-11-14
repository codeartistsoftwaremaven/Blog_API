from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


def get_redis(request: Request) -> Redis | None:
    return getattr(request.app.state, "redis", None)


DBSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[Redis | None, Depends(get_redis)]
