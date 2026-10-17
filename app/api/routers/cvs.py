from fastapi import APIRouter

from app.api.deps import CurrentUserDep

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("")
def list_cvs(user: CurrentUserDep):
    raise NotImplementedError


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
