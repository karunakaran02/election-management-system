from pydantic_settings import BaseSettings, SettingsConfigDict


class Core(BaseSettings):

    jwt_secret_key: str = "supersecretjwtkeyforvoterpollingapp"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    database_url: str = (
        "postgresql+asyncpg://voterdatabase:password@localhost:5432/voterdatabase"
    )
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


core = Core()
