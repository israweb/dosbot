#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ZigZag15MProcessor:
    """
    Процессор для создания зигзага на 15-минутных данных BTC.
    -1 = максимум (сигнал продажи)
    1 = минимум (сигнал покупки)
    0 = обычный бар
    """
    
    def __init__(self, data_file="processed_data/input_data.csv", deviation=1.0):
        """
        Инициализация процессора.
        
        Параметры:
        - data_file: путь к файлу с данными
        - deviation: минимальное отклонение в процентах (по умолчанию 1%)
        """
        self.data_file = data_file
        self.deviation = deviation
        self.data = None
        self.zigzag_points = []
        
    def load_data(self):
        """
        Загружает данные из файла.
        """
        print(f"Загрузка данных из {self.data_file}...")
        
        try:
            self.data = pd.read_csv(self.data_file)
            print(f"✓ Загружены данные: {len(self.data)} записей")
            
            # Проверяем наличие необходимых колонок
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            
            if missing_columns:
                print(f"⚠️ Отсутствуют колонки: {missing_columns}")
                return False
            
            # Выводим информацию о данных
            print(f"✓ Колонки: {list(self.data.columns)}")
            print(f"✓ Период: {self.data.index[0]} - {self.data.index[-1]}")
            print(f"✓ Размер данных: {len(self.data)} x {len(self.data.columns)}")
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Файл {self.data_file} не найден!")
            return False
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            return False
    
    def calculate_zigzag(self):
        """
        Правильный алгоритм зигзага по точному описанию пользователя:
        1. Первая точка = Low[0] (зафиксирована)
        2. Работаем только с High/Low (не Close)
        3. Динамическое обновление экстремумов
        4. Двухэтапная фиксация: кандидат → фиксация при противоположном экстремуме
        
        -1 = максимум (сигнал продажи)
        1 = минимум (сигнал покупки)
        """
        print(f"Вычисление зигзага с отклонением {self.deviation}%...")
        
        if self.data is None:
            print("❌ Данные не загружены!")
            return False
        
        high = self.data['High'].values
        low = self.data['Low'].values
        n = len(high)
        
        # Инициализируем массив зигзага
        zigzag_series = np.zeros(n)
        zigzag_points = []
        
        if n < 3:
            print("❌ Недостаточно данных для вычисления зигзага!")
            return False
        
        # ИНИЦИАЛИЗАЦИЯ согласно алгоритму
        last_zigzag_price = low[0]       # Первая точка - Low первой свечи
        last_zigzag_idx = 0              # Индекс первой точки
        last_zigzag_type = 1             # Тип: 1 = минимум
        zigzag_series[0] = 1             # Фиксируем первую точку как минимум
        zigzag_points.append((0, low[0], 1))
        
        current_max_price = high[0]      # Текущий максимум
        current_max_idx = 0              # Индекс текущего максимума
        max_candidate = False            # Максимум еще не кандидат
        
        current_min_price = low[0]       # Текущий минимум 
        current_min_idx = 0              # Индекс текущего минимума
        min_candidate = False            # Минимум еще не кандидат
        
        search_direction = -1            # -1 = ищем максимум, 1 = ищем минимум
        
        # ОСНОВНОЙ ЦИКЛ
        for i in range(1, n):
            
            if search_direction == -1:  # ИЩЕМ МАКСИМУМ
                
                # 1. Обновляем текущий максимум
                if high[i] > current_max_price:
                    current_max_price = high[i]
                    current_max_idx = i
                
                # 2. Проверяем, стал ли максимум кандидатом
                if not max_candidate:
                    deviation = (current_max_price - last_zigzag_price) / last_zigzag_price * 100
                    if deviation >= self.deviation:
                        max_candidate = True  # Максимум стал кандидатом
                
                # 3. Если максимум уже кандидат, ищем минимум
                if max_candidate:
                    deviation_down = (current_max_price - low[i]) / current_max_price * 100
                    
                    if deviation_down >= self.deviation:
                        # ФИКСИРУЕМ МАКСИМУМ И МИНИМУМ
                        zigzag_series[current_max_idx] = -1
                        zigzag_series[i] = 1
                        zigzag_points.append((current_max_idx, current_max_price, -1))
                        zigzag_points.append((i, low[i], 1))
                        
                        # Обновляем состояние
                        last_zigzag_price = low[i]
                        last_zigzag_idx = i
                        last_zigzag_type = 1
                        
                        # Начинаем поиск нового минимума
                        current_min_price = low[i]
                        current_min_idx = i
                        min_candidate = False
                        search_direction = 1  # Переключаемся на поиск минимума
                    
                    else:
                        # Проверяем, не нашли ли лучший максимум
                        if high[i] > current_max_price:
                            current_max_price = high[i]
                            current_max_idx = i
            
            else:  # ИЩЕМ МИНИМУМ (search_direction == 1)
                
                # 1. Обновляем текущий минимум
                if low[i] < current_min_price:
                    current_min_price = low[i]
                    current_min_idx = i
                
                # 2. Проверяем, стал ли минимум кандидатом
                if not min_candidate:
                    deviation = (last_zigzag_price - current_min_price) / last_zigzag_price * 100
                    if deviation >= self.deviation:
                        min_candidate = True  # Минимум стал кандидатом
                
                # 3. Если минимум уже кандидат, ищем максимум
                if min_candidate:
                    deviation_up = (high[i] - current_min_price) / current_min_price * 100
                    
                    if deviation_up >= self.deviation:
                        # ФИКСИРУЕМ МИНИМУМ И МАКСИМУМ
                        zigzag_series[current_min_idx] = 1
                        zigzag_series[i] = -1
                        zigzag_points.append((current_min_idx, current_min_price, 1))
                        zigzag_points.append((i, high[i], -1))
                        
                        # Обновляем состояние
                        last_zigzag_price = high[i]
                        last_zigzag_idx = i
                        last_zigzag_type = -1
                        
                        # Начинаем поиск нового максимума
                        current_max_price = high[i]
                        current_max_idx = i
                        max_candidate = False
                        search_direction = -1  # Переключаемся на поиск максимума
                    
                    else:
                        # Проверяем, не нашли ли лучший минимум
                        if low[i] < current_min_price:
                            current_min_price = low[i]
                            current_min_idx = i
        
        # Добавляем колонку зигзага к данным с правильным названием
        zigzag_column_name = f"zigzag ({self.deviation}%)"
        self.data[zigzag_column_name] = zigzag_series
        self.zigzag_points = zigzag_points
        
        # Статистика
        max_count = np.sum(zigzag_series == -1)
        min_count = np.sum(zigzag_series == 1)
        
        print(f"✓ Зигзаг вычислен:")
        print(f"  - Максимумов (сигналы продажи): {max_count}")
        print(f"  - Минимумов (сигналы покупки): {min_count}")
        print(f"  - Всего точек зигзага: {len(zigzag_points)}")
        
        return True
    
    def create_technical_features(self):
        """
        Создает технические индикаторы для анализа.
        """
        print("Создание технических индикаторов...")
        
        df = self.data.copy()
        
        # Базовые признаки цены
        df['price_change'] = df['Close'].pct_change()
        df['price_change_abs'] = df['price_change'].abs()
        df['high_low_ratio'] = df['High'] / df['Low']
        df['open_close_ratio'] = df['Open'] / df['Close']
        df['body_size'] = (df['Close'] - df['Open']) / df['Open']
        
        # Волатильность
        df['volatility_5'] = df['price_change'].rolling(window=5).std()
        df['volatility_10'] = df['price_change'].rolling(window=10).std()
        df['volatility_20'] = df['price_change'].rolling(window=20).std()
        
        # Скользящие средние
        df['sma_5'] = df['Close'].rolling(window=5).mean()
        df['sma_10'] = df['Close'].rolling(window=10).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['ema_5'] = df['Close'].ewm(span=5).mean()
        df['ema_10'] = df['Close'].ewm(span=10).mean()
        df['ema_20'] = df['Close'].ewm(span=20).mean()
        
        # Отклонения от средних
        df['deviation_sma_5'] = (df['Close'] - df['sma_5']) / df['sma_5']
        df['deviation_sma_10'] = (df['Close'] - df['sma_10']) / df['sma_10']
        df['deviation_sma_20'] = (df['Close'] - df['sma_20']) / df['sma_20']
        df['deviation_ema_5'] = (df['Close'] - df['ema_5']) / df['ema_5']
        df['deviation_ema_10'] = (df['Close'] - df['ema_10']) / df['ema_10']
        df['deviation_ema_20'] = (df['Close'] - df['ema_20']) / df['ema_20']
        
        # Позиция цены в окне
        df['high_window_5'] = df['High'].rolling(window=5).max()
        df['low_window_5'] = df['Low'].rolling(window=5).min()
        df['position_5'] = (df['Close'] - df['low_window_5']) / (df['high_window_5'] - df['low_window_5'])
        
        df['high_window_10'] = df['High'].rolling(window=10).max()
        df['low_window_10'] = df['Low'].rolling(window=10).min()
        df['position_10'] = (df['Close'] - df['low_window_10']) / (df['high_window_10'] - df['low_window_10'])
        
        df['high_window_20'] = df['High'].rolling(window=20).max()
        df['low_window_20'] = df['Low'].rolling(window=20).min()
        df['position_20'] = (df['Close'] - df['low_window_20']) / (df['high_window_20'] - df['low_window_20'])
        
        # RSI
        gains = df['price_change'].where(df['price_change'] > 0, 0)
        losses = -df['price_change'].where(df['price_change'] < 0, 0)
        
        avg_gains_5 = gains.rolling(window=5).mean()
        avg_losses_5 = losses.rolling(window=5).mean()
        df['rsi_5'] = 100 - (100 / (1 + avg_gains_5 / avg_losses_5))
        
        avg_gains_10 = gains.rolling(window=10).mean()
        avg_losses_10 = losses.rolling(window=10).mean()
        df['rsi_10'] = 100 - (100 / (1 + avg_gains_10 / avg_losses_10))
        
        avg_gains_20 = gains.rolling(window=20).mean()
        avg_losses_20 = losses.rolling(window=20).mean()
        df['rsi_20'] = 100 - (100 / (1 + avg_gains_20 / avg_losses_20))
        
        # Тренды
        df['trend_5'] = df['Close'] - df['Close'].shift(5)
        df['trend_10'] = df['Close'] - df['Close'].shift(10)
        df['trend_20'] = df['Close'] - df['Close'].shift(20)
        
        # Импульс
        df['momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        df['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        df['momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        # Объем
        df['volume_sma_5'] = df['Volume'].rolling(window=5).mean()
        df['volume_sma_10'] = df['Volume'].rolling(window=10).mean()
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio_5'] = df['Volume'] / df['volume_sma_5']
        df['volume_ratio_10'] = df['Volume'] / df['volume_sma_10']
        df['volume_ratio_20'] = df['Volume'] / df['volume_sma_20']
        
        # Bollinger Bands
        df['bb_upper_20'] = df['sma_20'] + 2 * df['volatility_20'] * df['sma_20']
        df['bb_lower_20'] = df['sma_20'] - 2 * df['volatility_20'] * df['sma_20']
        df['bb_position_20'] = (df['Close'] - df['bb_lower_20']) / (df['bb_upper_20'] - df['bb_lower_20'])
        
        # Stochastic Oscillator
        df['stoch_k_14'] = 100 * (df['Close'] - df['Low'].rolling(window=14).min()) / (df['High'].rolling(window=14).max() - df['Low'].rolling(window=14).min())
        df['stoch_d_14'] = df['stoch_k_14'].rolling(window=3).mean()
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Удаляем NaN значения
        df = df.dropna()
        
        self.data = df
        print(f"✓ Создано технических индикаторов: {len(df.columns) - 6}")  # -6 для базовых колонок
        
        return True
    
    def plot_zigzag(self, save_path="zigzag_15m_chart.png"):
        """
        Строит график с зигзагом и сохраняет его.
        """
        print(f"Создание графика зигзага...")
        
        zigzag_column_name = f"zigzag ({self.deviation}%)"
        if self.data is None or zigzag_column_name not in self.data.columns:
            print("❌ Данные зигзага не найдены!")
            return False
        
        # Берем только последние 10000 записей для графика
        plot_data = self.data.tail(10000).copy()
        
        # Создаем график
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[3, 1])
        
        # Основной график цены
        ax1.plot(plot_data.index, plot_data['Close'], color='blue', alpha=0.7, linewidth=1, label='Цена закрытия')
        
        # Отмечаем точки зигзага
        max_points = plot_data[plot_data[zigzag_column_name] == -1]
        min_points = plot_data[plot_data[zigzag_column_name] == 1]
        
        if len(max_points) > 0:
            ax1.scatter(max_points.index, max_points['High'], 
                       color='red', marker='v', s=100, alpha=0.8, 
                       label=f'Максимумы (продажа) - {len(max_points)}')
        
        if len(min_points) > 0:
            ax1.scatter(min_points.index, min_points['Low'], 
                       color='green', marker='^', s=100, alpha=0.8, 
                       label=f'Минимумы (покупка) - {len(min_points)}')
        
        # Соединяем точки зигзага линиями
        zigzag_indices = plot_data[plot_data[zigzag_column_name] != 0].index
        zigzag_prices = []
        
        for idx in zigzag_indices:
            if plot_data.loc[idx, zigzag_column_name] == -1:  # Максимум
                zigzag_prices.append(plot_data.loc[idx, 'High'])
            else:  # Минимум
                zigzag_prices.append(plot_data.loc[idx, 'Low'])
        
        if len(zigzag_indices) > 1:
            ax1.plot(zigzag_indices, zigzag_prices, color='orange', linewidth=2, alpha=0.8, label='Зигзаг')
        
        # Настройки графика
        ax1.set_title(f'BTC/USDT 15m - ZigZag (отклонение {self.deviation}%) - Последние 10K записей', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Цена (USDT)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
        # График объема
        ax2.bar(plot_data.index, plot_data['Volume'], color='gray', alpha=0.6, width=1)
        ax2.set_ylabel('Объем', fontsize=12)
        ax2.set_xlabel('Время', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Настройка осей времени
        plt.setp(ax1.get_xticklabels(), visible=False)
        
        # Поворот подписей оси X
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Сохраняем график
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ График сохранен: {save_path}")
        
        plt.show()
        return True
    
    def save_enhanced_data(self, output_file="processed_data/ml_data.csv"):
        """
        Сохраняет данные с добавленными признаками.
        """
        print(f"Сохранение данных с признаками в {output_file}...")
        
        if self.data is None:
            print("❌ Данные не загружены!")
            return False
        
        try:
            self.data.to_csv(output_file, index=False)
            print(f"✓ Данные сохранены: {len(self.data)} записей, {len(self.data.columns)} колонок")
            
            # Выводим список всех колонок
            print(f"\nКолонки в файле:")
            for i, col in enumerate(self.data.columns, 1):
                print(f"  {i:2d}. {col}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return False
    
    def get_statistics(self):
        """
        Выводит статистику по данным.
        """
        if self.data is None:
            print("❌ Данные не загружены!")
            return
        
        print("\n" + "="*60)
        print("СТАТИСТИКА ДАННЫХ")
        print("="*60)
        
        # Статистика зигзага
        zigzag_column_name = f"zigzag ({self.deviation}%)"
        zigzag_stats = self.data[zigzag_column_name].value_counts()
        print(f"Распределение зигзага:")
        print(f"  - Обычные бары (0): {zigzag_stats.get(0, 0):,}")
        print(f"  - Максимумы (-1): {zigzag_stats.get(-1, 0):,}")
        print(f"  - Минимумы (1): {zigzag_stats.get(1, 0):,}")
        
        # Статистика цены
        print(f"\nСтатистика цены:")
        print(f"  - Минимальная цена: ${self.data['Low'].min():,.2f}")
        print(f"  - Максимальная цена: ${self.data['High'].max():,.2f}")
        print(f"  - Средняя цена: ${self.data['Close'].mean():,.2f}")
        
        # Статистика объема
        print(f"\nСтатистика объема:")
        print(f"  - Минимальный объем: {self.data['Volume'].min():,.0f}")
        print(f"  - Максимальный объем: {self.data['Volume'].max():,.0f}")
        print(f"  - Средний объем: {self.data['Volume'].mean():,.0f}")
        
        # Период данных
        print(f"\nПериод данных:")
        print(f"  - Начало: {self.data.index[0]}")
        print(f"  - Конец: {self.data.index[-1]}")
        print(f"  - Всего записей: {len(self.data):,}")
        
        print("="*60)

def main():
    """
    Основная функция для обработки 15-минутных данных.
    """
    print("Обработка 15-минутных данных BTC с зигзагом")
    print("="*80)
    
    try:
        # Запрашиваем отклонение зигзага
        while True:
            try:
                deviation_input = input("Введите отклонение зигзага в процентах (по умолчанию 1.0): ").strip()
                if deviation_input == "":
                    deviation = 1.0
                    break
                else:
                    deviation = float(deviation_input)
                    if deviation > 0:
                        break
                    else:
                        print("❌ Отклонение должно быть положительным числом!")
            except ValueError:
                print("❌ Введите корректное число!")
        
        print(f"✓ Используется отклонение: {deviation}%")
        
        # Создаем процессор
        processor = ZigZag15MProcessor(
            data_file="processed_data/input_data.csv",
            deviation=deviation
        )
        
        # Загружаем данные
        if not processor.load_data():
            return
        
        # Вычисляем зигзаг
        if not processor.calculate_zigzag():
            return
        
        # Создаем технические индикаторы
        if not processor.create_technical_features():
            return
        
        # Выводим статистику
        processor.get_statistics()
        
        # Сохраняем данные с признаками
        processor.save_enhanced_data("processed_data/ml_data.csv")
        
        print("\n" + "="*80)
        print("✓ Обработка данных завершена успешно!")
        print("✓ Сохранены данные: processed_data/ml_data.csv")
        print("\n💡 Для создания графиков по периодам запустите: python create_period_charts.py")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 