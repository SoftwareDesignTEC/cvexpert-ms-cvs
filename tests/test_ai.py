import pytest
from fastapi.testclient import TestClient

from app.llm.base import LLMAdapter, LLMTimeoutError, TranslatedExperience
from app.llm.factory import get_llm_adapter
from app.main import app
from tests.fakes import FakeLLMAdapter

AUTH_HEADERS = {"X-User-Id": "u1", "X-User-Email": "a@b.com"}

EXPAND_BODY = {
    "company": "Acme",
    "position": "Backend Developer",
    "description": "hice cosas",
    "type": "formal",
    "language": "es",
}

TRANSLATE_BODY = {
    "type": "volunteer",
    "position": "Voluntario",
    "description": "ayude en un refugio",
    "language": "en",
}


class TimeoutLLMAdapter(LLMAdapter):
    async def expand_experience(self, company, position, description, type, language) -> str:
        raise LLMTimeoutError("boom")

    async def translate_experience(
        self, type, position, description, language, organization=None
    ) -> TranslatedExperience:
        raise LLMTimeoutError("boom")


@pytest.fixture
def client():
    app.dependency_overrides[get_llm_adapter] = lambda: FakeLLMAdapter()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_llm_adapter, None)


def test_expand_experience(client):
    response = client.post("/cvs/ai/expand-experience", headers=AUTH_HEADERS, json=EXPAND_BODY)
    assert response.status_code == 200
    assert response.json() == {"description": "hice cosas (expandida)"}


def test_translate_experience(client):
    response = client.post("/cvs/ai/translate-experience", headers=AUTH_HEADERS, json=TRANSLATE_BODY)
    assert response.status_code == 200
    assert response.json() == {
        "position": "Voluntario (traducido)",
        "description": "ayude en un refugio (traducido)",
    }


def test_expand_experience_requires_auth(client):
    response = client.post("/cvs/ai/expand-experience", json=EXPAND_BODY)
    assert response.status_code == 401


def test_llm_timeout_maps_to_503_without_leaking_provider_details():
    app.dependency_overrides[get_llm_adapter] = lambda: TimeoutLLMAdapter()
    with TestClient(app) as test_client:
        response = test_client.post("/cvs/ai/expand-experience", headers=AUTH_HEADERS, json=EXPAND_BODY)
    app.dependency_overrides.pop(get_llm_adapter, None)

    assert response.status_code == 503
    body = response.json()
    assert body["statusCode"] == 503
    assert "boom" not in body["message"]
