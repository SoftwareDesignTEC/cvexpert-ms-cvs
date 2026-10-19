import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.mongo import get_database
from tests.fake_mongo import FakeDatabase

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
        "id": "t2",
        "name": "Executive",
        "description": "Plantilla ejecutiva",
        "previewUrl": "https://example.com/t2.png",
        "category": "formal",
        "isPremium": True,
        "availableOffline": False,
    },
]

AUTH_HEADERS = {"X-User-Id": "u1", "X-User-Email": "a@b.com"}


@pytest.fixture
def client():
    app.dependency_overrides[get_database] = lambda: FakeDatabase({"templates": TEMPLATES})
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_database, None)


def test_list_templates_returns_paginated_items(client):
    response = client.get("/templates", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["totalRecords"] == 2
    assert body["page"] == 1
    assert body["pageSize"] == 20
    assert len(body["items"]) == 2


def test_list_templates_filters_by_search(client):
    response = client.get("/templates", params={"search": "exec"}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["totalRecords"] == 1
    assert body["items"][0]["name"] == "Executive"


def test_list_templates_paginates(client):
    response = client.get("/templates", params={"page": 1, "pageSize": 1}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["totalRecords"] == 2
    assert len(body["items"]) == 1


def test_list_templates_requires_auth_headers(client):
    response = client.get("/templates")
    assert response.status_code == 401
