LANGUAGE_NAMES = {"es": "español", "en": "English"}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "position": {"type": "string"},
        "description": {"type": "string"},
        "invalid": {
            "type": "boolean",
            "description": "true si el puesto/descripción original no tienen sentido.",
        },
    },
    "required": ["position", "description"],
}


def build_prompt(
    type: str,
    position: str,
    description: str,
    language: str,
    organization: str | None = None,
) -> str:
    language_name = LANGUAGE_NAMES.get(language, language)
    organization_line = f"Organización: {organization}\n" if organization else ""
    return (
        "Eres un asistente que ayuda a adaptar experiencia no laboral (voluntariado, "
        "proyectos escolares o experiencia informal) para un currículum profesional. "
        f"Traduce y adapta el puesto y la descripción a {language_name}, manteniendo el "
        "significado original y un tono profesional. Si el puesto o la descripción no "
        "tienen sentido, están vacíos de contenido real o no describen ninguna experiencia "
        "real, responde con invalid=true y deja position/description vacíos.\n\n"
        f"Tipo: {type}\n"
        f"{organization_line}"
        f"Puesto original: {position}\n"
        f"Descripción original: {description}"
    )
