from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.errors import NotFoundError
from app.domain.models import PaginatedTemplates, Template, TemplateLayout
from app.repositories.templates import find_template_by_id, find_templates


def _to_template(doc: dict) -> Template:
    layout = doc.get("layout")
    return Template(
        id=doc["id"],
        name=doc["name"],
        description=doc["description"],
        previewUrl=doc["previewUrl"],
        category=doc["category"],
        isPremium=doc["isPremium"],
        availableOffline=doc["availableOffline"],
        layout=TemplateLayout.model_validate(layout) if layout else None,
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


async def get_template(db: AsyncIOMotorDatabase, *, template_id: str) -> Template:
    doc = await find_template_by_id(db, template_id=template_id)
    if doc is None:
        raise NotFoundError("Plantilla no encontrada")
    return _to_template(doc)
