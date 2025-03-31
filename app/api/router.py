from fastapi import APIRouter
from app.api.endpoints import market_data, optimization

# Создаем основной маршрутизатор API
api_router = APIRouter()

# Подключаем маршрутизаторы конечных точек
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])
