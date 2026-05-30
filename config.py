from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    secret_key: SecretStr
    algorithm: str = "HS256"  # standard for json web tokens
    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5 * 1024 * 1024

    posts_per_page: int = 10

    reset_token_expire_minutes: int = 60

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:8000"


# Loaded from .env file when the module is imported
settings = Settings()  # type: ignore[call-arg]
