"""
파일명: settings.py
목적: 환경 변수 및 애플리케이션 설정 관리
작성일: 2025-01-26
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정

    .env 파일에서 자동으로 환경 변수를 로드합니다.
    """

    # AI API
    ANTHROPIC_API_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = "credentials.json"
    GOOGLE_SPREADSHEET_ID: Optional[str] = None

    # SendGrid
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@heartbridge.com"

    # App Configuration
    APP_ENV: str = "development"
    MAX_IMAGE_SIZE_MB: int = 5
    LOG_LEVEL: str = "INFO"

    # Constants
    ALLOWED_IMAGE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
    MAX_SURVEY_QUESTIONS: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 싱글톤 인스턴스
settings = Settings()


# 테스트용 함수
def get_settings() -> Settings:
    """
    설정 객체를 반환합니다.

    Returns:
        Settings: 애플리케이션 설정 객체
    """
    return settings
