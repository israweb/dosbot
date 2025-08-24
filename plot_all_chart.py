#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

class UniversalParameterPlotter:
    """
    Универсальный плоттер для построения графиков всех параметров по периодам.
    """
    
    def __init__(self, data_file="processed_data/ml_data.csv"):
        """
        Инициализация плоттера.
        
        Параметры:
        - data_file: путь к файлу с данными
        """
        self.data_file = data_file
        self.data = None
        self.zigzag_column = None
        self.charts_base_dir = "charts"
        self.selected_parameters = []
        self.selected_periods = []
        self.all_periods = []
        
    def load_data(self):
        """
        Загружает данные и находит колонку зигзага.
        """
        print("Загрузка данных...")
        print("=" * 60)
        
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Файл {self.data_file} не найден!")
        
        # Загружаем данные
        self.data = pd.read_csv(self.data_file)
        
        # Проверяем наличие необходимых колонок
        if 'Open time' not in self.data.columns:
            raise ValueError("Колонка 'Open time' не найдена!")
        
        # Ищем колонку зигзага
        zigzag_columns = [col for col in self.data.columns if 'zigzag' in col.lower()]
        if zigzag_columns:
            self.zigzag_column = zigzag_columns[0]
            print(f"✓ Найдена колонка зигзага: {self.zigzag_column}")
        else:
            raise ValueError("Колонка зигзага не найдена!")
        
        # Преобразуем время в datetime
        self.data['datetime'] = pd.to_datetime(self.data['Open time'])
        
        print(f"✓ Загружены данные: {len(self.data)} записей")
        print(f"✓ Период: {self.data['datetime'].min()} - {self.data['datetime'].max()}")
        
        return True
    
    def get_available_parameters(self):
        """
        Возвращает список доступных параметров для построения графиков.
        """
        if self.data is None:
            return []
        
        # Исключаем базовые колонки (но не зигзаг - его будем строить отдельно)
        exclude_columns = [
            'Open time', 'datetime', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades', 
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ]
        
        # Группируем параметры по категориям
        parameters = {}
        
        # Добавляем специальную категорию для зигзага
        parameters['ZigZag + Цена'] = ['ZIGZAG_PRICE_CHART']
        
        for col in self.data.columns:
            if col not in exclude_columns:
                # Определяем категорию
                if 'zigzag' in col.lower():
                    category = 'ZigZag (только точки)'
                elif 'sma' in col.lower():
                    category = 'Скользящие средние (SMA)'
                elif 'ema' in col.lower():
                    category = 'Экспоненциальные средние (EMA)'
                elif 'rsi' in col.lower():
                    category = 'RSI'
                elif 'volatility' in col.lower():
                    category = 'Волатильность'
                elif 'deviation' in col.lower():
                    category = 'Отклонения от средних'
                elif 'position' in col.lower():
                    category = 'Позиция в окне'
                elif 'trend' in col.lower():
                    category = 'Трендовые индикаторы'
                elif 'momentum' in col.lower():
                    category = 'Моментум'
                elif 'volume' in col.lower():
                    category = 'Объемные индикаторы'
                elif 'bb_' in col.lower():
                    category = 'Bollinger Bands'
                elif 'stoch' in col.lower():
                    category = 'Stochastic'
                elif 'macd' in col.lower():
                    category = 'MACD'
                elif any(word in col.lower() for word in ['ratio', 'change', 'body']):
                    category = 'Базовые признаки'
                else:
                    category = 'Прочие индикаторы'
                
                if category not in parameters:
                    parameters[category] = []
                parameters[category].append(col)
        
        return parameters
    
    def select_parameters(self):
        """
        Интерактивный выбор параметров для построения графиков.
        """
        parameters = self.get_available_parameters()
        
        print(f"\n" + "=" * 60)
        print("ВЫБОР ПАРАМЕТРОВ ДЛЯ ПОСТРОЕНИЯ ГРАФИКОВ")
        print("=" * 60)
        
        print("Доступные категории параметров:")
        categories = list(parameters.keys())
        for i, category in enumerate(categories, 1):
            print(f"  {i:2d}. {category} ({len(parameters[category])} параметров)")
        
        while True:
            try:
                choice = input(f"\nВыберите категории (1-{len(categories)}, через запятую, или 'all' для всех): ").strip()
                
                if choice.lower() == 'all':
                    selected_categories = categories
                    break
                else:
                    selected_indices = [int(x.strip()) for x in choice.split(',')]
                    if all(1 <= i <= len(categories) for i in selected_indices):
                        selected_categories = [categories[i-1] for i in selected_indices]
                        break
                    else:
                        print(f"❌ Некорректный выбор! Используйте числа от 1 до {len(categories)}")
            except ValueError:
                print("❌ Введите корректные числа через запятую!")
        
        print(f"\n✓ Выбранные категории:")
        for category in selected_categories:
            print(f"  - {category}")
        
        # Собираем все параметры из выбранных категорий
        self.selected_parameters = []
        for category in selected_categories:
            self.selected_parameters.extend(parameters[category])
        
        print(f"\n✓ Всего выбрано параметров: {len(self.selected_parameters)}")
        
        # Спрашиваем, показать ли подробный список
        show_details = input("Показать подробный список параметров? (y/n): ").strip().lower()
        if show_details == 'y':
            for i, param in enumerate(self.selected_parameters, 1):
                print(f"  {i:2d}. {param}")
        
        return True
    
    def get_time_periods(self, months=3):
        """
        Разбивает данные на периоды по 3 месяца.
        """
        if self.data is None:
            return []
        
        periods = []
        start_date = self.data['datetime'].min()
        end_date = self.data['datetime'].max()
        
        current_start = start_date
        period_num = 1
        
        while current_start < end_date:
            # Вычисляем конец периода
            current_end = current_start + timedelta(days=months*30)  # Примерно 3 месяца
            
            # Если это последний период, используем реальный конец данных
            if current_end > end_date:
                current_end = end_date
            
            # Фильтруем данные для текущего периода
            period_mask = (self.data['datetime'] >= current_start) & (self.data['datetime'] < current_end)
            period_data = self.data[period_mask]
            
            if len(period_data) > 0:
                period_info = {
                    'period_num': period_num,
                    'start_date': current_start,
                    'end_date': current_end,
                    'start_str': current_start.strftime('%Y-%m'),
                    'end_str': current_end.strftime('%Y-%m'),
                    'data_count': len(period_data)
                }
                periods.append(period_info)
                period_num += 1
            
            current_start = current_end
        
        return periods
    
    def select_periods(self):
        """
        Интерактивный выбор периодов для построения графиков.
        """
        self.all_periods = self.get_time_periods(months=3)
        
        print(f"\n" + "=" * 60)
        print("ВЫБОР ПЕРИОДОВ ДЛЯ ПОСТРОЕНИЯ ГРАФИКОВ")
        print("=" * 60)
        
        print(f"Доступные периоды (всего {len(self.all_periods)}):")
        for i, period in enumerate(self.all_periods, 1):
            print(f"  {i:2d}. {period['start_str']} - {period['end_str']} ({period['data_count']:,} записей)")
        
        while True:
            try:
                choice = input(f"\nВыберите периоды (1-{len(self.all_periods)}, через запятую, или 'all' для всех): ").strip()
                
                if choice.lower() == 'all':
                    self.selected_periods = self.all_periods
                    break
                else:
                    selected_indices = [int(x.strip()) for x in choice.split(',')]
                    if all(1 <= i <= len(self.all_periods) for i in selected_indices):
                        self.selected_periods = [self.all_periods[i-1] for i in selected_indices]
                        break
                    else:
                        print(f"❌ Некорректный выбор! Используйте числа от 1 до {len(self.all_periods)}")
            except ValueError:
                print("❌ Введите корректные числа через запятую!")
        
        print(f"\n✓ Выбрано периодов: {len(self.selected_periods)}")
        for period in self.selected_periods:
            print(f"  - {period['start_str']} - {period['end_str']}")
        
        return True
    
    def create_parameter_directories(self):
        """
        Создает папки для каждого выбранного параметра.
        """
        print(f"\nСоздание папок для параметров...")
        
        created_dirs = []
        for param in self.selected_parameters:
            # Очищаем название от специальных символов
            safe_param_name = param.replace('/', '_').replace('\\', '_').replace(':', '_')
            param_dir = os.path.join(self.charts_base_dir, safe_param_name)
            
            if not os.path.exists(param_dir):
                os.makedirs(param_dir)
                created_dirs.append(param_dir)
        
        print(f"✓ Создано папок: {len(created_dirs)}")
        return True
    
    def plot_parameter_for_period(self, parameter, period_info):
        """
        Создает график параметра для конкретного периода.
        """
        # Проверяем, это специальный график зигзага с ценой
        if parameter == 'ZIGZAG_PRICE_CHART':
            return self.plot_zigzag_price_chart(period_info)
        
        # Фильтруем данные для периода
        period_mask = (self.data['datetime'] >= period_info['start_date']) & (self.data['datetime'] < period_info['end_date'])
        period_data = self.data[period_mask].copy()
        
        if len(period_data) == 0:
            print(f"⚠️ Нет данных для периода {period_info['start_str']}-{period_info['end_str']}")
            return False
        
        # Находим точки зигзага
        zigzag_max = period_data[period_data[self.zigzag_column] == -1]  # Максимумы
        zigzag_min = period_data[period_data[self.zigzag_column] == 1]   # Минимумы
        
        # Создаем график
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        
        # График параметра
        ax.plot(period_data['datetime'], period_data[parameter], 
                color='blue', alpha=0.7, linewidth=1, label=parameter)
        
        # Отмечаем точки зигзага на графике параметра
        if len(zigzag_max) > 0:
            # Красные точки для максимумов
            ax.scatter(zigzag_max['datetime'], zigzag_max[parameter], 
                      color='red', marker='o', s=30, alpha=0.8, 
                      label=f'Максимумы ZigZag ({len(zigzag_max)})', zorder=5)
        
        if len(zigzag_min) > 0:
            # Зеленые точки для минимумов
            ax.scatter(zigzag_min['datetime'], zigzag_min[parameter], 
                      color='green', marker='o', s=30, alpha=0.8, 
                      label=f'Минимумы ZigZag ({len(zigzag_min)})', zorder=5)
        
        # Настройки графика
        ax.set_title(f'{parameter} ({period_info["start_str"]} - {period_info["end_str"]})', 
                     fontsize=16, fontweight='bold')
        ax.set_ylabel(parameter, fontsize=12)
        ax.set_xlabel('Время', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Форматирование оси времени
        self._format_time_axis(ax, period_data)
        
        plt.tight_layout()
        
        # Сохраняем график
        safe_param_name = parameter.replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f"{safe_param_name}_{period_info['start_str']}.png"
        save_path = os.path.join(self.charts_base_dir, safe_param_name, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Закрываем график для экономии памяти
        
        return True
    
    def plot_zigzag_price_chart(self, period_info):
        """
        Создает специальный график зигзага с ценой и линиями зигзага.
        """
        # Фильтруем данные для периода
        period_mask = (self.data['datetime'] >= period_info['start_date']) & (self.data['datetime'] < period_info['end_date'])
        period_data = self.data[period_mask].copy()
        
        if len(period_data) == 0:
            print(f"⚠️ Нет данных для периода {period_info['start_str']}-{period_info['end_str']}")
            return False
        
        # Находим точки зигзага
        zigzag_max = period_data[period_data[self.zigzag_column] == -1]  # Максимумы
        zigzag_min = period_data[period_data[self.zigzag_column] == 1]   # Минимумы
        zigzag_points = period_data[period_data[self.zigzag_column] != 0]  # Все точки
        
        # Создаем график
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        
        # График цены закрытия
        ax.plot(period_data['datetime'], period_data['Close'], 
                color='blue', alpha=0.7, linewidth=1, label='Цена закрытия')
        
        # Соединяем точки зигзага линиями
        if len(zigzag_points) > 1:
            zigzag_prices = []
            zigzag_times = []
            for _, row in zigzag_points.iterrows():
                if row[self.zigzag_column] == -1:  # Максимум
                    zigzag_prices.append(row['High'])
                else:  # Минимум
                    zigzag_prices.append(row['Low'])
                zigzag_times.append(row['datetime'])
            
            ax.plot(zigzag_times, zigzag_prices, 
                    color='orange', linewidth=2, alpha=0.9, label='Линии ZigZag')
        
        # Отмечаем точки зигзага
        if len(zigzag_max) > 0:
            # Красные точки для максимумов
            ax.scatter(zigzag_max['datetime'], zigzag_max['High'], 
                      color='red', marker='o', s=50, alpha=0.9, 
                      label=f'Максимумы ZigZag ({len(zigzag_max)})', zorder=5)
        
        if len(zigzag_min) > 0:
            # Зеленые точки для минимумов
            ax.scatter(zigzag_min['datetime'], zigzag_min['Low'], 
                      color='green', marker='o', s=50, alpha=0.9, 
                      label=f'Минимумы ZigZag ({len(zigzag_min)})', zorder=5)
        
        # Настройки графика
        ax.set_title(f'ZigZag + Цена BTC/USDT ({period_info["start_str"]} - {period_info["end_str"]})', 
                     fontsize=16, fontweight='bold')
        ax.set_ylabel('Цена (USDT)', fontsize=12)
        ax.set_xlabel('Время', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Форматирование оси времени
        self._format_time_axis(ax, period_data)
        
        plt.tight_layout()
        
        # Сохраняем график
        filename = f"ZigZag_Price_{period_info['start_str']}.png"
        save_path = os.path.join(self.charts_base_dir, "ZIGZAG_PRICE_CHART", filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Закрываем график для экономии памяти
        
        return True
    
    def _format_time_axis(self, ax, period_data):
        """
        Форматирует ось времени - только 1, 10, 20 числа месяцев.
        """
        start_date = period_data['datetime'].min()
        end_date = period_data['datetime'].max()
        
        # Генерируем даты для отметок: 1, 10, 20 число каждого месяца
        tick_dates = []
        current_date = start_date.replace(day=1)  # Начинаем с 1 числа месяца
        
        while current_date <= end_date:
            # Добавляем 1, 10, 20 число текущего месяца
            for day in [1, 10, 20]:
                try:
                    tick_date = current_date.replace(day=day)
                    if start_date <= tick_date <= end_date:
                        tick_dates.append(tick_date)
                except ValueError:
                    # Если день не существует в месяце (например, 30 февраля)
                    pass
            
            # Переходим к следующему месяцу
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Устанавливаем кастомные тики
        ax.set_xticks(tick_dates)
        ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in tick_dates], 
                          rotation=45, ha='right', fontsize=10)
    
    def create_all_charts(self):
        """
        Создает все выбранные графики для всех выбранных периодов.
        """
        print(f"\n" + "=" * 60)
        print("СОЗДАНИЕ ГРАФИКОВ")
        print("=" * 60)
        
        total_charts = len(self.selected_parameters) * len(self.selected_periods)
        created_charts = 0
        
        print(f"Всего будет создано графиков: {total_charts}")
        print(f"Параметров: {len(self.selected_parameters)}")
        print(f"Периодов: {len(self.selected_periods)}")
        
        # Создаем папки
        self.create_parameter_directories()
        
        print(f"\nНачинаем создание графиков...")
        
        for i, parameter in enumerate(self.selected_parameters, 1):
            print(f"\n[{i}/{len(self.selected_parameters)}] Обработка параметра: {parameter}")
            
            for j, period in enumerate(self.selected_periods, 1):
                try:
                    success = self.plot_parameter_for_period(parameter, period)
                    if success:
                        created_charts += 1
                        print(f"  ✓ {period['start_str']}-{period['end_str']} ({j}/{len(self.selected_periods)})")
                    else:
                        print(f"  ❌ {period['start_str']}-{period['end_str']} - ошибка создания")
                except Exception as e:
                    print(f"  ❌ {period['start_str']}-{period['end_str']} - ошибка: {e}")
        
        print(f"\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ СОЗДАНИЯ ГРАФИКОВ")
        print("=" * 60)
        print(f"✓ Успешно создано графиков: {created_charts}/{total_charts}")
        
        if created_charts < total_charts:
            print(f"⚠️ Не удалось создать: {total_charts - created_charts} графиков")
        
        print(f"✓ Графики сохранены в папке: {self.charts_base_dir}")
        
        return created_charts > 0

def main():
    """
    Основная функция для создания графиков параметров.
    """
    print("Универсальный плоттер параметров с точками ZigZag")
    print("=" * 80)
    
    try:
        # Создаем плоттер
        plotter = UniversalParameterPlotter("processed_data/ml_data.csv")
        
        # Загружаем данные
        plotter.load_data()
        
        # Выбираем параметры
        plotter.select_parameters()
        
        # Выбираем периоды
        plotter.select_periods()
        
        # Создаем все графики
        plotter.create_all_charts()
        
        print("\n" + "=" * 80)
        print("✓ Процесс завершен успешно!")
        print("✓ Все графики созданы и сохранены в соответствующие папки")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()