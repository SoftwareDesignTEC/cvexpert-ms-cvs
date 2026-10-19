LANGUAGE_NAMES = {"es": "español", "en": "English"}


def build_prompt(company: str, position: str, description: str, type: str, language: str) -> str:
    language_name = LANGUAGE_NAMES.get(language, language)
    return (
        "Eres un asistente que ayuda a redactar currículums. Expande la siguiente "
        f"descripción de experiencia laboral para que sea más detallada y profesional, "
        f"escrita en {language_name}. No inventes logros ni cifras que no estén "
        "implícitos en el texto original. Responde solo con la descripción expandida, "
        "sin comillas ni explicaciones adicionales.\n\n"
        f"Puesto: {position}\n"
        f"Empresa: {company}\n"
        f"Tipo de experiencia: {type}\n"
        f"Descripción original: {description}"
    )
