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

class ZigZagPeriodPlotter:
    """
    Класс для создания периодных графиков зигзага с отчетами.
    """
    
    def __init__(self, data_file="processed_data/ml_data.csv"):
        """
        Инициализация плоттера.
        
        Параметры:
        - data_file: путь к файлу с данными для ML
        """
        self.data_file = data_file
        self.data = None
        self.zigzag_column = None
        self.charts_dir = "charts/zigzag"
        self.report_data = []
        
    def load_data(self):
        """
        Загружает данные из файла.
        """
        print(f"Загрузка данных из {self.data_file}...")
        
        try:
            self.data = pd.read_csv(self.data_file)
            
                    # Проверяем наличие необходимых колонок
        if 'Open time' not in self.data.columns:
            print("❌ Колонка 'Open time' не найдена!")
            return False
            
        # Ищем колонку зигзага
        zigzag_columns = [col for col in self.data.columns if 'zigzag' in col.lower()]
        if zigzag_columns:
            self.zigzag_column = zigzag_columns[0]
            print(f"✓ Найдена колонка зигзага: {self.zigzag_column}")
        else:
            print("❌ Колонка зигзага не найдена!")
            return False
            
            # Преобразуем время в datetime
            self.data['datetime'] = pd.to_datetime(self.data['Open time'])
            
            # Создаем папку для графиков
            if not os.path.exists(self.charts_dir):
                os.makedirs(self.charts_dir)
                print(f"📁 Создана папка: {self.charts_dir}")
            
            print(f"✓ Загружены данные: {len(self.data)} записей")
            print(f"✓ Период: {self.data['datetime'].min()} - {self.data['datetime'].max()}")
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Файл {self.data_file} не найден!")
            print("💡 Сначала запустите: python data_for_ml_maker.py")
            return False
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            return False
    
    def split_data_into_periods(self, months=3):
        """
        Разбивает данные на периоды по 3 месяца.
        
        Параметры:
        - months: количество месяцев в периоде (по умолчанию 3)
        
        Возвращает:
        - список периодов с данными
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
            period_data = self.data[period_mask].copy()
            
            if len(period_data) > 0:
                period_info = {
                    'period_num': period_num,
                    'start_date': current_start,
                    'end_date': current_end,
                    'data': period_data
                }
                periods.append(period_info)
                period_num += 1
            
            current_start = current_end
        
        print(f"✓ Данные разбиты на {len(periods)} периодов по {months} месяца")
        return periods
    
    def analyze_zigzag_period(self, period_data):
        """
        Анализирует зигзаги в периоде.
        
        Параметры:
        - period_data: данные периода
        
        Возвращает:
        - словарь с анализом зигзагов
        """
        # Находим точки зигзага
        zigzag_points = period_data[period_data[self.zigzag_column] != 0]
        
        if len(zigzag_points) == 0:
            return {
                'zigzag_count': 0,
                'avg_distance': 0,
                'min_distance': 0,
                'max_distance': 0
            }
        
        # Вычисляем расстояния между точками зигзага
        distances = []
        for i in range(1, len(zigzag_points)):
            prev_price = zigzag_points.iloc[i-1]['Close']
            curr_price = zigzag_points.iloc[i]['Close']
            distance = abs(curr_price - prev_price)
            distances.append(distance)
        
        if distances:
            avg_distance = np.mean(distances)
            min_distance = np.min(distances)
            max_distance = np.max(distances)
        else:
            avg_distance = min_distance = max_distance = 0
        
        return {
            'zigzag_count': len(zigzag_points),
            'avg_distance': avg_distance,
            'min_distance': min_distance,
            'max_distance': max_distance
        }
    
    def plot_period_chart(self, period_data, period_info, save_path):
        """
        Создает график для периода.
        
        Параметры:
        - period_data: данные периода
        - period_info: информация о периоде
        - save_path: путь для сохранения
        """
        # Создаем график
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        
        # График цены
        ax.plot(period_data['datetime'], period_data['Close'], 
                color='blue', alpha=0.7, linewidth=1, label='Цена закрытия')
        
        # Соединяем точки зигзага линиями
        zigzag_data = period_data[period_data[self.zigzag_column] != 0]
        if len(zigzag_data) > 1:
            zigzag_prices = []
            for _, row in zigzag_data.iterrows():
                if row[self.zigzag_column] == -1:  # Максимум
                    zigzag_prices.append(row['High'])
                else:  # Минимум
                    zigzag_prices.append(row['Low'])
            
            ax.plot(zigzag_data['datetime'], zigzag_prices, 
                    color='orange', linewidth=2, alpha=0.8, label='Зигзаг')
        
        # Настройки графика
        start_str = period_info['start_date'].strftime('%Y-%m')
        end_str = period_info['end_date'].strftime('%Y-%m')
        ax.set_title(f'BTC/USDT - Цена и ZigZag ({start_str} - {end_str})', 
                     fontsize=16, fontweight='bold')
        ax.set_ylabel('Цена (USDT)', fontsize=12)
        ax.set_xlabel('Время', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Форматирование оси времени - только начало каждого месяца
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Сохраняем график
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Закрываем график для экономии памяти
        
        print(f"✓ График сохранен: {save_path}")
    
    def save_report(self, report_path="charts/zigzag/zigzag_analysis_report.txt"):
        """
        Сохраняет полный отчет в файл.
        
        Параметры:
        - report_path: путь для сохранения отчета
        """
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ ПО АНАЛИЗУ ЗИГЗАГОВ ПО ПЕРИОДАМ\n")
            f.write("=" * 60 + "\n")
            f.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего периодов: {len(self.report_data)}\n\n")
            
            # Заголовок таблицы
            f.write(f"{'Период':<15} {'Начало':<12} {'Конец':<12} {'Зигзагов':<10} {'Ср.расстояние':<15} {'Мин.расстояние':<15} {'Макс.расстояние':<15}\n")
            f.write("-" * 100 + "\n")
            
            total_zigzags = 0
            for report in self.report_data:
                f.write(f"{report['period']:<15} {report['start_date']:<12} {report['end_date']:<12} "
                       f"{report['zigzag_count']:<10} {report['avg_distance']:<15.2f} "
                       f"{report['min_distance']:<15.2f} {report['max_distance']:<15.2f}\n")
                total_zigzags += report['zigzag_count']
            
            f.write("-" * 100 + "\n")
            f.write(f"{'ИТОГО':<15} {'':<12} {'':<12} {total_zigzags:<10} {'':<15} {'':<15} {'':<15}\n\n")
            
            # Дополнительная статистика
            if self.report_data:
                avg_zigzags_per_period = total_zigzags / len(self.report_data)
                periods_with_zigzags = sum(1 for r in self.report_data if r['zigzag_count'] > 0)
                max_zigzags_in_period = max(r['zigzag_count'] for r in self.report_data)
                min_zigzags_in_period = min(r['zigzag_count'] for r in self.report_data)
                
                f.write("ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Общее количество зигзагов: {total_zigzags}\n")
                f.write(f"Среднее количество зигзагов на период: {avg_zigzags_per_period:.2f}\n")
                f.write(f"Периодов с зигзагами: {periods_with_zigzags} из {len(self.report_data)}\n")
                f.write(f"Максимум зигзагов в периоде: {max_zigzags_in_period}\n")
                f.write(f"Минимум зигзагов в периоде: {min_zigzags_in_period}\n")
        
        print(f"✓ Отчет сохранен: {report_path}")
    
    def create_period_charts(self):
        """
        Основной метод для создания периодных графиков и отчетов.
        """
        print("Создание периодных графиков зигзага")
        print("=" * 60)
        
        # Загружаем данные
        if not self.load_data():
            return
        
        # Разбиваем на периоды
        periods = self.split_data_into_periods(months=3)
        
        if not periods:
            print("❌ Не удалось разбить данные на периоды!")
            return
        
        total_zigzags = 0
        
        # Обрабатываем каждый период
        for period_info in periods:
            period_data = period_info['data']
            period_num = period_info['period_num']
            start_date = period_info['start_date']
            end_date = period_info['end_date']
            
            # Анализируем зигзаги в периоде
            analysis = self.analyze_zigzag_period(period_data)
            zigzag_count = analysis['zigzag_count']
            avg_distance = analysis['avg_distance']
            
            total_zigzags += zigzag_count
            
            # Выводим отчет в терминал
            start_str = start_date.strftime('%Y-%m')
            end_str = end_date.strftime('%Y-%m')
            print(f"Период {start_str}-{end_str}: {zigzag_count} зигзагов, среднее расстояние: {avg_distance:.2f}")
            
            # Сохраняем данные для отчета
            self.report_data.append({
                'period': f"Период {period_num}",
                'start_date': start_str,
                'end_date': end_str,
                'zigzag_count': zigzag_count,
                'avg_distance': avg_distance,
                'min_distance': analysis['min_distance'],
                'max_distance': analysis['max_distance']
            })
            
            # Создаем график для периода
            chart_filename = f"zigzag_{start_str}.png"
            chart_path = os.path.join(self.charts_dir, chart_filename)
            self.plot_period_chart(period_data, period_info, chart_path)
        
        # Выводим итоговую статистику
        print(f"\n" + "=" * 60)
        print("ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 60)
        print(f"Общее количество зигзагов: {total_zigzags}")
        print(f"Среднее количество зигзагов на период: {total_zigzags/len(periods):.2f}")
        print(f"Создано графиков: {len(periods)}")
        
        # Сохраняем полный отчет
        self.save_report()
        
        print(f"\n✓ Все графики сохранены в папку: {self.charts_dir}")
        print("✓ Полный отчет сохранен в файл: charts/zigzag/zigzag_analysis_report.txt")

def main():
    """
    Основная функция для создания периодных графиков.
    """
    try:
        # Создаем плоттер
        plotter = ZigZagPeriodPlotter("processed_data/ml_data.csv")
        
        # Создаем графики и отчеты
        plotter.create_period_charts()
        
        print("\n" + "=" * 60)
        print("✓ Процесс завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 