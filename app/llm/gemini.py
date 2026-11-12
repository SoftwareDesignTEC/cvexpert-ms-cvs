import json

import httpx

from app.config import settings
from app.llm.base import (
    NONSENSE_MESSAGE,
    NONSENSE_SENTINEL,
    GeneratedCvDraft,
    LLMAdapter,
    LLMNonsenseInputError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    TranslatedExperience,
)
from app.prompts import expand_experience as expand_experience_prompt
from app.prompts import generate_cv as generate_cv_prompt
from app.prompts import generate_text as generate_text_prompt
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
        result = result.strip()
        if result == NONSENSE_SENTINEL:
            raise LLMNonsenseInputError(NONSENSE_MESSAGE)
        return result

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
            if data.get("invalid"):
                raise LLMNonsenseInputError(NONSENSE_MESSAGE)
            return TranslatedExperience(position=data["position"], description=data["description"])
        except (json.JSONDecodeError, KeyError) as exc:
            raise LLMProviderError("El proveedor de IA devolvió una respuesta inválida") from exc

    async def generate_cv_draft(self, free_text: str, language: str) -> GeneratedCvDraft:
        prompt = generate_cv_prompt.build_prompt(free_text, language)
        raw = await self._generate(prompt, response_schema=generate_cv_prompt.RESPONSE_SCHEMA)
        try:
            data = json.loads(raw)
            if data.get("invalid"):
                raise LLMNonsenseInputError(NONSENSE_MESSAGE)
            return GeneratedCvDraft(
                bio=data.get("bio"),
                workExperiences=data.get("workExperiences", []),
                education=data.get("education", []),
                skills=data.get("skills", []),
                languages=data.get("languages", []),
                certifications=data.get("certifications", []),
            )
        except json.JSONDecodeError as exc:
            raise LLMProviderError("El proveedor de IA devolvió una respuesta inválida") from exc

    async def generate_text(self, field: str, context: str, language: str) -> str:
        prompt = generate_text_prompt.build_prompt(field, context, language)
        result = await self._generate(prompt)
        result = result.strip()
        if result == NONSENSE_SENTINEL:
            raise LLMNonsenseInputError(NONSENSE_MESSAGE)
        return result
