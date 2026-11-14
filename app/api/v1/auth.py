from fastapi import APIRouter
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
async def register():
    raise BusinessException(50100, "注册将在后续认证章节实现", 501)


@router.post("/login")
async def login():
    raise BusinessException(50100, "登录将在后续认证章节实现", 501)


@router.post("/logout")
async def logout():
    raise BusinessException(50100, "注销与令牌黑名单将在后续认证章节实现", 501)
