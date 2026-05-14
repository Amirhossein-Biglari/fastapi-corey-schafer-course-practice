from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    secret_key: SecretStr
    algorithm: str = "HS256"  # standard for json web tokens
    access_token_expire_minutes: int = 30


settings = Settings()  # Loaded from .env file when the module is imported