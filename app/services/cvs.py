from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.models import Cv, PaginatedCvs
from app.repositories.cvs import find_cvs


async def list_cvs(
    db: AsyncIOMotorDatabase, *, user_id: str, page: int, page_size: int, search: str | None
) -> PaginatedCvs:
    docs, total = await find_cvs(db, user_id=user_id, page=page, page_size=page_size, search=search)
    return PaginatedCvs(
        items=[Cv.model_validate(doc) for doc in docs],
        page=page,
        pageSize=page_size,
        totalRecords=total,
    )
