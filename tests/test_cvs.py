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

AUTH_HEADERS = {"X-User-Id": "u1", "X-User-Email": "a@b.com"}


@pytest.fixture
def client():
    app.dependency_overrides[get_database] = lambda: FakeDatabase({"cvs": CVS})
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
