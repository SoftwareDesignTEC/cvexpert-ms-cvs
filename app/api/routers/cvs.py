from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.domain.models import CurrentUser

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("")
def list_cvs(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError


@router.post("")
def create_cv(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError


@router.get("/{cv_id}")
def get_cv(cv_id: str, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError


@router.put("/{cv_id}")
def update_cv(cv_id: str, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError


@router.delete("/{cv_id}")
def delete_cv(cv_id: str, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError
