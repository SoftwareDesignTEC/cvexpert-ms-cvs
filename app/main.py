from http.client import responses as http_status_phrases

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers import ai, cvs, templates
from app.domain.errors import NotFoundError, ValidationError
from app.domain.models import Error
from app.llm.base import LLMError, LLMProviderError, LLMRateLimitError, LLMTimeoutError

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


@app.exception_handler(LLMTimeoutError)
async def handle_llm_timeout(request: Request, exc: LLMTimeoutError) -> JSONResponse:
    return _error_response(503, "ServiceUnavailable", "El servicio de IA no respondió a tiempo.")


@app.exception_handler(LLMRateLimitError)
async def handle_llm_rate_limit(request: Request, exc: LLMRateLimitError) -> JSONResponse:
    return _error_response(
        429, "RateLimitExceeded", "Límite de solicitudes al servicio de IA alcanzado, intenta de nuevo más tarde."
    )


@app.exception_handler(LLMProviderError)
async def handle_llm_provider_error(request: Request, exc: LLMProviderError) -> JSONResponse:
    return _error_response(502, "BadGateway", "El servicio de IA no está disponible en este momento.")


@app.exception_handler(LLMError)
async def handle_llm_error(request: Request, exc: LLMError) -> JSONResponse:
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
