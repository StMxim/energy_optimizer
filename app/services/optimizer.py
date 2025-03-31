from datetime import datetime, time
from typing import List, Dict, Any, Optional
import pandas as pd
from collections import defaultdict

from app.core.logging_config import logger
from app.schemas.market_data import MarketDataItem
from app.schemas.optimization import OptimizationCycle
from app.utils.csv_handler import format_to_csv

class OptimizerService:
    """Service for optimizing battery charge/discharge cycles"""
    
    def compute_daily_min_max_cycle(self, prices: List[Dict[str, Any]], threshold: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Finds the optimal charge/discharge cycle for a given day.
        
        Port of the computeDailyMinMaxCycle function from the original JavaScript code.
        
        Args:
            prices: List of prices for one day, each element contains hour and price
            threshold: Minimum profitability threshold in EUR
            
        Returns:
            Dictionary with the optimal cycle or None if there is no profitable cycle
        """
        if not prices:
            return None
        
        # Sort by hour
        prices_sorted = sorted(prices, key=lambda x: x["hour"])
        
        # Set initial values for minimum and maximum price
        min_entry = prices_sorted[0]
        max_entry = prices_sorted[0]
        
        # Find minimum and maximum prices during the day
        for price in prices_sorted[1:]:
            if price["price"] < min_entry["price"]:
                min_entry = price
            if price["price"] > max_entry["price"]:
                max_entry = price
        
        # Check that the minimum price (charging) is earlier than the maximum price (discharging)
        if min_entry["hour"] < max_entry["hour"]:
            # Calculate profit for 100 kWh
            profit = (max_entry["price"] - min_entry["price"]) * 100
            
            # Check if profit exceeds the threshold
            if profit > threshold:
                return {
                    "charge_start": min_entry["hour"],
                    "discharge_start": max_entry["hour"],
                    "charge_price": min_entry["price"],
                    "discharge_price": max_entry["price"],
                    "profit": profit
                }
        
        # If there is no suitable cycle, return None
        return None
    
    def process_data(self, data: List[Dict[str, Any]], threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Processes market data and finds optimal charge/discharge cycles.
        
        Args:
            data: List of dictionaries with market data
            threshold: Minimum profitability threshold in EUR
            
        Returns:
            List of optimal charge/discharge cycles
        """
        logger.info(f"Processing {len(data)} data records with threshold {threshold} EUR")
        
        # Group data by dates
        days = defaultdict(list)
        for item in data:
            # Use the dictionary key "date" instead of object attribute
            date_str = item["date"]
            if isinstance(date_str, datetime):
                # If datetime, convert to ISO string
                date_str = date_str.strftime("%Y-%m-%d")
                
            days[date_str].append({
                "hour": item["hour"],
                "price": item["price_eur"]
            })
        
        # Find the optimal cycle for each day
        result = []
        cycle_count = 1
        
        for date_str, prices in days.items():
            # Sort prices by hour
            prices.sort(key=lambda x: x["hour"])
            
            # Find the optimal cycle for the day
            cycle = self.compute_daily_min_max_cycle(prices, threshold)
            
            if cycle:
                # Format the date
                formatted_date = date_str
                # Convert date to the correct DD.MM.YYYY format if needed
                if "-" in date_str and len(date_str) == 10:  # YYYY-MM-DD
                    try:
                        dt = datetime.fromisoformat(date_str)
                        formatted_date = dt.strftime("%d.%m.%Y")
                    except ValueError:
                        logger.warning(f"Could not convert date: {date_str}")
                
                # Рассчитываем прибыль с учетом потерь (эффективность 85%)
                efficiency = 0.85
                profit_after_losses = cycle["profit"] * efficiency
                
                result.append({
                    "cycle": cycle_count,
                    "date": formatted_date,
                    "charge_start": f"{cycle['charge_start']}:00",
                    "charge_end": f"{cycle['charge_start'] + 1}:00",
                    "discharge_start": f"{cycle['discharge_start']}:00",
                    "discharge_end": f"{cycle['discharge_start'] + 1}:00",
                    "charge_price": cycle["charge_price"],
                    "discharge_price": cycle["discharge_price"],
                    "profit": cycle["profit"],
                    "profit_after_losses": profit_after_losses
                })
                
                cycle_count += 1
        
        logger.info(f"Found {len(result)} optimal cycles")
        return result
    
    def to_csv(self, cycles: List[Dict[str, Any]]) -> str:
        """Converts optimization results to CSV format"""
        return format_to_csv(cycles)
    
    def to_optimization_response(self, cycles: List[Dict[str, Any]]) -> List[OptimizationCycle]:
        """Converts optimization results to Pydantic model format"""
        result = []
        
        for cycle_data in cycles:
            # Copy data for modification
            cycle_dict = dict(cycle_data)
            
            # Check date format and format to DD.MM.YYYY
            date_value = cycle_dict.get("date")
            if isinstance(date_value, datetime):
                # If it's a datetime object, convert it to a string in DD.MM.YYYY format
                cycle_dict["date"] = date_value.strftime("%d.%m.%Y")
            elif isinstance(date_value, str):
                # If it's a string, check its format
                if "-" in date_value and len(date_value) == 10:  # YYYY-MM-DD format
                    try:
                        # Convert YYYY-MM-DD to DD.MM.YYYY
                        dt = datetime.fromisoformat(date_value)
                        cycle_dict["date"] = dt.strftime("%d.%m.%Y")
                    except Exception as e:
                        logger.warning(f"Error converting date {date_value}: {str(e)}")
            
            # Create a Pydantic model instance
            try:
                result.append(OptimizationCycle(**cycle_dict))
            except Exception as e:
                logger.error(f"Error creating OptimizationCycle: {str(e)}, data: {cycle_dict}")
                # Skip this cycle on error
                continue
                
        return result
