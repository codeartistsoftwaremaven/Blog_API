from fastapi import APIRouter
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/articles", tags=["文章"])


@router.get("")
async def list_articles():
    raise BusinessException(50100, "文章列表及分类标签筛选将在后续章节实现", 501)


@router.get("/{slug}")
async def get_article(slug: str):
    raise BusinessException(50100, "文章详情将在后续章节实现", 501)


@router.post("")
async def create_article():
    raise BusinessException(50100, "文章创建将在后续章节实现", 501)


@router.patch("/{slug}")
async def update_article(slug: str):
    raise BusinessException(50100, "文章编辑及发布将在后续章节实现", 501)


@router.delete("/{slug}")
async def delete_article(slug: str):
    raise BusinessException(50100, "文章删除将在后续章节实现", 501)
