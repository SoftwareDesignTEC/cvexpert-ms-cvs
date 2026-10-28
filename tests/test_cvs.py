import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.mongo import get_database
from tests.fake_mongo import FakeDatabase


def _cv(id: str, user_id: str, title: str) -> dict:
    return {
        "id": id,
        "userId": user_id,
        "title": title,
        "templateId": "t1",
        "thumbnailUrl": None,
        "createdAt": 1700000000000,
        "updatedAt": 1700000000000,
        "personalInfo": {"fullName": "Ana Perez", "email": "ana@example.com"},
        "workExperiences": [],
        "education": [],
        "skills": [],
        "languages": [],
        "certifications": [],
    }


CVS = [
    _cv("cv1", "u1", "Backend Developer CV"),
    _cv("cv2", "u1", "Frontend Developer CV"),
    _cv("cv3", "u2", "Other user CV"),
]

TEMPLATES = [
    {
        "id": "t1",
        "name": "Minimal",
        "description": "Plantilla minimalista",
        "previewUrl": "https://example.com/t1.png",
        "category": "simple",
        "isPremium": False,
        "availableOffline": True,
    }
]

AUTH_HEADERS = {"X-User-Id": "u1", "X-User-Email": "a@b.com"}

CV_INPUT_BODY = {
    "title": "Mi CV",
    "templateId": "t1",
    "personalInfo": {"fullName": "Ana Perez", "email": "ana@example.com"},
    "workExperiences": [],
    "education": [],
    "skills": [],
    "languages": [],
    "certifications": [],
}


@pytest.fixture
def client():
    app.dependency_overrides[get_database] = lambda: FakeDatabase(
        {"cvs": [dict(cv) for cv in CVS], "templates": [dict(t) for t in TEMPLATES]}
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_database, None)


def test_list_cvs_filters_by_authenticated_user(client):
    response = client.get("/cvs", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["totalRecords"] == 2
    ids = {item["id"] for item in body["items"]}
    assert ids == {"cv1", "cv2"}


def test_list_cvs_filters_by_search(client):
    response = client.get("/cvs", params={"search": "frontend"}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["totalRecords"] == 1
    assert body["items"][0]["id"] == "cv2"


def test_list_cvs_requires_auth_headers(client):
    response = client.get("/cvs")
    assert response.status_code == 401


def test_get_cv_by_id(client):
    response = client.get("/cvs/cv1", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["id"] == "cv1"


def test_get_cv_by_id_not_found_for_other_user(client):
    response = client.get("/cvs/cv3", headers=AUTH_HEADERS)
    assert response.status_code == 404


def test_create_cv_sets_server_fields(client):
    response = client.post("/cvs", headers=AUTH_HEADERS, json=CV_INPUT_BODY)
    assert response.status_code == 201
    body = response.json()
    assert body["userId"] == "u1"
    assert body["thumbnailUrl"] == "https://example.com/t1.png"
    assert isinstance(body["id"], str) and body["id"]
    assert isinstance(body["createdAt"], int)
    assert body["createdAt"] == body["updatedAt"]


def test_create_cv_invalid_template_returns_400(client):
    body = {**CV_INPUT_BODY, "templateId": "no-existe"}
    response = client.post("/cvs", headers=AUTH_HEADERS, json=body)
    assert response.status_code == 400
    assert response.json()["errors"]["templateId"]


def test_create_cv_missing_required_field_returns_400(client):
    body = {k: v for k, v in CV_INPUT_BODY.items() if k != "title"}
    response = client.post("/cvs", headers=AUTH_HEADERS, json=body)
    assert response.status_code == 400
    assert response.json()["statusCode"] == 400


def test_update_cv_replaces_and_bumps_updated_at(client):
    body = {**CV_INPUT_BODY, "title": "Titulo actualizado"}
    response = client.put("/cvs/cv1", headers=AUTH_HEADERS, json=body)
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Titulo actualizado"
    assert updated["createdAt"] == 1700000000000
    assert updated["updatedAt"] >= updated["createdAt"]


def test_update_cv_not_found_returns_404(client):
    response = client.put("/cvs/no-existe", headers=AUTH_HEADERS, json=CV_INPUT_BODY)
    assert response.status_code == 404


def test_delete_cv_returns_204_then_404_on_repeat(client):
    response = client.delete("/cvs/cv1", headers=AUTH_HEADERS)
    assert response.status_code == 204

    response = client.delete("/cvs/cv1", headers=AUTH_HEADERS)
    assert response.status_code == 404
