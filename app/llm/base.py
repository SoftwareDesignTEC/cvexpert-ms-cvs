from abc import ABC, abstractmethod


class LLMAdapter(ABC):
    @abstractmethod
    async def expand_experience(self, text: str) -> str:
        ...

    @abstractmethod
    async def translate_experience(self, text: str, target_language: str) -> str:
        ...
