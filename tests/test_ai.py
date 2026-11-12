import pytest
from fastapi.testclient import TestClient

from app.events.factory import get_event_publisher
from app.llm.base import (
    GeneratedCvDraft,
    LLMAdapter,
    LLMNonsenseInputError,
    LLMTimeoutError,
    TranslatedExperience,
)
from app.llm.factory import get_llm_adapter
from app.main import app
from app.repositories.mongo import get_database
from tests.fake_mongo import FakeDatabase
from tests.fakes import FakeEventPublisher, FakeLLMAdapter

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

TEMPLATES = [
    {
        "id": "t1",
        "name": "Minimal",
        "description": "Plantilla minimalista",
        "previewUrl": "https://example.com/t1.png",
        "category": "simple",
        "isPremium": False,
        "availableOffline": True,
    },
    {
        "id": "minimal",
        "name": "Minimal",
        "description": "Plantilla minimalista",
        "previewUrl": "https://example.com/minimal.png",
        "category": "simple",
        "isPremium": False,
        "availableOffline": True,
    },
]


class TimeoutLLMAdapter(LLMAdapter):
    async def expand_experience(self, company, position, description, type, language) -> str:
        raise LLMTimeoutError("boom")

    async def translate_experience(
        self, type, position, description, language, organization=None
    ) -> TranslatedExperience:
        raise LLMTimeoutError("boom")

    async def generate_cv_draft(self, free_text, language) -> GeneratedCvDraft:
        raise LLMTimeoutError("boom")

    async def generate_text(self, field, context, language) -> str:
        raise LLMTimeoutError("boom")


class NonsenseLLMAdapter(LLMAdapter):
    async def expand_experience(self, company, position, description, type, language) -> str:
        raise LLMNonsenseInputError("no tiene sentido")

    async def translate_experience(
        self, type, position, description, language, organization=None
    ) -> TranslatedExperience:
        raise LLMNonsenseInputError("no tiene sentido")

    async def generate_cv_draft(self, free_text, language) -> GeneratedCvDraft:
        raise LLMNonsenseInputError("no tiene sentido")

    async def generate_text(self, field, context, language) -> str:
        raise LLMNonsenseInputError("no tiene sentido")


@pytest.fixture
def client():
    db = FakeDatabase({"templates": [dict(t) for t in TEMPLATES]})
    app.dependency_overrides[get_llm_adapter] = lambda: FakeLLMAdapter()
    app.dependency_overrides[get_database] = lambda: db
    app.dependency_overrides[get_event_publisher] = lambda: FakeEventPublisher()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_llm_adapter, None)
    app.dependency_overrides.pop(get_database, None)
    app.dependency_overrides.pop(get_event_publisher, None)


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


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/cvs/ai/expand-experience", EXPAND_BODY),
        ("/cvs/ai/translate-experience", TRANSLATE_BODY),
        ("/cvs/ai/generate-text", {"field": "profileBio", "context": "asdkjaskdj", "language": "es"}),
        (
            "/cvs/ai/generate-cv",
            {"fullName": "Ana", "freeText": "asdkjaskdj", "language": "es"},
        ),
    ],
)
def test_nonsense_input_maps_to_400(path, body):
    app.dependency_overrides[get_llm_adapter] = lambda: NonsenseLLMAdapter()
    app.dependency_overrides[get_database] = lambda: FakeDatabase(
        {"templates": [dict(t) for t in TEMPLATES]}
    )
    app.dependency_overrides[get_event_publisher] = lambda: FakeEventPublisher()
    with TestClient(app) as test_client:
        response = test_client.post(path, headers=AUTH_HEADERS, json=body)
    app.dependency_overrides.pop(get_llm_adapter, None)
    app.dependency_overrides.pop(get_database, None)
    app.dependency_overrides.pop(get_event_publisher, None)

    assert response.status_code == 400
    body = response.json()
    assert body["statusCode"] == 400
    assert body["message"]


def test_llm_timeout_maps_to_503_without_leaking_provider_details():
    app.dependency_overrides[get_llm_adapter] = lambda: TimeoutLLMAdapter()
    app.dependency_overrides[get_database] = lambda: FakeDatabase({})
    with TestClient(app) as test_client:
        response = test_client.post("/cvs/ai/expand-experience", headers=AUTH_HEADERS, json=EXPAND_BODY)
    app.dependency_overrides.pop(get_llm_adapter, None)
    app.dependency_overrides.pop(get_database, None)

    assert response.status_code == 503
    body = response.json()
    assert body["statusCode"] == 503
    assert "boom" not in body["message"]


def test_generate_text(client):
    body = {"field": "profileBio", "context": "Ingeniero con 5 años de experiencia", "language": "es"}
    response = client.post("/cvs/ai/generate-text", headers=AUTH_HEADERS, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "text": "texto generado para profileBio (Ingeniero con 5 años de experiencia)"
    }


def test_generate_text_requires_auth(client):
    response = client.post(
        "/cvs/ai/generate-text",
        json={"field": "experienceDescription", "context": "ctx", "language": "es"},
    )
    assert response.status_code == 401


def test_generate_cv_creates_full_cv(client):
    body = {
        "title": "CV generado",
        "templateId": "t1",
        "fullName": "Ana Perez",
        "phone": "8888-8888",
        "freeText": "Trabajé 3 años en Acme como desarrolladora backend",
        "language": "es",
    }
    response = client.post("/cvs/ai/generate-cv", headers=AUTH_HEADERS, json=body)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "CV generado"
    assert created["personalInfo"]["fullName"] == "Ana Perez"
    assert created["personalInfo"]["email"] == "a@b.com"
    assert created["personalInfo"]["bio"] == "Resumen generado a partir de: " + body["freeText"]


