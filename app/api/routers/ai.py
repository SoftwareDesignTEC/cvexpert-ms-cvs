from fastapi import APIRouter

from app.api.deps import CurrentUserDep

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/expand-experience")
def expand_experience(user: CurrentUserDep):
    raise NotImplementedError


@router.post("/translate-experience")
def translate_experience(user: CurrentUserDep):
    raise NotImplementedError
