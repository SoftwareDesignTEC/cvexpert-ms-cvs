from app.config import settings
from app.llm.base import LLMAdapter
from app.llm.gemini import GeminiAdapter


def get_llm_adapter() -> LLMAdapter:
    if settings.llm_provider == "gemini":
        return GeminiAdapter()
    raise RuntimeError(f"Proveedor de LLM no soportado: {settings.llm_provider}")
