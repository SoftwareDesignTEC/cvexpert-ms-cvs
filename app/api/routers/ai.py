from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep
from app.domain.models import (
    Cv,
    ExpandExperienceRequest,
    ExpandExperienceResponse,
    GenerateCvRequest,
    GenerateTextRequest,
    GenerateTextResponse,
    TranslateExperienceRequest,
    TranslateExperienceResponse,
)
from app.events.factory import EventPublisherDep
from app.llm.factory import LLMAdapterDep
from app.repositories.ai_usage import mark_ai_used
from app.repositories.mongo import DatabaseDep
from app.services import ai as ai_service

router = APIRouter(prefix="/cvs/ai", tags=["ai"])


@router.post("/expand-experience", response_model=ExpandExperienceResponse)
async def expand_experience(user: CurrentUserDep, llm: LLMAdapterDep, db: DatabaseDep, body: ExpandExperienceRequest):
    description = await llm.expand_experience(
        company=body.company,
        position=body.position,
        description=body.description,
        type=body.type,
        language=body.language,
    )
    await mark_ai_used(db, user_id=user.user_id)
    return ExpandExperienceResponse(description=description)


@router.post("/translate-experience", response_model=TranslateExperienceResponse)
async def translate_experience(
    user: CurrentUserDep, llm: LLMAdapterDep, db: DatabaseDep, body: TranslateExperienceRequest
):
    result = await llm.translate_experience(
        type=body.type,
        position=body.position,
        description=body.description,
        language=body.language,
        organization=body.organization,
    )
    await mark_ai_used(db, user_id=user.user_id)
    return TranslateExperienceResponse(position=result.position, description=result.description)


@router.post("/generate-text", response_model=GenerateTextResponse)
async def generate_text(user: CurrentUserDep, llm: LLMAdapterDep, db: DatabaseDep, body: GenerateTextRequest):
    text = await llm.generate_text(field=body.field, context=body.context, language=body.language)
    await mark_ai_used(db, user_id=user.user_id)
    return GenerateTextResponse(text=text)


@router.post("/generate-cv", response_model=Cv, status_code=status.HTTP_201_CREATED)
async def generate_cv(
    user: CurrentUserDep, llm: LLMAdapterDep, db: DatabaseDep, events: EventPublisherDep, body: GenerateCvRequest
):
    draft = await llm.generate_cv_draft(free_text=body.freeText, language=body.language)
    return await ai_service.generate_cv(
        db,
        user_id=user.user_id,
        event_publisher=events,
        draft=draft,
        title=body.title,
        template_id=body.templateId,
        full_name=body.fullName,
        email=user.email,
        phone=body.phone,
    )
