"""Migracion manual: carga un layout real en dos plantillas ya existentes en Mongo.

Pensado para correr una sola vez contra la base real (no local), para que Andres
pueda probar el PDF de punta a punta con una plantilla de 1 columna y otra de 2.

Antes de correrlo:
1. Reemplazar TEMPLATE_ID_1_COLUMN / TEMPLATE_ID_2_COLUMNS por los id reales de
   dos plantillas que ya existan en la coleccion `templates` (los ves con
   GET /templates o en Cosmos DB directamente).
2. Que MONGODB_URI (en el entorno donde se corre) apunte a la base real, no a
   localhost. Ojo: esto escribe directo sobre datos de produccion.

Uso: python scripts/migrate_templates_layout.py
"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

TEMPLATE_ID_1_COLUMN = "CAMBIAR-POR-ID-REAL-PLANTILLA-1-COLUMNA"
TEMPLATE_ID_2_COLUMNS = "CAMBIAR-POR-ID-REAL-PLANTILLA-2-COLUMNAS"

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


async def main() -> None:
    client = AsyncIOMotorClient(settings.mongodb_uri)
    collection = client[settings.mongodb_db]["templates"]

    result_1 = await collection.update_one(
        {"id": TEMPLATE_ID_1_COLUMN}, {"$set": {"layout": LAYOUT_1_COLUMN}}
    )
    result_2 = await collection.update_one(
        {"id": TEMPLATE_ID_2_COLUMNS}, {"$set": {"layout": LAYOUT_2_COLUMNS}}
    )

    print(f"1 columna ({TEMPLATE_ID_1_COLUMN}): matched={result_1.matched_count} modified={result_1.modified_count}")
    print(f"2 columnas ({TEMPLATE_ID_2_COLUMNS}): matched={result_2.matched_count} modified={result_2.modified_count}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
