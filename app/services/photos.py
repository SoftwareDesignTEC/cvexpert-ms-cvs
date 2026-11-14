from app.domain.errors import FileTooLargeError, UnsupportedFileTypeError
from app.storage.base import PhotoStorage

MAX_BYTES = 5 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


async def upload_photo(storage: PhotoStorage, *, content: bytes, content_type: str | None) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedFileTypeError(
            "Tipo de archivo no soportado. Solo se aceptan image/jpeg, image/png o image/webp."
        )
    if len(content) > MAX_BYTES:
        raise FileTooLargeError("El archivo supera el tamaño máximo permitido de 5 MB.")

    extension = ALLOWED_CONTENT_TYPES[content_type]
    return await storage.upload(content=content, content_type=content_type, extension=extension)
