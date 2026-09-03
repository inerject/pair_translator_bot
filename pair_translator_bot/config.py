from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    allowed_user_ids: set[int]

    google_cloud_project: str

    log_message_text: bool = False

    log_max_bytes: int = 5 * 1024 * 1024
    log_backup_count: int = 10

    message_log_max_bytes: int = 10 * 1024 * 1024
    message_log_backup_count: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
