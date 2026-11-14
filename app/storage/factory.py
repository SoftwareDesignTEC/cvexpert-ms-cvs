from typing import Annotated

from fastapi import Depends

from app.storage.azure_blob import AzureBlobPhotoStorage
from app.storage.base import PhotoStorage


def get_photo_storage() -> PhotoStorage:
    return AzureBlobPhotoStorage()


PhotoStorageDep = Annotated[PhotoStorage, Depends(get_photo_storage)]
