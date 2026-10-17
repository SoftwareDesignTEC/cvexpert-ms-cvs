from fastapi import APIRouter

from app.api.deps import CurrentUserDep

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("")
def list_templates(user: CurrentUserDep):
    raise NotImplementedError
