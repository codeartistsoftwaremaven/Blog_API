from fastapi import APIRouter
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/comments", tags=["评论"])


@router.get("")
async def list_comments(article_id: int):
    raise BusinessException(50100, "文章评论列表将在后续章节实现", 501)


@router.post("")
async def create_comment():
    raise BusinessException(50100, "评论及回复将在后续章节实现", 501)


@router.delete("/{comment_id}")
async def delete_comment(comment_id: int):
    raise BusinessException(50100, "评论删除将在后续章节实现", 501)
