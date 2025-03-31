from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.schemas.market_data import MarketDataResponse
from app.services.market_data import MarketDataService
from app.core.logging_config import logger
from app.core.config import settings

router = APIRouter()

# Создаем экземпляр сервиса
market_service = MarketDataService()

# Кастомный JSON энкодер для обработки datetime объектов
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_to_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Преобразует объект в JSON-совместимый формат, правильно обрабатывая datetime."""
    return json.loads(json.dumps(data, cls=CustomJSONEncoder))

@router.get("/", response_model=MarketDataResponse, summary="Get market data for the period")
async def get_market_data(
    start_date: Optional[datetime] = Query(None, description="Start Date (Format: YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End Date (Format: YYYY-MM-DD)"),
    use_test_data: bool = Query(None, description="Use test data instead of the actual API")
):
    
    try:
        if not start_date:
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=7)
        elif not end_date:
            end_date = start_date + timedelta(days=7)
        
        logger.info(f"Запрос данных рынка с {start_date.isoformat()} по {end_date.isoformat()}")
       
        if use_test_data is None:
            use_test_data = settings.USE_TEST_DATA_BY_DEFAULT
            
        if use_test_data:
            logger.info("Use test data instead of real data (at the user's request)")
            market_data = await market_service.generate_test_data(start_date, end_date)
            
            response_data = serialize_to_json({
                "data": market_data,
                "is_test_data": True,
                "message": "Test data is used, as requested by the user"
            })
            
            response = JSONResponse(content=response_data)
            response.headers["X-Test-Data"] = "true"
            response.headers["X-Test-Reason"] = "user_request"
            return response
        
        try:
            market_data = await market_service.get_market_data(start_date, end_date)
            
            if not market_data or len(market_data) == 0:
                reason = "empty_response"
                message = "API did not return data for the specified period. Test data is used."
                logger.warning(message)
                
                market_data = await market_service.generate_test_data(start_date, end_date)
                
                response_data = serialize_to_json({
                    "data": market_data,
                    "is_test_data": True,
                    "message": message
                })
                
                response = JSONResponse(content=response_data)
                response.headers["X-Test-Data"] = "true"
                response.headers["X-Test-Reason"] = reason
                return response
            
            response_data = serialize_to_json({
                "data": market_data,
                "is_test_data": False,
                "message": "Data received from the Netztransparenz API"
            })
            
            response = JSONResponse(content=response_data)
            response.headers["X-Test-Data"] = "false"
            response.headers["X-Data-Source"] = "netztransparenz_api"
            return response
            
        except Exception as api_error:
            error_msg = str(api_error)
            reason = "api_error"
            
            if "Failed to obtain authorization token" in error_msg:
                reason = "auth_token_error"
                message = "Error receiving an authorization token. Test data is used."
            elif "404" in error_msg:
                reason = "api_not_found"
                message = "API is not available at the specified URL. Test data is used."
            elif "401" in error_msg or "403" in error_msg:
                reason = "api_auth_error"
                message = "Authentication error when accessing the API. Test data is used."
            elif "timeout" in error_msg.lower():
                reason = "api_timeout"
                message = "The time to wait for a response from the API has been exceeded. Test data is used."
            elif "connect" in error_msg.lower():
                reason = "api_connect_error"
                message = "Failed to connect to API. Test data is being used."
            else:
                message = f"Error when accessing the API. Test data is used."
            
            logger.error(f"API Error ({reason}): {error_msg}")
            
            market_data = await market_service.generate_test_data(start_date, end_date)
            
            response_data = serialize_to_json({
                "data": market_data,
                "is_test_data": True,
                "message": message,
                "error": error_msg
            })
            
            response = JSONResponse(content=response_data)
            response.headers["X-Test-Data"] = "true"
            response.headers["X-Test-Reason"] = reason
            return response
            
    except Exception as e:
        logger.error(f"Unhandled error when receiving market data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
