from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    db_url: str = "postgresql+asyncpg://127.0.0.1:5432/ipam"
    jwt_secret: str = "dev-not-secret"
    model_config = SettingsConfigDict(env_prefix="IPAM_", env_file=".env", extra="ignore")


settings = Settings()
