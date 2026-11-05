import time

from motor.motor_asyncio import AsyncIOMotorDatabase


async def mark_ai_used(db: AsyncIOMotorDatabase, *, user_id: str) -> None:
    await db["ai_usage"].update_one(
        {"userId": user_id},
        {"$set": {"userId": user_id, "markedAt": int(time.time() * 1000)}},
        upsert=True,
    )


async def consume_ai_used(db: AsyncIOMotorDatabase, *, user_id: str) -> bool:
    result = await db["ai_usage"].delete_one({"userId": user_id})
    return result.deleted_count > 0
