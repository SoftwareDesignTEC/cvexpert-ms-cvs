import uuid

from azure.core.exceptions import AzureError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from app.config import settings
from app.storage.base import PhotoStorage, PhotoStorageError

CACHE_CONTROL = "public, max-age=31536000, immutable"


class AzureBlobPhotoStorage(PhotoStorage):
    def __init__(self, connection_string: str | None = None, container: str | None = None) -> None:
        self._connection_string = (
            connection_string if connection_string is not None else settings.azure_storage_connection_string
        )
        self._container = container if container is not None else settings.azure_storage_container
        if not self._connection_string:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING no está configurada")

    async def upload(self, *, content: bytes, content_type: str, extension: str) -> str:
        blob_name = f"{uuid.uuid4()}.{extension}"
        try:
            async with BlobServiceClient.from_connection_string(self._connection_string) as service_client:
                blob_client = service_client.get_blob_client(self._container, blob_name)
                await blob_client.upload_blob(
                    content,
                    overwrite=False,
                    content_settings=ContentSettings(content_type=content_type, cache_control=CACHE_CONTROL),
                )
                return blob_client.url
        except AzureError as exc:
            raise PhotoStorageError("No se pudo subir el archivo al almacenamiento") from exc
