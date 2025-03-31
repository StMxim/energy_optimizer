from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form, Depends, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io
import traceback
import json

from app.schemas.optimization import OptimizationResponse, OptimizationCycle
from app.services.market_data import MarketDataService
from app.services.optimizer import OptimizerService
from app.core.logging_config import logger

router = APIRouter()

# Create service instances
market_service = MarketDataService()
optimizer_service = OptimizerService()

# Custom JSON encoder for handling datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, OptimizationCycle):
            # Convert OptimizationCycle to a dictionary for serialization
            # Извлекаем часы из строк charge_start и discharge_start (формат "HH:00")
            charge_hour = int(obj.charge_start.split(':')[0]) if obj.charge_start else None
            discharge_hour = int(obj.discharge_start.split(':')[0]) if obj.discharge_start else None
            
            # Рассчитываем прибыль с учетом потерь при зарядке/разрядке (эффективность 85%)
            efficiency = 0.85
            profit_after_losses = obj.profit * efficiency if obj.profit else 0.0
            
            return {
                "cycle": obj.cycle,
                "date": obj.date,
                "charge_hour": charge_hour,  # Добавляем числовое значение часа зарядки
                "discharge_hour": discharge_hour,  # Добавляем числовое значение часа разрядки
                "charge_start": obj.charge_start,
                "charge_end": obj.charge_end,
                "discharge_start": obj.discharge_start,
                "discharge_end": obj.discharge_end,
                "charge_price": obj.charge_price,
                "discharge_price": obj.discharge_price,
                "profit": obj.profit,
                "profit_after_losses": profit_after_losses
            }
        return super().default(obj)

