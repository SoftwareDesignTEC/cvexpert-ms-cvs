from fastapi import APIRouter, Query

from app.api.deps import CurrentUserDep
from app.domain.models import PaginatedCvs
from app.repositories.mongo import DatabaseDep
from app.services.cvs import list_cvs

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("", response_model=PaginatedCvs)
async def get_cvs(
    user: CurrentUserDep,
    db: DatabaseDep,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1),
    search: str | None = Query(default=None),
):
    return await list_cvs(db, user_id=user.user_id, page=page, page_size=pageSize, search=search)


@router.post("")
def create_cv(user: CurrentUserDep):
    raise NotImplementedError


@router.get("/{cv_id}")
def get_cv(cv_id: str, user: CurrentUserDep):
    raise NotImplementedError


@router.put("/{cv_id}")
def update_cv(cv_id: str, user: CurrentUserDep):
    raise NotImplementedError


@router.delete("/{cv_id}")
def delete_cv(cv_id: str, user: CurrentUserDep):
    raise NotImplementedError
