from fastapi import APIRouter
from app.core.exceptions import BusinessException

router = APIRouter(tags=["分类与标签"])


@router.get("/categories")
async def list_categories():
    raise BusinessException(50100, "分类列表将在后续章节实现", 501)


@router.post("/categories")
async def create_category():
    raise BusinessException(50100, "管理员分类管理将在后续章节实现", 501)


@router.get("/tags")
async def list_tags():
    raise BusinessException(50100, "标签列表将在后续章节实现", 501)


@router.post("/tags")
async def create_tag():
    raise BusinessException(50100, "管理员标签管理将在后续章节实现", 501)
