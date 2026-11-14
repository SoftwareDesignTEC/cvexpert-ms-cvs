from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import CurrentUserDep
from app.domain.models import PhotoUploadResponse
from app.services.photos import upload_photo
from app.storage.factory import PhotoStorageDep

router = APIRouter(prefix="/cvs/photos", tags=["cvs"])


@router.post("", response_model=PhotoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv_photo(
    user: CurrentUserDep, storage: PhotoStorageDep, file: Annotated[UploadFile, File()]
):
    content = await file.read()
    url = await upload_photo(storage, content=content, content_type=file.content_type)
    return PhotoUploadResponse(url=url)
