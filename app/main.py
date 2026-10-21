from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import ai, cvs, templates
from app.domain.models import Error
from app.llm.base import LLMError, LLMProviderError, LLMRateLimitError, LLMTimeoutError

app = FastAPI(title="cvexpert-ms-cvs")

app.include_router(cvs.router)
app.include_router(templates.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}


def _llm_error_response(status_code: int, error: str, message: str) -> JSONResponse:
    body = Error(statusCode=status_code, error=error, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


@app.exception_handler(LLMTimeoutError)
async def handle_llm_timeout(request: Request, exc: LLMTimeoutError) -> JSONResponse:
    return _llm_error_response(503, "ServiceUnavailable", "El servicio de IA no respondió a tiempo.")


@app.exception_handler(LLMRateLimitError)
async def handle_llm_rate_limit(request: Request, exc: LLMRateLimitError) -> JSONResponse:
    return _llm_error_response(
        429, "RateLimitExceeded", "Límite de solicitudes al servicio de IA alcanzado, intenta de nuevo más tarde."
    )


@app.exception_handler(LLMProviderError)
async def handle_llm_provider_error(request: Request, exc: LLMProviderError) -> JSONResponse:
    return _llm_error_response(502, "BadGateway", "El servicio de IA no está disponible en este momento.")


@app.exception_handler(LLMError)
async def handle_llm_error(request: Request, exc: LLMError) -> JSONResponse:
    return _llm_error_response(502, "BadGateway", "El servicio de IA no está disponible en este momento.")
