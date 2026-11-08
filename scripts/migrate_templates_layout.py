"""Siembra dos plantillas completas en Mongo (upsert), con layout real.

La coleccion `templates` en produccion esta vacia: sin esto, GET /templates
devuelve 0 resultados y nadie puede crear un CV (POST /cvs valida que
templateId exista). Este script crea dos plantillas completas desde cero
(no asume que ya existan), una de 1 columna y otra de 2.

Antes de correrlo:
1. Revisar previewUrl: son placeholders (placehold.co). Reemplazarlos por
   las imagenes reales de las plantillas en cuanto esten disponibles,
   corriendo el script de nuevo (es upsert, no rompe nada).
2. Que MONGODB_URI (en el entorno donde se corre) apunte a la base real, no
   a localhost. Ojo: esto escribe directo sobre datos de produccion.

Uso: python scripts/migrate_templates_layout.py
"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

LAYOUT_1_COLUMN = {
    "columns": 1,
    "colorScheme": "blue",
    "sections": [
        {
            "type": "header",
            "fields": ["personalInfo.fullName", "personalInfo.email", "personalInfo.phone"],
        },
        {
            "type": "list",
            "source": "workExperiences",
            "itemFields": ["position", "company", "startDate", "endDate", "current", "description"],
        },
        {
            "type": "list",
            "source": "education",
            "itemFields": ["degree", "institution", "startDate", "endDate", "current"],
        },
        {"type": "list", "source": "skills", "itemFields": ["name", "level"]},
        {"type": "list", "source": "languages", "itemFields": ["name", "level"]},
    ],
}

LAYOUT_2_COLUMNS = {
    "columns": 2,
    "colorScheme": "purple",
    "sections": [
        {
            "type": "header",
            "column": 1,
            "fields": ["personalInfo.fullName", "personalInfo.email", "personalInfo.phone"],
        },
        {
            "type": "list",
            "column": 1,
            "source": "workExperiences",
            "itemFields": ["position", "company", "startDate", "endDate", "current", "description"],
        },
        {
            "type": "list",
            "column": 1,
            "source": "education",
            "itemFields": ["degree", "institution", "startDate", "endDate", "current"],
        },
        {"type": "list", "column": 2, "source": "skills", "itemFields": ["name", "level"]},
        {"type": "list", "column": 2, "source": "languages", "itemFields": ["name", "level"]},
    ],
}

TEMPLATES = [
    {
        "id": "minimal",
        "name": "Minimal",
        "description": "Plantilla simple de una columna",
        "previewUrl": "https://placehold.co/400x560?text=Minimal",
        "category": "simple",
        "isPremium": False,
        "availableOffline": True,
        "layout": LAYOUT_1_COLUMN,
    },
    {
        "id": "executive",
        "name": "Executive",
        "description": "Plantilla ejecutiva de dos columnas",
        "previewUrl": "https://placehold.co/400x560?text=Executive",
        "category": "formal",
        "isPremium": False,
        "availableOffline": True,
        "layout": LAYOUT_2_COLUMNS,
    },
]


async def main() -> None:
    client = AsyncIOMotorClient(settings.mongodb_uri)
    collection = client[settings.mongodb_db]["templates"]

    for template in TEMPLATES:
        result = await collection.update_one(
            {"id": template["id"]}, {"$set": template}, upsert=True
        )
        action = "creada" if result.upserted_id else "actualizada"
        print(f"{template['id']}: {action}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
