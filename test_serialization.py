from app.schemas.optimization import OptimizationCycle
from app.api.endpoints.optimization import CustomJSONEncoder
import json

# Создаем тестовый экземпляр OptimizationCycle
test_cycle = OptimizationCycle(
    cycle=1,
    date="01.01.2025",
    charge_start="01:00",
    charge_end="02:00",
    discharge_start="10:00",
    discharge_end="11:00",
    charge_price=5.0,
    discharge_price=15.0,
    profit=10.0
)

# Пробуем сериализовать в JSON
try:
    json_data = json.dumps(test_cycle, cls=CustomJSONEncoder, indent=2)
    print("Сериализация успешна:")
    print(json_data)
except Exception as e:
    print(f"Ошибка сериализации: {str(e)}")

# Проверяем сериализацию списка объектов
try:
    cycles_list = [test_cycle, test_cycle]  # Два одинаковых объекта для примера
    json_list = json.dumps({"cycles": cycles_list}, cls=CustomJSONEncoder, indent=2)
    print("\nСериализация списка успешна:")
    print(json_list)
except Exception as e:
    print(f"Ошибка сериализации списка: {str(e)}") 