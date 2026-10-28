from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUserDep
from app.domain.models import Cv, CvInput, PaginatedCvs
from app.repositories.mongo import DatabaseDep
from app.services import cvs as cvs_service

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("", response_model=PaginatedCvs)
async def get_cvs(
    user: CurrentUserDep,
    db: DatabaseDep,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1),
    search: str | None = Query(default=None),
):
    return await cvs_service.list_cvs(db, user_id=user.user_id, page=page, page_size=pageSize, search=search)


@router.post("", response_model=Cv, status_code=status.HTTP_201_CREATED)
async def create_cv(user: CurrentUserDep, db: DatabaseDep, body: CvInput):
    return await cvs_service.create_cv(db, user_id=user.user_id, data=body)


@router.get("/{cv_id}", response_model=Cv)
async def get_cv(cv_id: str, user: CurrentUserDep, db: DatabaseDep):
    return await cvs_service.get_cv(db, cv_id=cv_id, user_id=user.user_id)


@router.put("/{cv_id}", response_model=Cv)
async def update_cv(cv_id: str, user: CurrentUserDep, db: DatabaseDep, body: CvInput):
    return await cvs_service.update_cv(db, cv_id=cv_id, user_id=user.user_id, data=body)


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cv(cv_id: str, user: CurrentUserDep, db: DatabaseDep):
    await cvs_service.delete_cv(db, cv_id=cv_id, user_id=user.user_id)
