from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.models import PaginatedTemplates, Template
from app.repositories.templates import find_templates


def _to_template(doc: dict) -> Template:
    return Template(
        id=doc["id"],
        name=doc["name"],
        description=doc["description"],
        previewUrl=doc["previewUrl"],
        category=doc["category"],
        isPremium=doc["isPremium"],
        availableOffline=doc["availableOffline"],
    )


async def list_templates(
    db: AsyncIOMotorDatabase, *, page: int, page_size: int, search: str | None
) -> PaginatedTemplates:
    docs, total = await find_templates(db, page=page, page_size=page_size, search=search)
    return PaginatedTemplates(
        items=[_to_template(doc) for doc in docs],
        page=page,
        pageSize=page_size,
        totalRecords=total,
    )
