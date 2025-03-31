# Energy Market Optimizer

API сервис для оптимизации циклов зарядки/разрядки аккумуляторов на основе данных рынка электроэнергии.

## Функциональность

- Получение данных рынка электроэнергии через API или CSV файл
- Оптимизация циклов зарядки/разрядки для максимизации прибыли
- Возможность задать минимальный порог прибыли
- Экспорт результатов в JSON или CSV формат

## Требования

- Python 3.8+
- FastAPI
- Docker & Docker Compose (опционально)

## Установка и запуск

### Локальный запуск

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
4. Скопируйте файл .env.example в .env и настройте переменные окружения
5. Запустите сервис:
   ```
   uvicorn app.main:app --reload
   ```

### Запуск через Docker

1. Убедитесь, что Docker и Docker Compose установлены
2. Создайте .env файл на основе .env.example
3. Запустите:
   ```
   docker-compose up -d
   ```

## API документация

После запуска сервиса, документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Примеры использования

### Получение данных рынка

```python
import requests
import json

url = "http://localhost:8000/api/v1/market-data/"
payload = {
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-01-02T00:00:00"
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
```

### Оптимизация циклов

```python
import requests
import json

url = "http://localhost:8000/api/v1/optimization/"
payload = {
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-01-07T00:00:00",
    "threshold": 0.5
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
cycles = response.json()
```

## Тесты

Для запуска тестов выполните:

```
pytest
```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.
