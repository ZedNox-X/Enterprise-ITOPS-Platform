from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://itops:itops@localhost:5432/itops"
    rabbitmq_url: str = "amqp://itops:itops@localhost:5672/"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
