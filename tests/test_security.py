import base64
import hashlib

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_cert_check_is_noop_when_no_thumbprints_configured():
    assert settings.apim_cert_thumbprints == ""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_accessible_without_cert_even_when_required(monkeypatch):
    monkeypatch.setattr(settings, "apim_cert_thumbprints", "AAAABBBBCCCC")
    response = client.get("/health")
    assert response.status_code == 200


def test_request_without_cert_rejected_when_thumbprints_configured(monkeypatch):
    monkeypatch.setattr(settings, "apim_cert_thumbprints", "AAAABBBBCCCC")
    response = client.get("/templates", headers={"X-User-Id": "u1", "X-User-Email": "a@b.com"})
    assert response.status_code == 403
    assert response.json()["error"] == "Forbidden"


def test_request_with_matching_cert_thumbprint_is_not_blocked(monkeypatch):
    fake_cert_der = b"fake-cert-bytes"
    thumbprint = hashlib.sha1(fake_cert_der).hexdigest().upper()
    monkeypatch.setattr(settings, "apim_cert_thumbprints", thumbprint)
    cert_header = base64.b64encode(fake_cert_der).decode()

    response = client.get("/templates", headers={"X-ARR-ClientCert": cert_header})

    assert response.status_code != 403


def test_request_with_garbage_cert_header_rejected(monkeypatch):
    monkeypatch.setattr(settings, "apim_cert_thumbprints", "AAAABBBBCCCC")
    response = client.get("/templates", headers={"X-ARR-ClientCert": "no-es-base64-valido!!"})
    assert response.status_code == 403