def serialize_to_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert object to JSON-compatible format, correctly handling datetime."""
    return json.loads(json.dumps(data, cls=CustomJSONEncoder))

@router.post("/optimize", response_model=OptimizationResponse, summary="Optimize charge/discharge cycles")
async def optimize_cycles(
    start_date: Optional[datetime] = Query(None, description="Start date (format: YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (format: YYYY-MM-DD)"),
    threshold: float = Query(0.0, description="Profit threshold (EUR)"),
    use_test_data: bool = Query(None, description="Use test data instead of real API")
):
    """
    Optimizes battery charge/discharge cycles based on market data.
    
    - **start_date**: Start date in YYYY-MM-DD format
    - **end_date**: End date in YYYY-MM-DD format
    - **threshold**: Minimum profit threshold in EUR to display a cycle (default 0.0)
    - **use_test_data**: Use test data instead of real API (for debugging)
    
    Returns a list of optimal charge/discharge cycles in JSON format.
    """
    try:
        # If dates are not specified, use the last 30 days
        if not start_date:
            current_date = datetime.now()
            # Получаем последний день предыдущего месяца (конец периода по умолчанию)
            end_date = current_date.replace(day=1) - timedelta(days=1)
            # Получаем первый день предыдущего месяца (начало периода по умолчанию)
            start_date = end_date.replace(day=1)
            logger.info(f"Using default date range: {start_date} to {end_date}")
        elif not end_date:
            # Если указана только начальная дата, берем 30 дней начиная с нее
            end_date = start_date + timedelta(days=30)
        
        logger.info(f"Optimization request from {start_date} to {end_date}, threshold: {threshold}")
        
        # Determine whether to use test data
        from app.core.config import settings
        if use_test_data is None:
            use_test_data = settings.USE_TEST_DATA_BY_DEFAULT
        
        is_test_data = use_test_data
        data_source_message = ""
        
        if use_test_data:
            logger.info("Using test data for optimization (user requested)")
            market_data = await market_service.generate_test_data(start_date, end_date)
            data_source_message = "Using test data as requested by user"
        else:
            try:
                # Try to get data through the API
                logger.info("Requesting real data from Netztransparenz API")
                market_data = await market_service.get_market_data(start_date, end_date)
                
                # Check if data was received
                if market_data and len(market_data) > 0:
                    is_test_data = False
                    data_source_message = "Data retrieved from Netztransparenz API"
                    logger.info(f"Successfully received {len(market_data)} records from API")
                else:
                    # If no data, use test data
                    logger.warning("API returned no data, using test data")
                    market_data = await market_service.generate_test_data(start_date, end_date)
                    is_test_data = True
                    data_source_message = "API returned no data. Using test data."
            except Exception as api_error:
                # If it failed, use test data
                logger.warning(f"Error when accessing the API: {str(api_error)}. Using test data.")
                market_data = await market_service.generate_test_data(start_date, end_date)
                is_test_data = True
                data_source_message = f"API Error. Using test data."
            
        # Check if there is data
        if not market_data or len(market_data) == 0:
            raise HTTPException(status_code=404, detail="No market data found for the specified period")
        
        # Optimize cycles
        cycles = optimizer_service.process_data(market_data, threshold)
        
        # Convert to response format
        response_cycles = optimizer_service.to_optimization_response(cycles)
        
        # Create response with additional header
        response_data = serialize_to_json({
            "cycles": response_cycles,
            "is_test_data": is_test_data,
            "message": data_source_message
        })
        
        response = JSONResponse(content=response_data)
        response.headers["X-Test-Data"] = str(is_test_data).lower()
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error during cycle optimization: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/optimize-csv", response_class=PlainTextResponse, summary="Optimize cycles and export as CSV")
async def optimize_cycles_csv(
    start_date: Optional[datetime] = Query(None, description="Start date (format: YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (format: YYYY-MM-DD)"),
    threshold: float = Query(0.0, description="Profit threshold (EUR)"),
    use_test_data: bool = Query(None, description="Use test data instead of real API")
):
    """
    Optimizes charge/discharge cycles and returns the result in CSV format.
    
    - **start_date**: Start date in YYYY-MM-DD format
    - **end_date**: End date in YYYY-MM-DD format
    - **threshold**: Minimum profit threshold in EUR to display a cycle (default 0.0)
    - **use_test_data**: Use test data instead of real API (for debugging)
    
    Returns a CSV file with optimal cycles.
    """
    try:
        # If dates are not specified, use the last 30 days
        if not start_date:
            current_date = datetime.now()
            # Получаем последний день предыдущего месяца (конец периода по умолчанию)
            end_date = current_date.replace(day=1) - timedelta(days=1)
            # Получаем первый день предыдущего месяца (начало периода по умолчанию)
            start_date = end_date.replace(day=1)
            logger.info(f"Using default date range: {start_date} to {end_date}")
        elif not end_date:
            # Если указана только начальная дата, берем 30 дней начиная с нее
            end_date = start_date + timedelta(days=30)
        
        logger.info(f"CSV optimization request from {start_date} to {end_date}, threshold: {threshold}")
        
        # Determine whether to use test data
        from app.core.config import settings
        if use_test_data is None:
            use_test_data = settings.USE_TEST_DATA_BY_DEFAULT
        
        is_test_data = use_test_data
            
        if use_test_data:
            logger.info("Using test data for CSV optimization (user requested)")
            market_data = await market_service.generate_test_data(start_date, end_date)
        else:
            try:
                # Try to get data through the API
                logger.info("Requesting real data from Netztransparenz API for CSV")
                market_data = await market_service.get_market_data(start_date, end_date)
                
                # Check if data was received
                if market_data and len(market_data) > 0:
                    is_test_data = False
                    logger.info(f"Successfully received {len(market_data)} records from API for CSV")
                else:
                    # If no data, use test data
                    logger.warning("API returned no data for CSV, using test data")
                    market_data = await market_service.generate_test_data(start_date, end_date)
                    is_test_data = True
            except Exception as api_error:
                # If it failed, use test data
                logger.warning(f"Error when accessing API for CSV: {str(api_error)}. Using test data.")
                market_data = await market_service.generate_test_data(start_date, end_date)
                is_test_data = True
            
        # Check if there is data
        if not market_data or len(market_data) == 0:
            raise HTTPException(status_code=404, detail="No market data found for the specified period")
        
        # Optimize cycles
        cycles = optimizer_service.process_data(market_data, threshold)
        
        # Convert to CSV
        csv_content = optimizer_service.to_csv(cycles)
        
        # Create response with data source header
        response = PlainTextResponse(content=csv_content)
        response.headers["X-Test-Data"] = str(is_test_data).lower()
        response.headers["Content-Disposition"] = f"attachment; filename=optimization_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error during CSV cycle optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/upload-csv", response_model=OptimizationResponse, summary="Upload CSV and optimize cycles")
async def process_csv(
    file: UploadFile = File(..., description="CSV file with market data"),
    threshold: float = Form(0.0, description="Profit threshold (EUR)")
):
    """
    Processes the uploaded CSV file and returns optimized cycles.
    
    - **file**: CSV file with market data (separator ";", decimal separator ",")
    - **threshold**: Minimum profit threshold in EUR to display a cycle (default 0.0)
    
    Returns a list of optimal charge/discharge cycles in JSON format.
    """
    try:
        logger.info(f"Upload and process CSV, threshold: {threshold}")
        
        # Read file contents
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # Parse CSV
        market_data = market_service.parse_csv_data(csv_content)
        
        if not market_data or len(market_data) == 0:
            raise HTTPException(status_code=400, detail="Could not extract market data from CSV file")
        
        # Optimize cycles
        cycles = optimizer_service.process_data(market_data, threshold)
        
        # Convert to response format
        response_cycles = optimizer_service.to_optimization_response(cycles)
        
        # Serialize data to prevent errors with datetime and OptimizationCycle
        response_data = serialize_to_json({"cycles": response_cycles, "is_test_data": False})
        return JSONResponse(content=response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@router.post("/upload-csv-download", response_class=PlainTextResponse, summary="Upload CSV and get results as CSV")
async def process_csv_download(
    file: UploadFile = File(..., description="CSV file with market data"),
    threshold: float = Form(0.0, description="Profit threshold (EUR)")
):
    """
    Processes the uploaded CSV file and returns optimized cycles in CSV format.
    
    - **file**: CSV file with market data (separator ";", decimal separator ",")
    - **threshold**: Minimum profit threshold in EUR to display a cycle (default 0.0)
    
    Returns a CSV file with optimal cycles.
    """
    try:
        logger.info(f"Upload and process CSV with CSV return, threshold: {threshold}")
        
        # Read file contents
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # Parse CSV
        market_data = market_service.parse_csv_data(csv_content)
        
        if not market_data or len(market_data) == 0:
            raise HTTPException(status_code=400, detail="Could not extract market data from CSV file")
        
        # Optimize cycles
        cycles = optimizer_service.process_data(market_data, threshold)
        
        # Convert to CSV
        result_csv = optimizer_service.to_csv(cycles)
        
        return result_csv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CSV and outputting to CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
