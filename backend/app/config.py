"""Application configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "Cyber HealthGuard AI"
    app_version: str = "1.0.0"
    debug: bool = True

    # MongoDB
    mongo_url: str = "mongodb://mongodb:27017"
    mongodb_db_name: str = "cyber_healthguard"

    # Authentication
    secret_key: str = "your-secret-key-change-in-production-please-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days

    # Anomaly Detection
    anomaly_threshold: float = 0.7
    min_samples_for_training: int = 100

    # Alert Rules
    failed_login_threshold: int = 5
    suspicious_processes: list = [
        "mimikatz", "powershell -enc", "powershell -e",
        "cmd.exe /c", "wmic", "psexec", "net user",
        "net localgroup", "procdump", "pwdump"
    ]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
