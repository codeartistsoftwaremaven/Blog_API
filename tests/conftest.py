import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Set before app imports, so test startup never opens the real blog.db.
_database_dir = TemporaryDirectory(prefix="blog-api-tests-")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + (Path(_database_dir.name) / "test.db").as_posix()
os.environ["SECRET_KEY"] = "test-secret-" + "a" * 48
os.environ["DEBUG"] = "false"
os.environ["ALLOWED_HOSTS"] = '["testserver","localhost","127.0.0.1"]'


@pytest.fixture
def anyio_backend():
    return "asyncio"
