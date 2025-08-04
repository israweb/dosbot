import time
import pandas as pd
import matplotlib.pyplot as plt
from bot import CryptoBot
from config import Config

def plot_btc_chart():
    data = pd.read_csv('../data/btcusdt_1m.csv')
    plt.figure(figsize=(12, 6))
    plt.plot(data['close'], label='Цена закрытия')
    plt.title('График курса BTC/USDT')
    plt.xlabel('Индекс (время)')
    plt.ylabel('Цена (USDT)')
    plt.legend()
    plt.show()

def main():
    config = Config()
    data = pd.read_csv('../data/btcusdt_1m.csv')
    bot = CryptoBot(config, data)
    while True:
        bot.trade()
        time.sleep(config.trade_interval)

if __name__ == "__main__":
    # Для построения графика раскомментируйте строку ниже:
    # plot_btc_chart()
    main()