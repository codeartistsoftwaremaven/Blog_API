import os
from pathlib import Path
import sqlite3
import subprocess
import sys

from sqlalchemy.orm import configure_mappers

from app.db.base import Base
import app.models  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]


def test_migration_constraints_and_model_alignment(tmp_path):
    configure_mappers()
    tables = {"users", "categories", "articles", "tags", "article_tags", "comments"}
    assert set(Base.metadata.tables) == tables
    database = tmp_path / "migration.db"
    env = dict(os.environ, DATABASE_URL="sqlite+aiosqlite:///" + database.as_posix())

    def alembic(*args):
        result = subprocess.run([sys.executable, "-m", "alembic", *args], cwd=ROOT,
                                env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

    alembic("upgrade", "head")
    alembic("check")
    with sqlite3.connect(database) as db:
        db.execute("PRAGMA foreign_keys=ON")
        actual = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert actual == tables | {"alembic_version"}
        db.execute("INSERT INTO users (id,username,email,hashed_password) VALUES (1,'reader','r@example.com','hash')")
        assert db.execute("SELECT role FROM users").fetchone()[0] == "reader"
        db.execute("INSERT INTO articles (id,title,slug,content,author_id) VALUES (1,'Title','title','Text',1)")
        db.execute("INSERT INTO tags (id,name,slug) VALUES (1,'Tag','tag')")
        db.execute("INSERT INTO article_tags VALUES (1,1)")
        try:
            db.execute("INSERT INTO article_tags VALUES (1,1)")
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Duplicate tag assignment was accepted")
        db.execute("INSERT INTO comments (id,content,article_id,author_id) VALUES (1,'Parent',1,1)")
        db.execute("INSERT INTO comments (id,content,article_id,author_id,parent_id) VALUES (2,'Reply',1,1,1)")
        db.execute("DELETE FROM comments WHERE id=1")
        assert db.execute("SELECT count(*) FROM comments").fetchone()[0] == 0
        db.execute("INSERT INTO comments (content,article_id,author_id) VALUES ('Another',1,1)")
        db.execute("DELETE FROM articles WHERE id=1")
        assert db.execute("SELECT count(*) FROM comments").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM article_tags").fetchone()[0] == 0
    alembic("downgrade", "base")
    alembic("upgrade", "head")
