import csv
import io
from typing import List, Dict, Any
from app.schemas.market_data import MarketDataItem
from datetime import datetime
from app.core.logging_config import logger

def parse_csv(csv_content: str) -> List[MarketDataItem]:
    """
    Парсит CSV файл с данными рынка электроэнергии.
    Ожидаемый формат:
    Datum;von;Zeitzone von;bis;Zeitzone bis;Spotmarktpreis in ct/kWh
    с значениями, разделенными точкой с запятой, и с запятой в качестве десятичного разделителя
    """
    try:
        result = []
        # Читаем CSV
        reader = csv.reader(io.StringIO(csv_content), delimiter=';')
        
        # Получаем заголовки
        headers = next(reader)
        
        # Проверяем заголовки
        expected_headers = ["Datum", "von", "Zeitzone von", "bis", "Zeitzone bis", "Spotmarktpreis in ct/kWh"]
        
        # Проверяем, что все ожидаемые заголовки присутствуют (порядок может быть разным)
        if not all(header in headers for header in expected_headers):
            logger.error(f"Неверный формат CSV: ожидались заголовки {expected_headers}, получены {headers}")
            raise ValueError(f"Неверный формат CSV. Ожидались колонки: {', '.join(expected_headers)}")
        
        # Индексы колонок
        date_idx = headers.index("Datum")
        hour_from_idx = headers.index("von")
        price_idx = headers.index("Spotmarktpreis in ct/kWh")
        
        # Парсим строки
        for row in reader:
            if not row:
                continue  # Пропускаем пустые строки
            
            try:
                # Получаем данные из строки
                date_str = row[date_idx].strip()
                hour_str = row[hour_from_idx].strip()
                price_str = row[price_idx].strip().replace(',', '.')
                
                # Парсим дату (ожидаем формат DD.MM.YYYY)
                try:
                    date = datetime.strptime(date_str, "%d.%m.%Y")
                except ValueError:
                    # Пробуем альтернативный формат YYYY-MM-DD
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Парсим час
                hour = int(hour_str)
                
                # Парсим цену
                price_ct_kwh = float(price_str)
                
                # Создаем объект MarketDataItem
                item = MarketDataItem(
                    date=date,
                    hour=hour,
                    price_ct_kwh=price_ct_kwh,
                    price_eur=price_ct_kwh / 100.0  # конвертируем центы в евро
                )
                
                result.append(item)
            except Exception as e:
                logger.warning(f"Ошибка при парсинге строки CSV {row}: {str(e)}")
                # Не прерываем работу, просто пропускаем некорректную строку
        
        if not result:
            logger.error("CSV успешно обработан, но данные не найдены")
            raise ValueError("В CSV файле не найдены данные в ожидаемом формате")
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при парсинге CSV: {str(e)}")
        raise

def format_to_csv(cycles: List[Dict[str, Any]]) -> str:
    """
    Форматирует результаты оптимизации в CSV.
    """
    if not cycles:
        return "Cycle;Date;Charge_Start;Charge_End;Discharge_Start;Discharge_End;Charge_Price;Discharge_Price;Profit\n"
    
    csv_content = "Cycle;Date;Charge_Start;Charge_End;Discharge_Start;Discharge_End;Charge_Price;Discharge_Price;Profit (EUR)\n"
    
    for cycle in cycles:
        date = cycle["date"].strftime("%d.%m.%Y") if isinstance(cycle["date"], datetime) else cycle["date"]
        
        # Форматируем цены с запятой в качестве десятичного разделителя
        charge_price = str(round(cycle["charge_price"], 4)).replace('.', ',')
        discharge_price = str(round(cycle["discharge_price"], 4)).replace('.', ',')
        profit = str(round(cycle["profit"], 2)).replace('.', ',')
        
        row = f"{cycle['cycle']};{date};{cycle['charge_start']};{cycle['charge_end']};"
        row += f"{cycle['discharge_start']};{cycle['discharge_end']};"
        row += f"{charge_price};{discharge_price};{profit}\n"
        
        csv_content += row
    
    return csv_content
