from abc import ABC, abstractmethod


class PhotoStorageError(Exception):
    """El storage de archivos no respondió o rechazó la subida, sin detalle interno."""


class PhotoStorage(ABC):
    @abstractmethod
    async def upload(self, *, content: bytes, content_type: str, extension: str) -> str:
        """Sube el archivo y devuelve su URL pública y permanente."""
        ...
