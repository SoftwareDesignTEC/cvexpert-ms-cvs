from app.events.base import EventPublisher
from app.llm.base import GeneratedCvDraft, LLMAdapter, TranslatedExperience


class FakeLLMAdapter(LLMAdapter):
    """Implementación falsa de LLMAdapter para pruebas. Nunca llama a un proveedor real."""

    def __init__(self, cv_draft: GeneratedCvDraft | None = None) -> None:
        self._cv_draft = cv_draft

    async def expand_experience(
        self, company: str, position: str, description: str, type: str, language: str
    ) -> str:
        return f"{description} (expandida)"

    async def translate_experience(
        self,
        type: str,
        position: str,
        description: str,
        language: str,
        organization: str | None = None,
    ) -> TranslatedExperience:
        return TranslatedExperience(position=f"{position} (traducido)", description=f"{description} (traducido)")

    async def generate_cv_draft(self, free_text: str, language: str) -> GeneratedCvDraft:
        if self._cv_draft is not None:
            return self._cv_draft
        return GeneratedCvDraft(bio=f"Resumen generado a partir de: {free_text}")

    async def generate_text(self, field: str, context: str, language: str) -> str:
        return f"texto generado para {field} ({context})"


class FakeEventPublisher(EventPublisher):
    """Implementación falsa de EventPublisher para pruebas. Nunca llama a Service Bus."""

    def __init__(self) -> None:
        self.published: list[dict] = []

    async def publish(self, *, subject: str, message_id: str, body: dict) -> None:
        self.published.append({"subject": subject, "message_id": message_id, "body": body})
