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
