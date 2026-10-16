from app.config import settings


def test_settings_defaults():
    assert settings.mongo_db_name == "cvexpert"
    assert settings.llm_provider == "none"
