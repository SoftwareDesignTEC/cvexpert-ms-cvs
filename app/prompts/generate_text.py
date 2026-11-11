LANGUAGE_NAMES = {"es": "español", "en": "English"}

FIELD_INSTRUCTIONS = {
    "profileBio": (
        "Redacta un resumen profesional (bio) breve para el inicio de un currículum, en "
        "primera persona o neutro según sea natural, de no más de 3 o 4 oraciones."
    ),
    "experienceDescription": (
        "Redacta la descripción de una experiencia (laboral, voluntariado, proyecto "
        "académico o informal) para un currículum, en 2 o 3 oraciones, con tono profesional."
    ),
}


def build_prompt(field: str, context: str, language: str) -> str:
    language_name = LANGUAGE_NAMES.get(language, language)
    instruction = FIELD_INSTRUCTIONS.get(field, FIELD_INSTRUCTIONS["experienceDescription"])
    return (
        "Eres un asistente que ayuda a redactar currículums. "
        f"{instruction} Escribe en {language_name}. No inventes logros ni cifras que no "
        "estén implícitos en el contexto. Responde solo con el texto final, sin comillas "
        "ni explicaciones adicionales.\n\n"
        f"Contexto disponible:\n{context}"
    )
