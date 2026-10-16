from fastapi import FastAPI

from app.api.routers import ai, cvs, templates

app = FastAPI(title="cvexpert-ms-cvs")

app.include_router(cvs.router)
app.include_router(templates.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}
