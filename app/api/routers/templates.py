from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.domain.models import CurrentUser

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("")
def list_templates(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError
