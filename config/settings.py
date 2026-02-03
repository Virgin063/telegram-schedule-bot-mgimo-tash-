"""
Настройки приложения
"""
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from typing import List
import os


class Settings(BaseSettings):
    """Основные настройки приложения"""
    
    # ===== TELEGRAM =====
    student_bot_token: str = Field(..., env="STUDENT_BOT_TOKEN")
    admin_bot_token: str = Field(..., env="ADMIN_BOT_TOKEN")
    # Используем alias чтобы читать ADMIN_IDS из env
    admin_ids_raw: str = Field(default="", validation_alias="ADMIN_IDS")
    
    @computed_field
    @property
    def admin_ids(self) -> List[int]:
        """Парсит ADMIN_IDS как строку с числами через запятую"""
        if not self.admin_ids_raw:
            return []
        return [int(x.strip()) for x in self.admin_ids_raw.split(",") if x.strip()]
    
    # ===== DATABASE =====
    database_url: str = Field(..., env="DATABASE_URL")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="schedule_bot", env="DB_NAME")
    db_user: str = Field(default="schedule_user", env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    
    # ===== REDIS =====
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    
    @property
    def redis_url(self) -> str:
        """Формирует URL для подключения к Redis"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ===== OPENAI =====
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    
    # ===== GOOGLE DRIVE =====
    google_drive_mode: str = Field(default="simple", env="GOOGLE_DRIVE_MODE")  # simple или api
    google_drive_public_url: str = Field(default="", env="GOOGLE_DRIVE_PUBLIC_URL")
    google_drive_folder_id: str = Field(default="", env="GOOGLE_DRIVE_FOLDER_ID")
    google_credentials_file: str = Field(default="credentials.json", env="GOOGLE_CREDENTIALS_FILE")
    
    # ===== SYNC SETTINGS =====
    sync_interval_minutes: int = Field(default=15, env="SYNC_INTERVAL_MINUTES")
    sync_mode: str = Field(default="auto", env="SYNC_MODE")  # auto или manual
    
    # ===== NOTIFICATIONS =====
    morning_notification_time: str = Field(default="07:00", env="MORNING_NOTIFICATION_TIME")
    before_class_notification_minutes: int = Field(default=15, env="BEFORE_CLASS_NOTIFICATION_MINUTES")
    
    # ===== LOGGING =====
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/bot.log", env="LOG_FILE")
    
    # ===== TIMEZONE =====
    timezone: str = Field(default="Asia/Tashkent", env="TIMEZONE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Игнорировать лишние поля из .env


# Создаем глобальный экземпляр настроек
settings = Settings()
