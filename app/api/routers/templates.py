from fastapi import APIRouter, Query

from app.api.deps import CurrentUserDep
from app.domain.models import PaginatedTemplates, Template
from app.repositories.mongo import DatabaseDep
from app.services.templates import get_template, list_templates

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=PaginatedTemplates)
async def get_templates(
    user: CurrentUserDep,
    db: DatabaseDep,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1),
    search: str | None = Query(default=None),
):
    return await list_templates(db, page=page, page_size=pageSize, search=search)


@router.get("/{template_id}", response_model=Template)
async def get_template_by_id(template_id: str, user: CurrentUserDep, db: DatabaseDep):
    return await get_template(db, template_id=template_id)
