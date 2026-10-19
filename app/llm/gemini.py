import json

import httpx

from app.config import settings
from app.llm.base import (
    LLMAdapter,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    TranslatedExperience,
)
from app.prompts import expand_experience as expand_experience_prompt
from app.prompts import translate_experience as translate_experience_prompt

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key if api_key is not None else settings.gemini_api_key
        self._model = model if model is not None else settings.gemini_model
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY no está configurada")

    async def _generate(self, prompt: str, response_schema: dict | None = None) -> str:
        url = f"{GEMINI_BASE_URL}/{self._model}:generateContent"
        body: dict = {"contents": [{"parts": [{"text": prompt}]}]}
        if response_schema is not None:
            body["generationConfig"] = {
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
            }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, params={"key": self._api_key}, json=body)
                response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("El proveedor de IA no respondió a tiempo") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise LLMRateLimitError("Límite de solicitudes del proveedor de IA alcanzado") from exc
            raise LLMProviderError("El proveedor de IA devolvió un error") from exc
        except (httpx.RequestError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise LLMProviderError("El proveedor de IA no está disponible en este momento") from exc

    async def expand_experience(
        self, company: str, position: str, description: str, type: str, language: str
    ) -> str:
        prompt = expand_experience_prompt.build_prompt(company, position, description, type, language)
        result = await self._generate(prompt)
        return result.strip()

    async def translate_experience(
        self,
        type: str,
        position: str,
        description: str,
        language: str,
        organization: str | None = None,
    ) -> TranslatedExperience:
        prompt = translate_experience_prompt.build_prompt(
            type, position, description, language, organization
        )
        raw = await self._generate(prompt, response_schema=translate_experience_prompt.RESPONSE_SCHEMA)
        try:
            data = json.loads(raw)
            return TranslatedExperience(position=data["position"], description=data["description"])
        except (json.JSONDecodeError, KeyError) as exc:
            raise LLMProviderError("El proveedor de IA devolvió una respuesta inválida") from exc
