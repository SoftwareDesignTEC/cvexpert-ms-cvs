from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranslatedExperience:
    position: str
    description: str


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
