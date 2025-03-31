from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

class MarketDataRequest(BaseModel):
    start_date: datetime = Field(..., description="Начальная дата (формат: YYYY-MM-DD)")
    end_date: datetime = Field(..., description="Конечная дата (формат: YYYY-MM-DD)")

class MarketDataItem(BaseModel):
    date: datetime = Field(..., description="Дата")
    hour: int = Field(..., description="Час (0-23)")
    price_ct_kwh: float = Field(..., description="Цена в центах за кВтч")
    price_eur: float = Field(..., description="Цена в евро за кВтч")
    
    @validator('price_eur', pre=True, always=True)
    def set_price_eur(cls, v, values):
        if v is None and 'price_ct_kwh' in values:
            return values['price_ct_kwh'] / 100.0
        return v

class Config:
    json_schema_extra = {
        "example": {
            "date": "2023-01-01T00:00:00",
            "hour": 12,
            "price_ct_kwh": 25.5,
            "price_eur": 0.255
        }
    }

class MarketDataResponse(BaseModel):
    data: List[MarketDataItem]
