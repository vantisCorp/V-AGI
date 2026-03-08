import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main configuration settings for OMNI-AI system."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Application
    app_name: str = "OMNI-AI"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Security
    secret_key: str
    encryption_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # Database Connections
    redis_url: str = "redis://localhost:6379/0"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str

    # Vector Database
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "omni-ai-vectors"

    # AI Model Configuration
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Agent Configuration
    max_concurrent_agents: int = 10
    agent_timeout_seconds: int = 300
    task_queue_max_size: int = 1000

    # Security Configuration
    max_login_attempts: int = 5
    login_cooldown_minutes: int = 15
    two_fa_enabled: bool = True
    biometric_auth_enabled: bool = False

    # Memory Configuration
    working_memory_size: int = 1000
    long_term_memory_enabled: bool = True
    vector_store_dimension: int = 1536

    # Sandbox Configuration
    sandbox_enabled: bool = True
    docker_network: str = "omni-ai-network"
    sandbox_timeout_seconds: int = 600

    # Logging
    log_level: str = "INFO"
    log_file_path: str = "logs/omni-ai.log"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Simulation Configuration
    openfoam_enabled: bool = True
    freecad_enabled: bool = True
    max_simulation_time_seconds: int = 3600


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
