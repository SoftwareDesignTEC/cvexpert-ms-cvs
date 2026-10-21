from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION_NAME = "cvs"


async def find_cvs(
    db: AsyncIOMotorDatabase, *, user_id: str, page: int, page_size: int, search: str | None
) -> tuple[list[dict], int]:
    query: dict = {"userId": user_id}
    if search:
        query["title"] = {"$regex": search, "$options": "i"}

    collection = db[COLLECTION_NAME]
    total = await collection.count_documents(query)
    skip = (page - 1) * page_size
    cursor = collection.find(query).skip(skip).limit(page_size)
    items = [doc async for doc in cursor]
    return items, total
