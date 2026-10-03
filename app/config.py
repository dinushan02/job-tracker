from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./tracker.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Email (if smtp_host is empty, emails are printed to the log instead)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str = "tracker@example.com"

    # Reminder scheduler
    scheduler_enabled: bool = True
    reminder_hour: int = 8

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()