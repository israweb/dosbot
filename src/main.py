import time
import pandas as pd
import matplotlib.pyplot as plt
import os
from bot import CryptoBot
from config import Config

def plot_btc_chart():
    """
    Draws a chart of BTC/USDT price over time.

    Data is retrieved from a CSV file in the 'data' directory.
    The chart displays the closing price of BTC/USDT over time.
    """
    try:
        # Используем существующий файл данных
        data = pd.read_csv('processed_data/input_data.csv')
        plt.figure(figsize=(12, 6))
        plt.plot(data['close'], label='Цена закрытия')
        plt.title('График курса BTC/USDT')
        plt.xlabel('Индекс (время)')
        plt.ylabel('Цена (USDT)')
        plt.legend()
        
        # Сохраняем график в файл
        plt.savefig('btc_chart.png', dpi=300, bbox_inches='tight')
        print("График сохранен в файл: btc_chart.png")
        
        plt.show()
    except FileNotFoundError:
        print("Ошибка: Файл данных не найден. Проверьте папку data/")
    except Exception as e:
        print(f"Ошибка при построении графика: {e}")

def main():
    """
    Главная функция, которая запускает торговлю.
    
    Она настраивает конфигурацию, загружает данные, создает объект CryptoBot
    и запускает торговлю.
    """
    try:
        config = Config()
        
        # Проверяем наличие файла данных
        data_file = 'processed_data/input_data.csv'
        if not os.path.exists(data_file):
            print(f"Файл {data_file} не найден. Используем другой файл...")
            # Пробуем найти любой файл с данными BTC
            data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
            if data_files:
                data_file = f"data/{data_files[0]}"
                print(f"Используем файл: {data_file}")
            else:
                print("Ошибка: Не найдены файлы с данными BTC")
                return
        
        data = pd.read_csv(data_file)
        print(f"Загружены данные из файла: {data_file}")
        print(f"Количество записей: {len(data)}")
        
        bot = CryptoBot(config, data)
        
        print("Запуск торгового бота...")
        while True:
            bot.trade()
            time.sleep(config.trade_interval)
            
    except KeyboardInterrupt:
        print("\nТорговля остановлена пользователем")
    except Exception as e:
        print(f"Ошибка в главной функции: {e}")

if __name__ == "__main__":
    # Для построения графика раскомментируйте строку ниже:
    plot_btc_chart()
    main()