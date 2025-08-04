API_KEY = "your_api_key_here"
API_SECRET = "your_api_secret_here"
BASE_URL = "https://api.yourcryptocurrencyexchange.com"

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