"""Configuração da aplicação carregada a partir de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações tipadas e validadas (Pydantic Settings)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # MongoDB
    mongodb_uri: str = "mongodb://root:root@localhost:27017/?authSource=admin"
    mongo_db_name: str = "papodevweb"

    # Infra de mensageria / cache / objetos
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    minio_endpoint: str = "localhost:9000"
    minio_public_endpoint: str = "localhost:9000"
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_bucket: str = "papodevweb-media"
    minio_use_ssl: bool = False

    # Segurança / JWT
    jwt_secret_key: str = "troque-este-segredo-em-producao"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    jwt_reset_token_expire_minutes: int = 30
    jwt_verify_token_expire_hours: int = 24

    # E-mail / SMTP
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_from: str = "no-reply@papodevweb.local"
    smtp_from_name: str = "Papo Dev Web"

    # CORS
    frontend_origin: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância única (cacheada) das configurações."""
    return Settings()
