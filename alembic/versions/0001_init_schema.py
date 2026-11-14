"""Create the six Blog API tables.

Revision ID: 0001
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def entity_columns():
    return [
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    ]


def upgrade():
    op.create_table(
        "users",
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("role", sa.Enum("reader", "author", "admin", name="user_role", native_enum=False, create_constraint=True),
                  server_default="reader", nullable=False),
        *entity_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_table(
        "categories",
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        *entity_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_categories"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )
    op.create_table(
        "tags",
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        *entity_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_tags"),
        sa.UniqueConstraint("name", name="uq_tags_name"),
        sa.UniqueConstraint("slug", name="uq_tags_slug"),
    )
    op.create_table(
        "articles",
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(240), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.String(500), nullable=True),
        sa.Column("status", sa.Enum("draft", "published", name="article_status", native_enum=False, create_constraint=True),
                  server_default="draft", nullable=False),
        sa.Column("views", sa.Integer(), server_default="0", nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        *entity_columns(),
        sa.CheckConstraint("views >= 0", name="views_nonnegative"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="fk_articles_author_id_users", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name="fk_articles_category_id_categories", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_articles"),
    )
    op.create_index("ix_articles_slug", "articles", ["slug"], unique=True)
    op.create_index("ix_articles_status", "articles", ["status"])
    op.create_index("ix_articles_author_id", "articles", ["author_id"])
    op.create_index("ix_articles_category_id", "articles", ["category_id"])
    op.create_table(
        "article_tags",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], name="fk_article_tags_article_id_articles", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="fk_article_tags_tag_id_tags", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id", name="pk_article_tags"),
    )
    op.create_table(
        "comments",
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        *entity_columns(),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], name="fk_comments_article_id_articles", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="fk_comments_author_id_users", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"], name="fk_comments_parent_id_comments", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
    )
    op.create_index("ix_comments_article_id", "comments", ["article_id"])
    op.create_index("ix_comments_author_id", "comments", ["author_id"])
    op.create_index("ix_comments_parent_id", "comments", ["parent_id"])


def downgrade():
    for table in ("comments", "article_tags", "articles", "tags", "categories", "users"):
        op.drop_table(table)