def test_generate_cv_defaults_title_and_template_when_omitted(client):
    body = {
        "fullName": "Ana Perez",
        "freeText": "Trabajé 3 años en Acme como desarrolladora backend",
        "language": "es",
    }
    response = client.post("/cvs/ai/generate-cv", headers=AUTH_HEADERS, json=body)
    assert response.status_code == 201
    created = response.json()
    assert created["templateId"] == "minimal"
    assert created["title"].startswith("CV generado el ")


def test_generate_cv_result_can_be_resaved_via_put_unchanged(client):
    draft = GeneratedCvDraft(
        bio="Bio",
        workExperiences=[
            {
                "company": "Pulpería La Esquina",
                "position": "Cajero",
                "description": "Atención al cliente y cobros",
                "type": "formal",
                # sin "current": el modelo no siempre lo manda
            }
        ],
        education=[{"institution": "TEC", "degree": "Ingeniería", "field": "Software"}],
        skills=[{"name": "Excel", "level": "advanced"}],  # sin category
        languages=[{"name": "Inglés", "level": "advanced"}],
        certifications=[],
    )
    client.app.dependency_overrides[get_llm_adapter] = lambda: FakeLLMAdapter(cv_draft=draft)

    body = {
        "fullName": "Ana Perez",
        "freeText": "irrelevante, el adaptador falso ignora esto",
        "language": "es",
    }
    created_response = client.post("/cvs/ai/generate-cv", headers=AUTH_HEADERS, json=body)
    assert created_response.status_code == 201
    created = created_response.json()

    for experience in created["workExperiences"]:
        assert isinstance(experience["current"], bool)
    for skill in created["skills"]:
        assert isinstance(skill.get("category"), str) and skill["category"]

    resave_response = client.put(f"/cvs/{created['id']}", headers=AUTH_HEADERS, json=created)
    assert resave_response.status_code == 200
    assert resave_response.json()["id"] == created["id"]


def test_generate_cv_requires_auth(client):
    response = client.post(
        "/cvs/ai/generate-cv",
        json={
            "title": "CV",
            "templateId": "t1",
            "fullName": "Ana",
            "freeText": "texto",
            "language": "es",
        },
    )
    assert response.status_code == 401


def test_generate_cv_normalizes_and_discards_unusable_entries(client):
    from app.llm.base import GeneratedCvDraft
    from app.llm.factory import get_llm_adapter
    from tests.fakes import FakeLLMAdapter

    draft = GeneratedCvDraft(
        bio="Bio",
        workExperiences=[
            {
                "company": "Acme",
                "position": "Dev",
                "startDate": "2020-01",
                "current": False,
                "endDate": "2022-06",
                "description": "hice cosas",
                "type": "formal",
            },
            {
                "position": "Voluntario",
                "startDate": "2019",
                "current": True,
                "description": "ayude",
                "type": "volunteer",
            },
            {"position": "sin fecha, se guarda con fecha aproximada", "current": False, "description": "x", "type": "informal"},
            {"position": "formal sin empresa, se descarta", "current": False, "description": "x", "type": "formal"},
        ],
        education=[{"institution": "TEC", "current": True, "startDate": None}],
        skills=[{"name": "Python", "level": "advanced"}, {"name": "sin nivel, se descarta"}],
        languages=[{"name": "Inglés", "level": "advanced"}],
        certifications=[],
    )
    client.app.dependency_overrides[get_llm_adapter] = lambda: FakeLLMAdapter(cv_draft=draft)

    body = {
        "title": "CV generado",
        "templateId": "t1",
        "fullName": "Ana Perez",
        "freeText": "irrelevante, el adaptador falso ignora esto",
        "language": "es",
    }
    response = client.post("/cvs/ai/generate-cv", headers=AUTH_HEADERS, json=body)

    assert response.status_code == 201
    created = response.json()
    assert len(created["workExperiences"]) == 3
    assert {e["type"] for e in created["workExperiences"]} == {"formal", "volunteer", "informal"}
    formal = next(e for e in created["workExperiences"] if e["type"] == "formal")
    assert formal["company"] == "Acme"
    volunteer = next(e for e in created["workExperiences"] if e["type"] == "volunteer")
    assert volunteer["company"] is None
    without_date = next(e for e in created["workExperiences"] if e["type"] == "informal")
    assert isinstance(without_date["startDate"], int)

    assert len(created["education"]) == 1
    assert created["education"][0]["institution"] == "TEC"
    assert created["education"][0]["degree"] == ""
    assert isinstance(created["education"][0]["startDate"], int)

    assert len(created["skills"]) == 1
    assert created["skills"][0]["name"] == "Python"
    assert created["skills"][0]["category"] == "General"


def test_unexpected_error_maps_to_500_with_contract_shape():
    def _broken_adapter():
        raise RuntimeError("Proveedor de LLM no soportado: none")

    app.dependency_overrides[get_llm_adapter] = _broken_adapter
    app.dependency_overrides[get_database] = lambda: FakeDatabase({})
    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.post("/cvs/ai/expand-experience", headers=AUTH_HEADERS, json=EXPAND_BODY)
    app.dependency_overrides.pop(get_llm_adapter, None)
    app.dependency_overrides.pop(get_database, None)

    assert response.status_code == 500
    body = response.json()
    assert body["statusCode"] == 500
    assert "Proveedor de LLM" not in body["message"]
