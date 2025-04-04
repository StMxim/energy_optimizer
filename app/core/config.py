from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Energy Market Optimizer"
    
    # Аутентификация для внешнего API
    CLIENT_ID: str = os.getenv("CLIENT_ID", "cm_app_ntp_id_1b3e94274c3d41f88944e01633640701")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", "ntp_9CCzWONT5FWN3lvpNDu4")
    
    # URL для получения токена
    TOKEN_URL: str = os.getenv("TOKEN_URL", "https://identity.netztransparenz.de/users/connect/token")
    
    # URL внешнего API Netztransparenz для спотовых цен
    MARKET_API_URL: str = os.getenv("MARKET_API_URL", "https://ds.netztransparenz.de/api/v1/data/Spotmarktpreise")
    
    # User-Agent для запросов к API
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Формат даты/времени для URL API (YYYY-MM-DDTHH:MM:SS)
    API_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    
    # Уровень логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Время жизни токена (в секундах) - используется для кеширования
    TOKEN_LIFETIME: int = 3500  # Обычно токены живут около часа, берем чуть меньше для запаса
    
    # Флаг, указывающий использовать ли тестовые данные по умолчанию 
    # из-за отсутствия настоящего API
    USE_TEST_DATA_BY_DEFAULT: bool = False
    
    # CORS настройки
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
