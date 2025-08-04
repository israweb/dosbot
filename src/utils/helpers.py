def fetch_data(symbol, start_date, end_date):
    import pandas as pd
    import requests

    url = f"https://api.example.com/data?symbol={symbol}&start={start_date}&end={end_date}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        raise Exception("Error fetching data from API")

def calculate_indicators(data):
    data['SMA'] = data['close'].rolling(window=14).mean()
    data['EMA'] = data['close'].ewm(span=14, adjust=False).mean()
    data['RSI'] = compute_rsi(data['close'], window=14)
    return data

def compute_rsi(series, window):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))