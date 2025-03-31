import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime
import json

from app.main import app
from app.schemas.market_data import MarketDataItem

client = TestClient(app)

# Тестовые данные
TEST_MARKET_DATA = [
    MarketDataItem(date=datetime(2023, 1, 1), hour=0, price_ct_kwh=20.0, price_eur=0.2),
    MarketDataItem(date=datetime(2023, 1, 1), hour=1, price_ct_kwh=18.5, price_eur=0.185),
]

@patch("app.services.market_data.MarketDataService.get_market_data")
def test_get_market_data(mock_get_market_data):
    """Тест API эндпоинта получения данных рынка"""
    # Настраиваем мок
    mock_get_market_data.return_value = TEST_MARKET_DATA
    
    # Формируем запрос
    request_data = {
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-01-02T00:00:00"
    }
    
    # Отправляем запрос
    response = client.post("/api/v1/market-data/", json=request_data)
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2

@patch("app.services.market_data.MarketDataService.parse_csv_data")
def test_upload_csv(mock_parse_csv_data):
    """Тест API эндпоинта загрузки CSV файла"""
    # Настраиваем мок
    mock_parse_csv_data.return_value = TEST_MARKET_DATA
    
    # Подготавливаем тестовый CSV файл
    csv_content = b"Datum;von;Zeitzone von;bis;Zeitzone bis;Spotmarktpreis in ct/kWh\n01.01.2023;0;CET;1;CET;20,0"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    
    # Отправляем запрос
    response = client.post("/api/v1/market-data/upload-csv", files=files)
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2

@patch("app.services.market_data.MarketDataService.get_market_data")
@patch("app.services.optimizer.OptimizerService.optimize_cycles")
def test_optimize_cycles(mock_optimize_cycles, mock_get_market_data):
    """Тест API эндпоинта оптимизации циклов"""
    # Настраиваем моки
    mock_get_market_data.return_value = TEST_MARKET_DATA
    
    # Создаем тестовый результат оптимизации
    from app.schemas.optimization import OptimizationCycle
    test_cycles = [
        OptimizationCycle(
            cycle=1,
            date=datetime(2023, 1, 1),
            charge_start="01:00",
            charge_end="02:00",
            discharge_start="06:00",
            discharge_end="07:00",
            charge_price=0.185,
            discharge_price=0.25,
            profit=5.85
        )
    ]
    mock_optimize_cycles.return_value = test_cycles
    
    # Формируем запрос
    request_data = {
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-01-02T00:00:00",
        "threshold": 0.0
    }
    
    # Отправляем запрос
    response = client.post("/api/v1/optimization/", json=request_data)
    
    # Проверяем ответ
    assert response.status_code == 200
    data = response.json()
    assert "cycles" in data
    assert len(data["cycles"]) == 1
    assert data["cycles"][0]["cycle"] == 1
    assert data["cycles"][0]["profit"] == 5.85

@patch("app.services.market_data.MarketDataService.get_market_data")
@patch("app.services.optimizer.OptimizerService.optimize_cycles")
def test_optimize_cycles_csv(mock_optimize_cycles, mock_get_market_data):
    """Тест API эндпоинта оптимизации циклов с выводом в CSV"""
    # Настраиваем моки
    mock_get_market_data.return_value = TEST_MARKET_DATA
    
    # Создаем тестовый результат оптимизации
    from app.schemas.optimization import OptimizationCycle
    test_cycles = [
        OptimizationCycle(
            cycle=1,
            date=datetime(2023, 1, 1),
            charge_start="01:00",
            charge_end="02:00",
            discharge_start="06:00",
            discharge_end="07:00",
            charge_price=0.185,
            discharge_price=0.25,
            profit=5.85
        )
    ]
    mock_optimize_cycles.return_value = test_cycles
    
    # Формируем запрос
    request_data = {
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-01-02T00:00:00",
        "threshold": 0.0
    }
    
    # Отправляем запрос
    response = client.post("/api/v1/optimization/csv", json=request_data)
    
    # Проверяем ответ
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv"
    assert "Content-Disposition" in response.headers
    assert "attachment; filename=optimization_results.csv" in response.headers["Content-Disposition"]
    
    # Проверяем содержимое CSV
    content = response.content.decode('utf-8')
    assert "Cycle;Date;Charge_Start" in content
    assert "1;01.01.2023;01:00" in content
