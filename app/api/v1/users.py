from fastapi import APIRouter
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me")
async def get_profile():
    raise BusinessException(50100, "个人资料将在后续认证章节实现", 501)


@router.patch("/me")
async def update_profile():
    raise BusinessException(50100, "修改资料将在后续认证章节实现", 501)


@router.get("")
async def list_users():
    raise BusinessException(50100, "管理员用户列表将在后续权限章节实现", 501)
