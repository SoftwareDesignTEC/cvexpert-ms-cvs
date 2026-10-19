from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION_NAME = "templates"


async def find_templates(
    db: AsyncIOMotorDatabase, *, page: int, page_size: int, search: str | None
) -> tuple[list[dict], int]:
    query: dict = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    collection = db[COLLECTION_NAME]
    total = await collection.count_documents(query)
    skip = (page - 1) * page_size
    cursor = collection.find(query).skip(skip).limit(page_size)
    items = [doc async for doc in cursor]
    return items, total
