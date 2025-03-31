import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import json
import random
import base64
import aiohttp
import csv
import io
import urllib.parse
import time
from io import StringIO

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.market_data import MarketDataItem
from app.utils.csv_handler import parse_csv

class MarketDataService:
    
    def __init__(self):
        self._token = None
        self._token_expiry = 0
    
    async def _get_token(self) -> str:
        current_time = time.time()
        if self._token and self._token_expiry > current_time:
            logger.debug("Using an existing token")
            return self._token
        
        logger.info("Receiving a new Bearer-token for the Netztransparenz API")
        
        try:
            data = {
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET,
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(settings.TOKEN_URL, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error when receiving a token: {response.status}, {error_text}")
                        raise Exception(f"Error when receiving a token: {response.status}")
                    
                    token_data = await response.json()
                    
                    if 'access_token' not in token_data:
                        logger.error(f"The response does not contain a token: {token_data}")
                        raise Exception("The response does not contain a token")
                    
                    self._token = token_data['access_token']
                    expires_in = token_data.get('expires_in', settings.TOKEN_LIFETIME)
                    self._token_expiry = current_time + expires_in
                    
                    logger.info(f"Received a new token, valid until {datetime.fromtimestamp(self._token_expiry)}")
                    return self._token
        except Exception as e:
            logger.error(f"Error when receiving a token: {str(e)}")
            raise Exception(f"Failed to receive an authorization token: {str(e)}")
    
    async def get_market_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        logger.info(f"Getting market data from {start_date} to {end_date}")
        
        try:
            token = await self._get_token()
            
            start_str = start_date.replace(hour=0, minute=0, second=0).strftime(settings.API_DATETIME_FORMAT)
            end_str = end_date.replace(hour=23, minute=59, second=59).strftime(settings.API_DATETIME_FORMAT)
            
            start_encoded = urllib.parse.quote(start_str)
            end_encoded = urllib.parse.quote(end_str)
            
            url = f"{settings.MARKET_API_BASE_URL}/{start_encoded}/{end_encoded}"
            
            logger.info(f"Request to API: {url}")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "*/*"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API Error: {response.status}, {error_text}")
                        raise Exception(f"API returned an error: {response.status}, text: {error_text}")
                    
                    csv_content = await response.text()
                    logger.debug(f"Received API response: first 200 characters: {csv_content[:200]}")
                    
                    return self._parse_csv_response(csv_content)
        except Exception as e:
            logger.error(f"Error when receiving market data: {str(e)}")
            raise Exception(f"Error when receiving market data: {str(e)}")
    
    def _parse_csv_response(self, csv_content: str) -> List[Dict[str, Any]]:
        result = []
        
        try:
            csv_file = StringIO(csv_content)
            
            reader = csv.reader(csv_file, delimiter=';')
            
            headers = next(reader, None)
            if not headers:
                logger.warning("CSV does not contain a header")
                return result
            
            logger.debug(f"CSV headers: {headers}")
            
            for row in reader:
                if len(row) < 6: 
                    logger.warning(f"Not enough data in the CSV line: {row}")
                    continue
                
                try:
                    date_str = row[0].strip()  
                    
                    hour_str = row[1].strip()  
                    hour = int(hour_str.split(':')[0])

                    price_str = row[5].strip().replace(',', '.')  
                    price_ct_kwh = float(price_str)
                    price_eur = price_ct_kwh / 100.0
                    
                    result.append({
                        "date": date_str,
                        "hour": hour,
                        "price_ct_kwh": price_ct_kwh,
                        "price_eur": price_eur
                    })
                except Exception as e:
                    logger.warning(f"Error when parsing a CSV line: {e}, line: {row}")
                    continue
            
            logger.info(f"Successfully parsed {len(result)} records from the API response")
            return result
        except Exception as e:
            logger.error(f"Error when parsing a CSV response: {str(e)}")
            raise Exception(f"Error while parsing API response: {str(e)}")
    
    async def generate_test_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        logger.info("Generation of test data on market prices")
        
        days = (end_date - start_date).days + 1
        if days <= 0:
            days = 1
        
        current_date = start_date
        result = []
        
        for _ in range(days):
            base_price = random.uniform(5.0, 15.0)  
            
            date_str = current_date.strftime("%d.%m.%Y")
           
            for hour in range(24):
                hour_factor = 1.0 + 0.5 * (
                    (0.5 * (hour - 3) / 9.0) if hour < 12 else 
                    (0.5 - 0.5 * (hour - 12) / 12.0)
                )
                
                noise = random.uniform(-0.5, 0.5)
                
                price_ct_kwh = max(1.0, base_price * hour_factor + noise)
                
                result.append({
                    "date": date_str,
                    "hour": hour,
                    "price_ct_kwh": price_ct_kwh,
                    "price_eur": price_ct_kwh / 100.0
                })
            
            current_date += timedelta(days=1)
        
        logger.info(f"Generated {len(result)} test records of market data")
        return result

    def parse_csv_data(self, csv_content: str) -> List[Dict[str, Any]]:
        logger.info("Parsing CSV data for analysis")
        
        result = []
        
        csv_file = io.StringIO(csv_content)
        
        try:
            reader = csv.reader(csv_file, delimiter=';')
            
            headers = next(reader, None)
            
            for row in reader:
                if len(row) < 6:  
                    logger.warning(f"Not enough data in the CSV line: {row}")
                    continue
                
                try:
                    date_str = row[0].strip()
                    
                    if "-" in date_str and len(date_str) == 10:
                        try:
                            dt = datetime.fromisoformat(date_str)
                            date_str = dt.strftime("%d.%m.%Y")
                        except ValueError:
                            logger.warning(f"Unable to convert the date: {date_str}")
                    
                    hour_str = row[1].strip().split(':')[0]  
                    hour = int(hour_str)
                    
                    price_str = row[5].strip().replace(',', '.')
                    price_ct_kwh = float(price_str)
                    price_eur = price_ct_kwh / 100.0
                    
                    result.append({
                        "date": date_str,
                        "hour": hour,
                        "price_ct_kwh": price_ct_kwh,
                        "price_eur": price_eur
                    })
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error when parsing a CSV line: {e}, line: {row}")
                    continue
            
            logger.info(f"Successfully parsed {len(result)} records from CSV")
            return result
        except Exception as e:
            logger.error(f"Error when parsing a CSV: {str(e)}")
            raise
