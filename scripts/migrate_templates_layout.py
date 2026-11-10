"""Siembra las plantillas completas en Mongo (upsert), con layout real.

La coleccion `templates` en produccion esta vacia: sin esto, GET /templates
devuelve 0 resultados y nadie puede crear un CV (POST /cvs valida que
templateId exista). Este script crea las plantillas completas desde cero
(no asume que ya existan).

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

LAYOUT_SHOWCASE = {
    "columns": 2,
    "colorScheme": "green",
    "sections": [
        {
            "type": "header",
            "column": 1,
            "fields": [
                "personalInfo.fullName",
                "personalInfo.email",
                "personalInfo.phone",
                "personalInfo.birthDate",
                "personalInfo.bio",
            ],
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
            "itemFields": ["degree", "institution", "field", "startDate", "endDate", "current"],
        },
        {"type": "list", "column": 2, "source": "skills", "itemFields": ["name", "category", "level"]},
        {"type": "list", "column": 2, "source": "languages", "itemFields": ["name", "level"]},
        {
            "type": "list",
            "column": 2,
            "source": "certifications",
            "itemFields": ["name", "issuer", "issuedAt"],
        },
    ],
}

LAYOUT_PHOTO_2_COLUMNS = {
    "columns": 2,
    "colorScheme": "blue",
    "sections": [
        {
            "type": "header",
            "fields": [
                "personalInfo.photoUrl",
                "personalInfo.fullName",
                "personalInfo.email",
                "personalInfo.phone",
                "personalInfo.address",
                "personalInfo.bio",
            ],
        },
        {
            "type": "list",
            "column": 1,
            "source": "workExperiences",
            "itemFields": [
                "position",
                "company",
                "startDate",
                "endDate",
                "current",
                "description",
                "type",
            ],
        },
        {
            "type": "list",
            "column": 1,
            "source": "education",
            "itemFields": ["degree", "institution", "field", "startDate", "endDate", "current"],
        },
        {"type": "list", "column": 2, "source": "skills", "itemFields": ["name", "category", "level"]},
        {"type": "list", "column": 2, "source": "languages", "itemFields": ["name", "level"]},
        {
            "type": "list",
            "column": 2,
            "source": "certifications",
            "itemFields": ["name", "issuer", "issuedAt", "expiresAt"],
        },
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
    {
        "id": "showcase",
        "name": "Showcase",
        "description": "Plantilla premium de dos columnas, disponible solo en linea",
        "previewUrl": "https://placehold.co/400x560?text=Showcase",
        "category": "premium",
        "isPremium": True,
        "availableOffline": False,
        "layout": LAYOUT_SHOWCASE,
    },
    {
        "id": "photo-two-column",
        "name": "Foto",
        "description": "Plantilla de dos columnas con foto de perfil a la izquierda",
        "previewUrl": "https://placehold.co/400x560?text=Foto",
        "category": "formal",
        "isPremium": False,
        "availableOffline": True,
        "layout": LAYOUT_PHOTO_2_COLUMNS,
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
