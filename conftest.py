# Ensure APP_ENV is test BEFORE any imports
import os
import sys

os.environ["APP_ENV"] = "test"
os.environ["TESTING"] = "1"

_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "app"))
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

import pytest
import pytest_asyncio
from app.core.database import engine, Base

pytest_plugins = ["pytest_asyncio"]

@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_test_database():
    """Automatically create all tables in SQLite in-memory database for testing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

