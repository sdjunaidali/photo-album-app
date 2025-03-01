from pydantic_settings import BaseSettings  # Updated import
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Database Configuration
    database_url: PostgresDsn  # Strict validation for PostgreSQL URLs

    # Application Configuration
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    # MinIO Configuration
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str

    # Security Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 300

    # Debug Configuration
    debug: bool = False

    class Config:
        env_file = ".env"  # Path to your .env file
        env_file_encoding = "utf-8"
