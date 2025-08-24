import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# API настройки (лучше хранить в переменных окружения)
API_KEY = os.getenv("API_KEY", "your_api_key_here")
API_SECRET = os.getenv("API_SECRET", "your_api_secret_here")
BASE_URL = os.getenv("BASE_URL", "https://api.yourcryptocurrencyexchange.com")

MODEL_PARAMS = {
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 32
}

TRADING_SETTINGS = {
    "trade_amount": 0.01,
    "stop_loss": 0.05,
    "take_profit": 0.1
}

class Config:
    def __init__(self):
        self.trade_interval = 60  # интервал между сделками в секундах
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
        self.model_params = MODEL_PARAMS
        self.trading_settings = TRADING_SETTINGS
        
        # Дополнительные настройки
        self.symbol = "BTCUSDT"
        self.timeframe = "1h"
        self.max_retries = 3
        self.log_level = "INFO"