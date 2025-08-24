import pandas as pd
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data(symbol, start_date, end_date):
    """
    Получение данных с API с обработкой ошибок
    """
    try:
        url = f"https://api.example.com/data?symbol={symbol}&start={start_date}&end={end_date}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            logger.error(f"API вернул статус {response.status_code}")
            raise Exception(f"Error fetching data from API: {response.status_code}")
            
    except requests.exceptions.Timeout:
        logger.error("Таймаут при запросе к API")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при запросе к API: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении данных: {e}")
        raise

def calculate_indicators(data):
    """
    Расчет технических индикаторов с проверкой данных
    """
    try:
        if data.empty:
            logger.warning("Пустые данные для расчета индикаторов")
            return data
            
        if 'close' not in data.columns:
            logger.error("Колонка 'close' отсутствует в данных")
            return data
            
        # Простые скользящие средние
        data['SMA_14'] = data['close'].rolling(window=14).mean()
        data['SMA_50'] = data['close'].rolling(window=50).mean()
        
        # Экспоненциальные скользящие средние
        data['EMA_14'] = data['close'].ewm(span=14, adjust=False).mean()
        data['EMA_50'] = data['close'].ewm(span=50, adjust=False).mean()
        
        # RSI
        data['RSI'] = compute_rsi(data['close'], window=14)
        
        # Bollinger Bands
        data['BB_upper'], data['BB_lower'] = compute_bollinger_bands(data['close'])
        
        logger.info("Технические индикаторы рассчитаны успешно")
        return data
        
    except Exception as e:
        logger.error(f"Ошибка при расчете индикаторов: {e}")
        return data

def compute_rsi(series, window=14):
    """
    Расчет RSI (Relative Strength Index)
    """
    try:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        # Избегаем деления на ноль
        loss = loss.replace(0, 0.0001)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    except Exception as e:
        logger.error(f"Ошибка при расчете RSI: {e}")
        return pd.Series([50] * len(series), index=series.index)

def compute_bollinger_bands(series, window=20, num_std=2):
    """
    Расчет полос Боллинджера
    """
    try:
        sma = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return upper_band, lower_band
        
    except Exception as e:
        logger.error(f"Ошибка при расчете полос Боллинджера: {e}")
        return pd.Series([0] * len(series), index=series.index), pd.Series([0] * len(series), index=series.index)