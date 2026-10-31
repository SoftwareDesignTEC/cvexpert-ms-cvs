import time
import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.domain.errors import NotFoundError, ValidationError
from app.domain.models import Cv, CvInput, PaginatedCvs
from app.repositories.cvs import delete_cv as repo_delete_cv
from app.repositories.cvs import find_cv_by_id, find_cvs, insert_cv, replace_cv
from app.repositories.templates import find_template_by_id


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


async def get_cv(db: AsyncIOMotorDatabase, *, cv_id: str, user_id: str) -> Cv:
    doc = await find_cv_by_id(db, cv_id=cv_id, user_id=user_id)
    if doc is None:
        raise NotFoundError("CV no encontrado")
    return Cv.model_validate(doc)


async def _resolve_thumbnail_url(db: AsyncIOMotorDatabase, template_id: str) -> str | None:
    template = await find_template_by_id(db, template_id=template_id)
    if template is None:
        raise ValidationError({"templateId": "La plantilla no existe"})
    return template.get("previewUrl")


def _with_id(item: BaseModel) -> dict:
    data = item.model_dump()
    if not data.get("id"):
        data["id"] = str(uuid.uuid4())
    return data


def _input_sections(data: CvInput) -> dict:
    return {
        "personalInfo": data.personalInfo.model_dump(),
        "workExperiences": [_with_id(item) for item in data.workExperiences],
        "education": [_with_id(item) for item in data.education],
        "skills": [_with_id(item) for item in data.skills],
        "languages": [_with_id(item) for item in data.languages],
        "certifications": [_with_id(item) for item in data.certifications],
    }


async def create_cv(db: AsyncIOMotorDatabase, *, user_id: str, data: CvInput) -> Cv:
    thumbnail_url = await _resolve_thumbnail_url(db, data.templateId)
    now = int(time.time() * 1000)
    doc = {
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "title": data.title,
        "templateId": data.templateId,
        "thumbnailUrl": thumbnail_url,
        "createdAt": now,
        "updatedAt": now,
        **_input_sections(data),
    }
    await insert_cv(db, doc)
    return Cv.model_validate(doc)


async def update_cv(db: AsyncIOMotorDatabase, *, cv_id: str, user_id: str, data: CvInput) -> Cv:
    existing = await find_cv_by_id(db, cv_id=cv_id, user_id=user_id)
    if existing is None:
        raise NotFoundError("CV no encontrado")

    thumbnail_url = await _resolve_thumbnail_url(db, data.templateId)
    doc = {
        "id": cv_id,
        "userId": user_id,
        "title": data.title,
        "templateId": data.templateId,
        "thumbnailUrl": thumbnail_url,
        "createdAt": existing["createdAt"],
        "updatedAt": int(time.time() * 1000),
        **_input_sections(data),
    }
    await replace_cv(db, cv_id=cv_id, user_id=user_id, doc=doc)
    return Cv.model_validate(doc)


async def delete_cv(db: AsyncIOMotorDatabase, *, cv_id: str, user_id: str) -> None:
    deleted = await repo_delete_cv(db, cv_id=cv_id, user_id=user_id)
    if not deleted:
        raise NotFoundError("CV no encontrado")
