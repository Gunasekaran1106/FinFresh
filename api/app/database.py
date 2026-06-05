import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import settings

print("MongoDB URL:", settings.mongodb_url)

logger = logging.getLogger(__name__)

# Module-level client — shared across the application lifetime
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """
    Open the MongoDB connection. Called once on application startup.
    Motor manages an internal connection pool automatically.
    """
    global _client, _database

    try:
        _client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,   # fail fast if Atlas unreachable
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=1,
        )

        # Force a real connection attempt so startup fails loudly if Atlas
        # credentials are wrong rather than silently at first request.
        await _client.admin.command("ping")

        _database = _client[settings.database_name]
        logger.info("Connected to MongoDB Atlas — database: %s", settings.database_name)

        # Create indexes for optimal query performance
        await _create_indexes()

    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.critical("MongoDB connection failed: %s", exc)
        raise RuntimeError(f"Could not connect to MongoDB: {exc}") from exc


async def _create_indexes() -> None:
    """Create MongoDB indexes for transactions collection."""
    db = _database
    transactions_col = db["transactions"]

    try:
        # Compound index on userId and date for financial health queries
        await transactions_col.create_index(
            [("user_id", 1), ("date", -1)],
            name="idx_user_date",
        )
        logger.info("Created index: user_id (ascending), date (descending)")
    except Exception as exc:
        logger.warning("Failed to create index: %s", exc)


async def close_db() -> None:
    """Close the MongoDB connection. Called once on application shutdown."""
    global _client, _database

    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the active database instance.
    Raises RuntimeError if called before connect_db() succeeds.
    """
    if _database is None:
        raise RuntimeError(
            "Database is not initialised. "
            "Ensure connect_db() ran during application startup."
        )
    return _database