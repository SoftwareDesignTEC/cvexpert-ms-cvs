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


async def find_cv_by_id(db: AsyncIOMotorDatabase, *, cv_id: str, user_id: str) -> dict | None:
    return await db[COLLECTION_NAME].find_one({"id": cv_id, "userId": user_id})


async def insert_cv(db: AsyncIOMotorDatabase, doc: dict) -> None:
    await db[COLLECTION_NAME].insert_one(doc)


async def replace_cv(db: AsyncIOMotorDatabase, *, cv_id: str, user_id: str, doc: dict) -> bool:
    result = await db[COLLECTION_NAME].replace_one({"id": cv_id, "userId": user_id}, doc)
    return result.matched_count > 0


async def delete_cv(db: AsyncIOMotorDatabase, *, cv_id: str, user_id: str) -> bool:
    result = await db[COLLECTION_NAME].delete_one({"id": cv_id, "userId": user_id})
    return result.deleted_count > 0
