# backend/app/config.py
# Настройки читаются из переменных окружения (см. .env в корне проекта)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "products_db"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "products"

    ollama_host: str = "ollama"
    ollama_port: int = 11434
    embedding_model: str = "nomic-embed-text:v1.5"
    llm_model: str = "llama3.2:3b"
    embedding_dim: int = 768

    @property
    def postgres_dsn(self) -> str:
        return (
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password} host={self.postgres_host} port={self.postgres_port}"
        )

    @property
    def ollama_url(self) -> str:
        return f"http://{self.ollama_host}:{self.ollama_port}"


# один общий объект настроек на всё приложение
settings = Settings()
