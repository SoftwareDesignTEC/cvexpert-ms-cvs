from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError as PydanticValidationError

from app.domain.models import (
    Certification,
    Cv,
    CvInput,
    Education,
    Language,
    PersonalInfo,
    Skill,
    WorkExperience,
)
from app.events.base import EventPublisher
from app.llm.base import GeneratedCvDraft
from app.repositories.ai_usage import mark_ai_used
from app.services.cvs import create_cv

DEFAULT_SKILL_CATEGORY = "General"
DEFAULT_TEMPLATE_ID = "minimal"


def _default_title() -> str:
    return f"CV generado el {datetime.now(UTC).date().isoformat()}"


def _placeholder_start_date() -> int:
    today = datetime.now(UTC).date()
    return int(datetime(today.year, today.month, today.day, tzinfo=UTC).timestamp() * 1000)


def _parse_date_to_epoch_ms(value: object) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            parsed = datetime.strptime(text, fmt).replace(tzinfo=UTC)
            return int(parsed.timestamp() * 1000)
        except ValueError:
            continue
    try:
        year = int(text[:4])
        parsed = datetime(year, 1, 1, tzinfo=UTC)
        return int(parsed.timestamp() * 1000)
    except ValueError:
        return None


def _normalize_work_experience(raw: dict) -> WorkExperience | None:
    item = dict(raw)
    item["current"] = bool(item.get("current", False))
    item["startDate"] = _parse_date_to_epoch_ms(item.get("startDate")) or _placeholder_start_date()
    item["endDate"] = _parse_date_to_epoch_ms(item.get("endDate"))
    item.setdefault("description", "")
    item.setdefault("position", "")
    if item.get("type") not in ("formal", "freelance", "volunteer", "school-project", "informal"):
        item["type"] = "informal"
    try:
        return WorkExperience.model_validate(item)
    except PydanticValidationError:
        return None


def _normalize_education(raw: dict) -> Education | None:
    item = dict(raw)
    item["current"] = bool(item.get("current", False))
    item["startDate"] = _parse_date_to_epoch_ms(item.get("startDate")) or _placeholder_start_date()
    item["endDate"] = _parse_date_to_epoch_ms(item.get("endDate"))
    item.setdefault("institution", "")
    item.setdefault("degree", "")
    item.setdefault("field", "")
    try:
        return Education.model_validate(item)
    except PydanticValidationError:
        return None


def _normalize_skill(raw: dict) -> Skill | None:
    item = dict(raw)
    item.setdefault("category", DEFAULT_SKILL_CATEGORY)
    try:
        return Skill.model_validate(item)
    except PydanticValidationError:
        return None


def _normalize_language(raw: dict) -> Language | None:
    try:
        return Language.model_validate(raw)
    except PydanticValidationError:
        return None


def _normalize_certification(raw: dict) -> Certification | None:
    item = dict(raw)
    item["issuedAt"] = _parse_date_to_epoch_ms(item.get("issuedAt"))
    item["expiresAt"] = _parse_date_to_epoch_ms(item.get("expiresAt"))
    try:
        return Certification.model_validate(item)
    except PydanticValidationError:
        return None


def build_cv_input_from_draft(
    draft: GeneratedCvDraft,
    *,
    title: str,
    template_id: str,
    full_name: str,
    email: str,
    phone: str | None,
) -> CvInput:
    work_experiences = [
        item for raw in draft.workExperiences if (item := _normalize_work_experience(raw)) is not None
    ]
    education = [item for raw in draft.education if (item := _normalize_education(raw)) is not None]
    skills = [item for raw in draft.skills if (item := _normalize_skill(raw)) is not None]
    languages = [item for raw in draft.languages if (item := _normalize_language(raw)) is not None]
    certifications = [
        item for raw in draft.certifications if (item := _normalize_certification(raw)) is not None
    ]

    return CvInput(
        title=title,
        templateId=template_id,
        personalInfo=PersonalInfo(fullName=full_name, email=email, phone=phone, bio=draft.bio),
        workExperiences=work_experiences,
        education=education,
        skills=skills,
        languages=languages,
        certifications=certifications,
    )


async def generate_cv(
    db: AsyncIOMotorDatabase,
    *,
    user_id: str,
    event_publisher: EventPublisher,
    draft: GeneratedCvDraft,
    title: str | None,
    template_id: str | None,
    full_name: str,
    email: str,
    phone: str | None,
) -> Cv:
    cv_input = build_cv_input_from_draft(
        draft,
        title=title or _default_title(),
        template_id=template_id or DEFAULT_TEMPLATE_ID,
        full_name=full_name,
        email=email,
        phone=phone,
    )
    await mark_ai_used(db, user_id=user_id)
    return await create_cv(db, user_id=user_id, data=cv_input, event_publisher=event_publisher)
