from app.llm.base import NONSENSE_SENTINEL
from app.prompts import expand_experience, generate_cv, generate_text, translate_experience


def test_expand_experience_prompt_includes_fields():
    prompt = expand_experience.build_prompt(
        company="Acme",
        position="Backend Developer",
        description="Trabajé en APIs",
        type="formal",
        language="es",
    )
    assert "Acme" in prompt
    assert "Backend Developer" in prompt
    assert "Trabajé en APIs" in prompt
    assert "español" in prompt


def test_expand_experience_prompt_language_en():
    prompt = expand_experience.build_prompt(
        company="Acme", position="Dev", description="desc", type="formal", language="en"
    )
    assert "English" in prompt


def test_translate_experience_prompt_includes_organization_when_present():
    prompt = translate_experience.build_prompt(
        type="volunteer",
        position="Voluntario",
        description="Ayudé en un refugio",
        language="en",
        organization="Cruz Roja",
    )
    assert "Cruz Roja" in prompt
    assert "English" in prompt


def test_translate_experience_prompt_omits_organization_when_absent():
    prompt = translate_experience.build_prompt(
        type="school-project",
        position="Lider de proyecto",
        description="Proyecto final",
        language="es",
    )
    assert "Organización" not in prompt


def test_expand_experience_prompt_instructs_nonsense_sentinel():
    prompt = expand_experience.build_prompt(
        company="Acme", position="Dev", description="desc", type="formal", language="es"
    )
    assert NONSENSE_SENTINEL in prompt


def test_translate_experience_prompt_instructs_invalid_flag():
    prompt = translate_experience.build_prompt(
        type="volunteer", position="Voluntario", description="desc", language="es"
    )
    assert "invalid" in prompt


def test_generate_text_prompt_instructs_nonsense_sentinel():
    prompt = generate_text.build_prompt("profileBio", "contexto", "es")
    assert NONSENSE_SENTINEL in prompt


def test_generate_cv_prompt_instructs_invalid_flag():
    prompt = generate_cv.build_prompt("relato", "es")
    assert "invalid" in prompt
    assert "invalid" in generate_cv.RESPONSE_SCHEMA["properties"]
