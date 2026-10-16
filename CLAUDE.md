# cvexpert-ms-cvs

Microservicio de CVs con IA del proyecto CVExpert (TEC, Diseño de Software, Fase II).
Stack: Python 3.12, FastAPI, MongoDB (Cosmos DB con API de MongoDB en Azure), GitHub Actions, Azure App Service Linux.

## Reglas no negociables
- Nunca secretos en el código, en el repo ni en el chat. Todo por variables de entorno; `.env` está en .gitignore y solo se versiona `.env.example` con valores falsos.
- Todas las fechas son epoch en milisegundos UTC (int). Nunca strings de fecha ni zonas horarias en la API.
- La identidad sale SOLO de los encabezados que pone APIM: X-User-Id y X-User-Email (X-User-Role en rutas de admin). Nunca de un token ni del body. Si faltan, 401.
- Este servicio no llama a otros microservicios.
- La rama principal está protegida: todo cambio entra por PR con revisión de otra persona. Nunca hacer push directo a main.
- El LLM va detrás de un adaptador reemplazable (app/llm). Los prompts viven en app/prompts/ dentro del repo.

## Contrato
- 6 endpoints de la Fase I (5 de currículums, 1 de plantillas): mismo contrato que ya usan web y Android. No cambiarlo sin avisar al equipo.
- Endpoints de IA: expandir experiencia y traducir experiencia no laboral.
- El contrato se define primero en docs/openapi.yaml (fuente de verdad).

## Estructura
app/api (routers y dependencias), app/domain (modelos), app/services (lógica), app/repositories (Mongo), app/llm (adaptador), app/prompts, tests/

## Comandos
- Instalar: pip install -r requirements.txt -r requirements-dev.txt
- Correr: uvicorn app.main:app --reload
- Pruebas: pytest
- Lint: ruff check .

## Convenciones
- Ramas: feat/..., fix/..., chore/... ; commits en español, cortos, imperativo.
- Cada endpoint nuevo lleva prueba unitaria.
