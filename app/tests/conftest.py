from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core import get_db, settings
from app.main import app
from app.models.base import Base


@pytest_asyncio.fixture
async def test_engine():
    """Function-scoped async engine with NullPool to prevent event loop mismatch."""
    engine = create_async_engine(
        settings.test_database_url, echo=False, poolclass=NullPool
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def TestingSessionLocal(test_engine):
    """Function-scoped sessionmaker."""
    return async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db(test_engine):
    """Creates database schema before each test and drops tables after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def override_db_dependency(TestingSessionLocal):
    """Overrides app get_db dependency for tests."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async test HTTP client fixture."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture
def admin_headers() -> dict[str, str]:
    """Admin secret header fixture."""
    return {"X-Admin-Secret": settings.secret_key}
