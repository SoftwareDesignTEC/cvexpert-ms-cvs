LANGUAGE_NAMES = {"es": "español", "en": "English"}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "bio": {"type": "string"},
        "workExperiences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "position": {"type": "string"},
                    "startDate": {"type": "string"},
                    "endDate": {"type": "string"},
                    "current": {"type": "boolean"},
                    "description": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["formal", "freelance", "volunteer", "school-project", "informal"],
                    },
                },
                "required": ["position", "startDate", "current", "description", "type"],
            },
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": "string"},
                    "startDate": {"type": "string"},
                    "endDate": {"type": "string"},
                    "current": {"type": "boolean"},
                },
                "required": ["institution", "degree", "field", "startDate", "current"],
            },
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced", "expert"],
                    },
                    "category": {"type": "string"},
                },
                "required": ["name", "level"],
            },
        },
        "languages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "level": {
                        "type": "string",
                        "enum": ["basic", "intermediate", "advanced", "native"],
                    },
                },
                "required": ["name", "level"],
            },
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "issuer": {"type": "string"},
                    "issuedAt": {"type": "string"},
                },
                "required": ["name", "issuer"],
            },
        },
        "invalid": {
            "type": "boolean",
            "description": "true si el relato no tiene sentido o no describe una trayectoria real.",
        },
    },
    "required": ["workExperiences", "education", "skills", "languages", "certifications"],
}


def build_prompt(free_text: str, language: str) -> str:
    language_name = LANGUAGE_NAMES.get(language, language)
    return (
        "Eres un asistente que construye currículums profesionales a partir de un relato "
        "en texto libre de una persona sobre su trayectoria. Extrae su experiencia laboral, "
        "educación, habilidades, idiomas y certificaciones, y redacta un resumen profesional "
        f"(bio) breve, todo en {language_name}. No inventes datos que no estén implícitos en "
        "el relato. Si una fecha no se menciona, omítela en vez de inventarla. Las fechas van "
        "como texto en formato AAAA-MM-DD o AAAA-MM si no se menciona el día. El campo 'type' "
        "de cada experiencia laboral debe ser 'formal' si fue un empleo con una empresa, "
        "'freelance' si fue trabajo independiente, 'volunteer' si fue voluntariado, "
        "'school-project' si fue un proyecto académico, o 'informal' en cualquier otro caso. "
        "Si el relato no tiene sentido, está vacío de contenido real, es ilegible o no "
        "describe en absoluto la trayectoria de una persona, responde con invalid=true y "
        "las listas vacías. Responde únicamente con el JSON que cumpla el esquema indicado.\n\n"
        f"Relato de la persona:\n{free_text}"
    )
