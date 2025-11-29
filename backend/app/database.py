"""Database configuration and connection"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import get_settings

settings = get_settings()


class Database:
    """Database connection manager"""
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    db.client = AsyncIOMotorClient(settings.mongo_url)
    db.db = db.client[settings.mongodb_db_name]

    # Create indexes
    await db.db.logs.create_index([("organisation_id", 1), ("timestamp", -1)])
    await db.db.logs.create_index([("organisation_id", 1), ("host", 1)])
    await db.db.logs.create_index([("organisation_id", 1), ("event_type", 1)])

    await db.db.alerts.create_index([("organisation_id", 1), ("created_at", -1)])
    await db.db.alerts.create_index([("organisation_id", 1), ("status", 1)])
    await db.db.alerts.create_index("alert_id", unique=True)

    await db.db.endpoints.create_index([("organisation_id", 1), ("host", 1)], unique=True)

    print("✅ Connected to MongoDB")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("❌ Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.db
