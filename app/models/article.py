from __future__ import annotations

from enum import Enum

from sqlalchemy import CheckConstraint, Column, Enum as SAEnum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

article_tags = Table(
    "article_tags", Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Category(Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    articles: Mapped[list["Article"]] = relationship(back_populates="category", passive_deletes=True)


class Tag(Base):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    articles: Mapped[list["Article"]] = relationship(
        secondary=article_tags, back_populates="tags", passive_deletes=True
    )


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (CheckConstraint("views >= 0", name="views_nonnegative"),)

    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(240), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[ArticleStatus] = mapped_column(
        SAEnum(ArticleStatus, values_callable=lambda statuses: [s.value for s in statuses],
               name="article_status", native_enum=False, create_constraint=True),
        default=ArticleStatus.DRAFT, server_default="draft", index=True,
    )
    views: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    author: Mapped["User"] = relationship(back_populates="articles")
    category: Mapped[Category | None] = relationship(back_populates="articles")
    tags: Mapped[list[Tag]] = relationship(secondary=article_tags, back_populates="articles", passive_deletes=True)
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="article", cascade="all, delete-orphan", passive_deletes=True
    )
