"""Import every model so Alembic sees all six tables."""

from app.models.user import Role, User
from app.models.article import Article, ArticleStatus, Category, Tag, article_tags
from app.models.comment import Comment

__all__ = ["User", "Role", "Article", "ArticleStatus", "Category", "Tag", "article_tags", "Comment"]
