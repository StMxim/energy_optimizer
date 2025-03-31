from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import List, Optional

class OptimizationRequest(BaseModel):
    start_date: datetime = Field(..., description="Start date (format: YYYY-MM-DD)")
    end_date: datetime = Field(..., description="End date (format: YYYY-MM-DD)")
    threshold: float = Field(0.0, description="Minimum profit threshold in EUR")

class OptimizationCycle(BaseModel):
    cycle: int = Field(..., description="Cycle number")
    date: str = Field(..., description="Date (format: DD.MM.YYYY or YYYY-MM-DD)")
    charge_start: str = Field(..., description="Charge start time (format: HH:00)")
    charge_end: str = Field(..., description="Charge end time (format: HH:00)")
    discharge_start: str = Field(..., description="Discharge start time (format: HH:00)")
    discharge_end: str = Field(..., description="Discharge end time (format: HH:00)")
    charge_price: float = Field(..., description="Charge price (EUR/kWh)")
    discharge_price: float = Field(..., description="Discharge price (EUR/kWh)")
    profit: float = Field(..., description="Profit for 100 kWh (EUR)")
    profit_after_losses: Optional[float] = Field(None, description="Profit after efficiency losses (EUR)")

class OptimizationResponse(BaseModel):
    cycles: List[OptimizationCycle]
