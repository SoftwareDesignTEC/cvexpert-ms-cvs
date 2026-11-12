from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TranslatedExperience:
    position: str
    description: str


@dataclass
class GeneratedCvDraft:
    bio: str | None = None
    workExperiences: list[dict] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    skills: list[dict] = field(default_factory=list)
    languages: list[dict] = field(default_factory=list)
    certifications: list[dict] = field(default_factory=list)


class LLMError(Exception):
    """Error genérico del adaptador LLM, sin detalles internos del proveedor."""


class LLMTimeoutError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMProviderError(LLMError):
    pass


class LLMNonsenseInputError(LLMError):
    """El texto que mandó el usuario no tiene sentido; el adaptador se niega a transformarlo."""


NONSENSE_SENTINEL = "###SIN_SENTIDO###"

NONSENSE_MESSAGE = (
    "El texto no parece tener sentido para generar contenido de currículum. "
    "Revisá lo que escribiste e intentá de nuevo."
)

NONSENSE_INSTRUCTION = (
    f"Si el texto de entrada no tiene sentido, está vacío de contenido real, es ilegible "
    f"o no tiene relación alguna con un currículum (por ejemplo, caracteres al azar, o un "
    f"tema completamente ajeno), no lo transformes: responde únicamente con {NONSENSE_SENTINEL} "
    "y nada más."
)


class LLMAdapter(ABC):
    @abstractmethod
    async def expand_experience(
        self, company: str, position: str, description: str, type: str, language: str
    ) -> str:
        ...

    @abstractmethod
    async def translate_experience(
        self,
        type: str,
        position: str,
        description: str,
        language: str,
        organization: str | None = None,
    ) -> TranslatedExperience:
        ...

    @abstractmethod
    async def generate_cv_draft(self, free_text: str, language: str) -> GeneratedCvDraft:
        ...

    @abstractmethod
    async def generate_text(self, field: str, context: str, language: str) -> str:
        ...
