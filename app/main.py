import base64
import hashlib
import logging
from http.client import responses as http_status_phrases

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers import ai, cvs, templates
from app.config import settings
from app.domain.errors import NotFoundError, ValidationError
from app.domain.models import Error
from app.llm.base import (
    LLMError,
    LLMNonsenseInputError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="cvexpert-ms-cvs")

app.include_router(cvs.router)
app.include_router(templates.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}


def _error_response(
    status_code: int, error: str, message: str, errors: dict[str, str] | None = None
) -> JSONResponse:
    body = Error(statusCode=status_code, error=error, message=message, errors=errors)
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


def _allowed_cert_thumbprints() -> set[str]:
    return {
        t.strip().replace(":", "").upper()
        for t in settings.apim_cert_thumbprints.split(",")
        if t.strip()
    }


@app.middleware("http")
async def require_apim_client_cert(request: Request, call_next):
    allowed = _allowed_cert_thumbprints()
    if allowed and request.url.path != "/health":
        cert = request.headers.get("X-ARR-ClientCert", "")
        try:
            thumbprint = hashlib.sha1(base64.b64decode(cert)).hexdigest().upper()
        except ValueError:
            thumbprint = ""
        if thumbprint not in allowed:
            return _error_response(403, "Forbidden", "La llamada no trae el certificado de APIM.")
    return await call_next(request)


@app.exception_handler(LLMTimeoutError)
async def handle_llm_timeout(request: Request, exc: LLMTimeoutError) -> JSONResponse:
    return _error_response(503, "ServiceUnavailable", "El servicio de IA no respondió a tiempo.")


@app.exception_handler(LLMRateLimitError)
async def handle_llm_rate_limit(request: Request, exc: LLMRateLimitError) -> JSONResponse:
    logger.warning("Rate limit del proveedor de IA en %s %s", request.method, request.url.path)
    return _error_response(
        429, "RateLimitExceeded", "Límite de solicitudes al servicio de IA alcanzado, intenta de nuevo más tarde."
    )


@app.exception_handler(LLMNonsenseInputError)
async def handle_llm_nonsense_input(request: Request, exc: LLMNonsenseInputError) -> JSONResponse:
    return _error_response(400, "BadRequest", str(exc))


@app.exception_handler(LLMProviderError)
async def handle_llm_provider_error(request: Request, exc: LLMProviderError) -> JSONResponse:
    logger.error("Error del proveedor de IA en %s %s", request.method, request.url.path, exc_info=exc)
    return _error_response(502, "BadGateway", "El servicio de IA no está disponible en este momento.")


@app.exception_handler(LLMError)
async def handle_llm_error(request: Request, exc: LLMError) -> JSONResponse:
    logger.error("Error del proveedor de IA en %s %s", request.method, request.url.path, exc_info=exc)
    return _error_response(502, "BadGateway", "El servicio de IA no está disponible en este momento.")


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    error = http_status_phrases.get(exc.status_code, "Error").replace(" ", "")
    return _error_response(exc.status_code, error, str(exc.detail))


@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return _error_response(404, "NotFound", str(exc) or "No encontrado.")


@app.exception_handler(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return _error_response(400, "BadRequest", "Solicitud inválida.", errors=exc.errors)


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors: dict[str, str] = {}
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"] if p != "body")
        errors[loc or "body"] = err["msg"]
    return _error_response(400, "BadRequest", "Solicitud inválida.", errors=errors)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error no manejado en %s %s", request.method, request.url.path)
    return _error_response(500, "InternalServerError", "Ocurrió un error inesperado.")
