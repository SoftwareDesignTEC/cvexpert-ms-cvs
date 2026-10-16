from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.domain.models import CurrentUser

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/expand-experience")
def expand_experience(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError


@router.post("/translate-experience")
def translate_experience(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError
