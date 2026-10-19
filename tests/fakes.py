from app.llm.base import LLMAdapter, TranslatedExperience


class FakeLLMAdapter(LLMAdapter):
    """Implementación falsa de LLMAdapter para pruebas. Nunca llama a un proveedor real."""

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
