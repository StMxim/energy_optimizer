import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
import httpx

from app.services.market_data import MarketDataService
from app.schemas.market_data import MarketDataItem

# Тестовые CSV данные
TEST_CSV_CONTENT = """Datum;von;Zeitzone von;bis;Zeitzone bis;Spotmarktpreis in ct/kWh
01.01.2023;0;CET;1;CET;20,0
01.01.2023;1;CET;2;CET;18,5
01.01.2023;2;CET;3;CET;15,0
01.01.2023;3;CET;4;CET;12,5"""

# Тестовые API данные
TEST_API_DATA = [
    {
        "Datum": "01.01.2023",
        "von": 0,
        "Zeitzone von": "CET",
        "bis": 1,
        "Zeitzone bis": "CET",
        "Spotmarktpreis in ct/kWh": "20,0"
    },
    {
        "Datum": "01.01.2023",
        "von": 1,
        "Zeitzone von": "CET",
        "bis": 2,
        "Zeitzone bis": "CET",
        "Spotmarktpreis in ct/kWh": "18,5"
    }
]

@pytest.fixture
def market_data_service():
    """Фикстура для создания сервиса данных рынка"""
    return MarketDataService()

def test_parse_csv_data(market_data_service):
    """Тест парсинга CSV данных"""
    # Вызываем метод парсинга CSV
    result = market_data_service.parse_csv_data(TEST_CSV_CONTENT)
    
    # Проверяем результат
    assert len(result) == 4
    
    # Проверяем первый элемент
    first_item = result[0]
    assert isinstance(first_item, MarketDataItem)
    assert first_item.date.date() == datetime(2023, 1, 1).date()
    assert first_item.hour == 0
    assert first_item.price_ct_kwh == 20.0
    assert first_item.price_eur == 0.2
    
    # Проверяем последний элемент
    last_item = result[3]
    assert last_item.hour == 3
    assert last_item.price_ct_kwh == 12.5
    assert last_item.price_eur == 0.125

@patch("httpx.AsyncClient.get")
@pytest.mark.asyncio
async def test_get_market_data(mock_get, market_data_service):
    """Тест получения данных рынка через API"""
    # Создаем мок-ответ
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = TEST_API_DATA
    mock_get.return_value = mock_response
    
    # Вызываем метод получения данных
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 2)
    result = await market_data_service.get_market_data(start_date, end_date)
    
    # Проверяем, что API был вызван с правильными параметрами
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "von=2023-01-01" in str(kwargs)
    assert "bis=2023-01-02" in str(kwargs)
    
    # Проверяем результат
    assert len(result) == 2
    
    # Проверяем первый элемент
    first_item = result[0]
    assert isinstance(first_item, MarketDataItem)
    assert first_item.date.date() == datetime(2023, 1, 1).date()
    assert first_item.hour == 0
    assert first_item.price_ct_kwh == 20.0
    assert first_item.price_eur == 0.2

@patch("httpx.AsyncClient.get")
@pytest.mark.asyncio
async def test_get_market_data_error(mock_get, market_data_service):
    """Тест обработки ошибки при получении данных через API"""
    # Создаем мок-ответ с ошибкой
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response
    
    # Вызываем метод и ожидаем исключение
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 2)
    
    with pytest.raises(Exception) as excinfo:
        await market_data_service.get_market_data(start_date, end_date)
    
    # Проверяем текст исключения
    assert "Ошибка получения данных рынка" in str(excinfo.value)
