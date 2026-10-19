from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "cvexpert"

    llm_provider: str = "none"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"


settings = Settings()
