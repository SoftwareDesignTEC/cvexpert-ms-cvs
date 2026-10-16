from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_cvs_requires_identity_headers():
    response = client.get("/cvs")
    assert response.status_code == 401


def test_cvs_rejects_when_role_header_missing_id():
    response = client.get("/cvs", headers={"X-User-Email": "a@b.com"})
    assert response.status_code == 401
