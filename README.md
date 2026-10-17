# cvexpert-ms-cvs

Microservicio de CVs con IA del proyecto CVExpert (TEC, Diseño de Software, Fase II).

Stack: Python 3.12, FastAPI, MongoDB (Cosmos DB con API de MongoDB en Azure), GitHub Actions, Azure App Service Linux.

## Requisitos

- Python 3.12
- Una instancia de MongoDB accesible (local o Cosmos DB con API de Mongo)

## Instalación

```bash
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env  # completar con valores reales, nunca commitear este archivo
```

## Comandos

| Acción | Comando |
| --- | --- |
| Correr en desarrollo | `uvicorn app.main:app --reload` |
| Pruebas | `pytest` |
| Lint | `ruff check .` |

## Estructura

```
app/
  api/          routers y dependencias (auth por headers de APIM)
  domain/       modelos
  services/     lógica de negocio
  repositories/ acceso a Mongo
  llm/          adaptador de IA reemplazable
  prompts/      prompts usados por el adaptador de IA
tests/
```

## Identidad

La identidad del usuario llega únicamente por los encabezados que inyecta APIM: `X-User-Id`, `X-User-Email` (y `X-User-Role` en rutas de administración). Si faltan, la API responde 401.

## Contrato

El contrato de la API se define primero en `docs/openapi.yaml` (fuente de verdad). Incluye los 6 endpoints de la Fase I (5 de currículums, 1 de plantillas) y los endpoints de IA (expandir experiencia, traducir experiencia no laboral).

## Convenciones

- Ramas: `feat/...`, `fix/...`, `chore/...`
- Commits en español, cortos, en modo imperativo
- Todo cambio entra por PR revisado; no se hace push directo a `main`
- Cada endpoint nuevo lleva prueba unitaria
