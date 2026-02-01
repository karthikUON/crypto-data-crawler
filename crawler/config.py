"""Configuration management for the crypto crawler using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/crypto_db"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Crawler Configuration
    crypto_api_url: str = "https://api.coingecko.com/api/v3"
    crawler_interval: int = 300  # seconds
    top_n_cryptos: int = 50

    # Retry Configuration
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    retry_max_delay: int = 60

    # Logging
    log_level: str = "INFO"


# Global settings instance
settings = Settings()
