from fastapi import APIRouter

from app.api.deps import CurrentUserDep
from app.domain.models import (
    ExpandExperienceRequest,
    ExpandExperienceResponse,
    TranslateExperienceRequest,
    TranslateExperienceResponse,
)
from app.llm.factory import LLMAdapterDep

router = APIRouter(prefix="/cvs/ai", tags=["ai"])


@router.post("/expand-experience", response_model=ExpandExperienceResponse)
async def expand_experience(user: CurrentUserDep, llm: LLMAdapterDep, body: ExpandExperienceRequest):
    description = await llm.expand_experience(
        company=body.company,
        position=body.position,
        description=body.description,
        type=body.type,
        language=body.language,
    )
    return ExpandExperienceResponse(description=description)


@router.post("/translate-experience", response_model=TranslateExperienceResponse)
async def translate_experience(user: CurrentUserDep, llm: LLMAdapterDep, body: TranslateExperienceRequest):
    result = await llm.translate_experience(
        type=body.type,
        position=body.position,
        description=body.description,
        language=body.language,
        organization=body.organization,
    )
    return TranslateExperienceResponse(position=result.position, description=result.description)
