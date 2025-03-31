import pytest
from datetime import datetime

from app.services.optimizer import OptimizerService

def test_optimize_cycles_basic(optimizer_service, sample_market_data):
    """Тест базового функционала оптимизации циклов"""
    # Запускаем оптимизацию
    cycles = optimizer_service.optimize_cycles(sample_market_data)
    
    # Проверяем, что найден хотя бы один цикл
    assert len(cycles) > 0
    
    # Проверяем первый цикл
    cycle = cycles[0]
    
    # Проверяем, что цикл имеет правильные поля
    assert cycle.cycle == 1
    assert isinstance(cycle.date, datetime)
    assert cycle.charge_start == "03:00"  # Час с минимальной ценой
    assert cycle.charge_end == "04:00"
    assert cycle.discharge_start == "08:00"  # Час с максимальной ценой
    assert cycle.discharge_end == "09:00"
    
    # Проверяем цены
    assert cycle.charge_price == 0.125  # Минимальная цена
    assert cycle.discharge_price == 0.28  # Максимальная цена
    
    # Проверяем прибыль
    expected_profit = (0.28 - 0.125) * 100 * 0.9  # (макс_цена - мин_цена) * 100 кВтч * КПД 90%
    assert cycle.profit == pytest.approx(expected_profit)

def test_optimize_cycles_with_threshold(optimizer_service, sample_market_data):
    """Тест оптимизации циклов с порогом прибыли"""
    # Установим порог выше ожидаемой прибыли
    high_threshold = 20.0
    cycles = optimizer_service.optimize_cycles(sample_market_data, threshold=high_threshold)
    
    # При высоком пороге не должно быть найдено циклов
    assert len(cycles) == 0
    
    # Установим порог ниже ожидаемой прибыли
    low_threshold = 10.0
    cycles = optimizer_service.optimize_cycles(sample_market_data, threshold=low_threshold)
    
    # При низком пороге должны быть найдены циклы
    assert len(cycles) > 0

def test_find_alternate_cycle(optimizer_service, sample_market_data):
    """Тест поиска альтернативного цикла"""
    # Создадим тестовые данные, где максимальная цена идет до минимальной
    test_data = [
        # Цена падает в течение дня
        sample_market_data[8],  # Максимальная цена (hour=8)
        sample_market_data[7],  # ...
        sample_market_data[6],
        sample_market_data[5],
        sample_market_data[4],
        sample_market_data[3],  # Минимальная цена (hour=3)
    ]
    
    # Вызываем метод поиска альтернативного цикла
    result = optimizer_service._find_alternate_cycle(test_data)
    
    # Должен быть возвращен None, так как все высокие цены идут до низких
    assert result is None
    
    # Тест с данными, где есть возможный альтернативный цикл
    test_data_2 = [
        sample_market_data[5],  # hour=5, price=0.17
        sample_market_data[3],  # hour=3, price=0.125 (минимальная)
        sample_market_data[8],  # hour=8, price=0.28 (максимальная)
        sample_market_data[7],  # hour=7, price=0.25
    ]
    
    # Вызываем метод
    result = optimizer_service._find_alternate_cycle(test_data_2)
    
    # Должна быть возвращена пара (min_price_item, max_price_item)
    assert result is not None
    assert len(result) == 2
    
    min_item, max_item = result
    # Проверяем, что найдена правильная пара
    assert min_item.price_eur == 0.125
    assert max_item.price_eur == 0.28
    assert min_item.hour < max_item.hour
