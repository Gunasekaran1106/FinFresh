"""
Shared pytest fixtures.

Strategy: override the database dependency at startup so tests hit a
dedicated test database on the same Atlas cluster, then wipe it after
each test function to guarantee isolation.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.config import settings
from app.database import connect_db, close_db, get_database

TEST_DB_NAME = f"{settings.database_name}_test"


#@pytest.fixture(scope="session")
#def event_loop():
 #   """Single event loop for the entire test session."""
  #  loop = asyncio.new_event_loop()
   # yield loop
    #loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    """
    Connect to MongoDB once for the session using the test database name.
    We monkey-patch the module-level _database variable to point at the
    test DB instead of the production DB.
    """
    import app.database as db_module

    client = AsyncIOMotorClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=5000,
    )
    await client.admin.command("ping")

    db_module._client = client
    db_module._database = client[TEST_DB_NAME]
    print("TEST DB INITIALIZED:", TEST_DB_NAME)

    yield

    # Drop the test database after all tests complete
    await client.drop_database(TEST_DB_NAME)
    client.close()
    db_module._client = None
    db_module._database = None


@pytest_asyncio.fixture(autouse=True)
async def clean_collections(setup_test_db):
    """Wipe all collections before each test for full isolation."""
    db = get_database()
    for col_name in await db.list_collection_names():
        await db[col_name].delete_many({})
    yield


@pytest_asyncio.fixture
async def client():
    """Async HTTP client wired directly to the FastAPI app (no real server)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a user and return the full response payload."""
    resp = await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Str0ng!Pass",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user: dict) -> dict:
    """Return Authorization headers for the registered test user."""
    token = registered_user["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}