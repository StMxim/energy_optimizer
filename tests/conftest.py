import pytest
from fastapi.testclient import TestClient
from datetime import datetime, time

from app.main import app
from app.schemas.market_data import MarketDataItem
from app.services.optimizer import OptimizerService

@pytest.fixture
def client():
    """Фикстура для создания тестового клиента FastAPI"""
    return TestClient(app)

@pytest.fixture
def optimizer_service():
    """Фикстура для создания сервиса оптимизации"""
    return OptimizerService()

@pytest.fixture
def sample_market_data():
    """Фикстура с примером данных рынка для тестирования"""
    # Создаем тестовые данные на один день
    date = datetime(2023, 1, 1)
    return [
        MarketDataItem(date=date, hour=0, price_ct_kwh=20.0, price_eur=0.20),
        MarketDataItem(date=date, hour=1, price_ct_kwh=18.5, price_eur=0.185),
        MarketDataItem(date=date, hour=2, price_ct_kwh=15.0, price_eur=0.15),
        MarketDataItem(date=date, hour=3, price_ct_kwh=12.5, price_eur=0.125),  # Минимальная цена
        MarketDataItem(date=date, hour=4, price_ct_kwh=14.0, price_eur=0.14),
        MarketDataItem(date=date, hour=5, price_ct_kwh=17.0, price_eur=0.17),
        MarketDataItem(date=date, hour=6, price_ct_kwh=22.0, price_eur=0.22),
        MarketDataItem(date=date, hour=7, price_ct_kwh=25.0, price_eur=0.25),
        MarketDataItem(date=date, hour=8, price_ct_kwh=28.0, price_eur=0.28),  # Максимальная цена
        MarketDataItem(date=date, hour=9, price_ct_kwh=26.5, price_eur=0.265),
        MarketDataItem(date=date, hour=10, price_ct_kwh=24.0, price_eur=0.24),
        MarketDataItem(date=date, hour=11, price_ct_kwh=22.5, price_eur=0.225),
        MarketDataItem(date=date, hour=12, price_ct_kwh=21.0, price_eur=0.21),
        MarketDataItem(date=date, hour=13, price_ct_kwh=20.0, price_eur=0.20),
        MarketDataItem(date=date, hour=14, price_ct_kwh=19.5, price_eur=0.195),
        MarketDataItem(date=date, hour=15, price_ct_kwh=18.0, price_eur=0.18),
        MarketDataItem(date=date, hour=16, price_ct_kwh=17.5, price_eur=0.175),
        MarketDataItem(date=date, hour=17, price_ct_kwh=19.0, price_eur=0.19),
        MarketDataItem(date=date, hour=18, price_ct_kwh=22.0, price_eur=0.22),
        MarketDataItem(date=date, hour=19, price_ct_kwh=24.0, price_eur=0.24),
        MarketDataItem(date=date, hour=20, price_ct_kwh=23.0, price_eur=0.23),
        MarketDataItem(date=date, hour=21, price_ct_kwh=21.0, price_eur=0.21),
        MarketDataItem(date=date, hour=22, price_ct_kwh=19.0, price_eur=0.19),
        MarketDataItem(date=date, hour=23, price_ct_kwh=17.0, price_eur=0.17),
    ]
