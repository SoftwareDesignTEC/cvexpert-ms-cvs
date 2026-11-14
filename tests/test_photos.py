import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage.factory import get_photo_storage
from tests.fakes import FakePhotoStorage

AUTH_HEADERS = {"X-User-Id": "u1", "X-User-Email": "a@b.com"}


@pytest.fixture
def storage():
    return FakePhotoStorage()


@pytest.fixture
def client(storage):
    app.dependency_overrides[get_photo_storage] = lambda: storage
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_photo_storage, None)


def test_upload_photo_returns_url(client, storage):
    response = client.post(
        "/cvs/photos",
        headers=AUTH_HEADERS,
        files={"file": ("foto.jpg", io.BytesIO(b"contenido-falso"), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["url"].startswith("https://fake.blob.core.windows.net/cv-photos/")
    assert len(storage.uploaded) == 1
    assert storage.uploaded[0]["content_type"] == "image/jpeg"
    assert storage.uploaded[0]["extension"] == "jpg"


def test_upload_photo_requires_auth(client):
    response = client.post(
        "/cvs/photos",
        files={"file": ("foto.jpg", io.BytesIO(b"contenido-falso"), "image/jpeg")},
    )
    assert response.status_code == 401


def test_upload_photo_rejects_unsupported_type(client):
    response = client.post(
        "/cvs/photos",
        headers=AUTH_HEADERS,
        files={"file": ("archivo.txt", io.BytesIO(b"hola"), "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["error"] == "UnsupportedMediaType"


def test_upload_photo_rejects_file_too_large(client):
    big_content = b"a" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/cvs/photos",
        headers=AUTH_HEADERS,
        files={"file": ("foto.jpg", io.BytesIO(big_content), "image/jpeg")},
    )
    assert response.status_code == 413
    assert response.json()["error"] == "PayloadTooLarge"


def test_upload_photo_accepts_png_and_webp(client):
    for content_type, extension in (("image/png", "png"), ("image/webp", "webp")):
        response = client.post(
            "/cvs/photos",
            headers=AUTH_HEADERS,
            files={"file": (f"foto.{extension}", io.BytesIO(b"contenido"), content_type)},
        )
        assert response.status_code == 201
