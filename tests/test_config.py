from app.config import settings


def test_settings_defaults():
    assert settings.mongodb_db == "cvexpert"
    assert settings.llm_provider == "none"
