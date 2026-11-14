from __future__ import annotations

from enum import Enum

from sqlalchemy import Boolean, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(str, Enum):
    READER = "reader"
    AUTHOR = "author"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, values_callable=lambda roles: [r.value for r in roles],
               name="user_role", native_enum=False, create_constraint=True),
        default=Role.READER, server_default="reader",
    )
    articles: Mapped[list["Article"]] = relationship(back_populates="author", passive_deletes="all")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author", passive_deletes="all")
