#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from datetime import datetime

class ZigZagAnalyzer:
    """
    Анализатор зигзагов для проверки расстояний между вершинами.
    """
    
    def __init__(self, data_file="processed_data/ml_data.csv"):
        """
        Инициализация анализатора.
        
        Параметры:
        - data_file: путь к файлу с данными и зигзагами
        """
        self.data_file = data_file
        self.data = None
        self.zigzag_column = None
        self.analysis_results = {}
        
    def load_data(self):
        """
        Загружает данные и находит колонку зигзага.
        """
        print("Загрузка данных для анализа зигзага...")
        print("=" * 60)
        
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Файл {self.data_file} не найден!")
        
        # Загружаем данные
        self.data = pd.read_csv(self.data_file)
        print(f"✓ Загружены данные: {len(self.data)} записей")
        
        # Ищем колонку зигзага
        zigzag_columns = [col for col in self.data.columns if 'zigzag' in col.lower()]
        if zigzag_columns:
            self.zigzag_column = zigzag_columns[0]
            print(f"✓ Найдена колонка зигзага: {self.zigzag_column}")
        else:
            raise ValueError("Колонка зигзага не найдена в файле!")
        
        # Проверяем наличие необходимых колонок
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Отсутствуют колонки: {missing_columns}")
        
        # Показываем статистику зигзага
        zigzag_stats = self.data[self.zigzag_column].value_counts()
        print(f"\nСтатистика зигзага:")
        print(f"  - Обычные бары (0): {zigzag_stats.get(0, 0):,}")
        print(f"  - Максимумы (-1): {zigzag_stats.get(-1, 0):,}")
        print(f"  - Минимумы (1): {zigzag_stats.get(1, 0):,}")
        
        return True
    
    def analyze_zigzag_distances(self):
        """
        Анализирует расстояния между вершинами зигзага.
        """
        print(f"\nАнализ расстояний между вершинами зигзага...")
        print("-" * 50)
        
        # Находим все точки зигзага
        zigzag_points = self.data[self.data[self.zigzag_column] != 0].copy()
        
        if len(zigzag_points) < 2:
            print("❌ Недостаточно точек зигзага для анализа (найдено < 2)")
            return False
        
        print(f"✓ Найдено {len(zigzag_points)} точек зигзага")
        
        # Списки для хранения расстояний
        price_distances = []
        percent_distances = []
        candle_distances = []
        
        # Анализируем каждую пару соседних точек
        for i in range(1, len(zigzag_points)):
            prev_point = zigzag_points.iloc[i-1]
            curr_point = zigzag_points.iloc[i]
            
            # Получаем цены (для максимумов - High, для минимумов - Low)
            if prev_point[self.zigzag_column] == -1:  # Максимум
                prev_price = prev_point['High']
            else:  # Минимум
                prev_price = prev_point['Low']
            
            if curr_point[self.zigzag_column] == -1:  # Максимум
                curr_price = curr_point['High']
            else:  # Минимум
                curr_price = curr_point['Low']
            
            # Вычисляем расстояния
            price_distance = abs(curr_price - prev_price)
            percent_distance = abs((curr_price - prev_price) / prev_price * 100)
            
            # Расстояние в свечах (индексах)
            prev_idx = zigzag_points.index[i-1]
            curr_idx = zigzag_points.index[i]
            candle_distance = curr_idx - prev_idx
            
            # Сохраняем результаты
            price_distances.append(price_distance)
            percent_distances.append(percent_distance)
            candle_distances.append(candle_distance)
            
            # Выводим детали для первых 5 пар
            if i <= 5:
                direction_prev = "MAX" if prev_point[self.zigzag_column] == -1 else "MIN"
                direction_curr = "MAX" if curr_point[self.zigzag_column] == -1 else "MIN"
                print(f"  {i:2d}. {direction_prev}({prev_idx}) -> {direction_curr}({curr_idx}): "
                      f"{percent_distance:.2f}%, ${price_distance:.2f}, {candle_distance} свечей")
        
        if len(zigzag_points) > 5:
            print(f"  ... и еще {len(zigzag_points) - 5} пар")
        
        # Сохраняем результаты анализа
        self.analysis_results = {
            'total_points': len(zigzag_points),
            'total_pairs': len(price_distances),
            'price_distances': price_distances,
            'percent_distances': percent_distances,
            'candle_distances': candle_distances
        }
        
        return True
    
    def calculate_statistics(self):
        """
        Вычисляет статистики расстояний.
        """
        if not self.analysis_results:
            print("❌ Сначала выполните анализ расстояний!")
            return False
        
        price_distances = self.analysis_results['price_distances']
        percent_distances = self.analysis_results['percent_distances']
        candle_distances = self.analysis_results['candle_distances']
        
        # Вычисляем статистики
        stats = {
            'Метрика': ['Процентное изменение (%)', 'Изменение цены ($)', 'Расстояние в свечах'],
            'Среднее': [
                np.mean(percent_distances),
                np.mean(price_distances),
                np.mean(candle_distances)
            ],
            'Минимальное': [
                np.min(percent_distances),
                np.min(price_distances),
                np.min(candle_distances)
            ],
            'Максимальное': [
                np.max(percent_distances),
                np.max(price_distances),
                np.max(candle_distances)
            ],
            'Медиана': [
                np.median(percent_distances),
                np.median(price_distances),
                np.median(candle_distances)
            ],
            'Стд. отклонение': [
                np.std(percent_distances),
                np.std(price_distances),
                np.std(candle_distances)
            ]
        }
        
        return stats
    
    def print_analysis_table(self):
        """
        Выводит таблицу с результатами анализа.
        """
        print(f"\n" + "=" * 80)
        print("АНАЛИЗ РАССТОЯНИЙ МЕЖДУ ВЕРШИНАМИ ЗИГЗАГА")
        print("=" * 80)
        
        stats = self.calculate_statistics()
        if not stats:
            return
        
        # Общая информация
        print(f"Файл данных: {self.data_file}")
        print(f"Колонка зигзага: {self.zigzag_column}")
        print(f"Всего записей: {len(self.data):,}")
        print(f"Точек зигзага: {self.analysis_results['total_points']:,}")
        print(f"Анализируемых пар: {self.analysis_results['total_pairs']:,}")
        
        print(f"\n" + "-" * 80)
        print("СТАТИСТИКА РАССТОЯНИЙ МЕЖДУ СОСЕДНИМИ ВЕРШИНАМИ")
        print("-" * 80)
        
        # Создаем красивую таблицу
        header = f"{'Метрика':<25} {'Среднее':<15} {'Минимальное':<15} {'Максимальное':<15} {'Медиана':<15} {'Стд.откл.':<15}"
        print(header)
        print("-" * len(header))
        
        for i, metric in enumerate(stats['Метрика']):
            if 'Процентное' in metric:
                row = f"{metric:<25} {stats['Среднее'][i]:<15.2f} {stats['Минимальное'][i]:<15.2f} {stats['Максимальное'][i]:<15.2f} {stats['Медиана'][i]:<15.2f} {stats['Стд. отклонение'][i]:<15.2f}"
            elif 'цены' in metric:
                row = f"{metric:<25} {stats['Среднее'][i]:<15.2f} {stats['Минимальное'][i]:<15.2f} {stats['Максимальное'][i]:<15.2f} {stats['Медиана'][i]:<15.2f} {stats['Стд. отклонение'][i]:<15.2f}"
            else:  # свечи
                row = f"{metric:<25} {stats['Среднее'][i]:<15.0f} {stats['Минимальное'][i]:<15.0f} {stats['Максимальное'][i]:<15.0f} {stats['Медиана'][i]:<15.0f} {stats['Стд. отклонение'][i]:<15.0f}"
            print(row)
        
        print("-" * len(header))
        
        # Дополнительная информация
        percent_distances = self.analysis_results['percent_distances']
        print(f"\nДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
        print(f"  - Самое маленькое изменение: {min(percent_distances):.3f}%")
        print(f"  - Самое большое изменение: {max(percent_distances):.3f}%")
        print(f"  - Количество изменений < 1%: {sum(1 for x in percent_distances if x < 1.0)}")
        print(f"  - Количество изменений < 0.5%: {sum(1 for x in percent_distances if x < 0.5)}")
        print(f"  - Количество изменений < 0.1%: {sum(1 for x in percent_distances if x < 0.1)}")
        
        return stats
    
    def save_detailed_report(self, output_file="zigzag_analysis_detailed.txt"):
        """
        Сохраняет подробный отчет в файл.
        """
        if not self.analysis_results:
            print("❌ Сначала выполните анализ!")
            return False
        
        print(f"\nСохранение подробного отчета в {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ПОДРОБНЫЙ АНАЛИЗ ЗИГЗАГОВ\n")
            f.write("=" * 50 + "\n")
            f.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Файл данных: {self.data_file}\n")
            f.write(f"Колонка зигзага: {self.zigzag_column}\n\n")
            
            # Общая статистика
            stats = self.calculate_statistics()
            f.write("ОБЩАЯ СТАТИСТИКА\n")
            f.write("-" * 30 + "\n")
            f.write(f"Всего записей: {len(self.data):,}\n")
            f.write(f"Точек зигзага: {self.analysis_results['total_points']:,}\n")
            f.write(f"Анализируемых пар: {self.analysis_results['total_pairs']:,}\n\n")
            
            # Таблица статистик
            f.write("СТАТИСТИКА РАССТОЯНИЙ\n")
            f.write("-" * 30 + "\n")
            for i, metric in enumerate(stats['Метрика']):
                f.write(f"{metric}:\n")
                f.write(f"  Среднее: {stats['Среднее'][i]:.4f}\n")
                f.write(f"  Минимальное: {stats['Минимальное'][i]:.4f}\n")
                f.write(f"  Максимальное: {stats['Максимальное'][i]:.4f}\n")
                f.write(f"  Медиана: {stats['Медиана'][i]:.4f}\n")
                f.write(f"  Стд. отклонение: {stats['Стд. отклонение'][i]:.4f}\n\n")
            
            # Детальный список всех расстояний
            f.write("ДЕТАЛЬНЫЙ СПИСОК ВСЕХ РАССТОЯНИЙ\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'№':<4} {'Тип1':<5} {'Тип2':<5} {'Процент%':<10} {'Цена$':<12} {'Свечи':<8}\n")
            f.write("-" * 50 + "\n")
            
            zigzag_points = self.data[self.data[self.zigzag_column] != 0]
            for i in range(1, len(zigzag_points)):
                prev_point = zigzag_points.iloc[i-1]
                curr_point = zigzag_points.iloc[i]
                
                type1 = "MAX" if prev_point[self.zigzag_column] == -1 else "MIN"
                type2 = "MAX" if curr_point[self.zigzag_column] == -1 else "MIN"
                
                percent_dist = self.analysis_results['percent_distances'][i-1]
                price_dist = self.analysis_results['price_distances'][i-1]
                candle_dist = self.analysis_results['candle_distances'][i-1]
                
                f.write(f"{i:<4} {type1:<5} {type2:<5} {percent_dist:<10.3f} {price_dist:<12.2f} {candle_dist:<8}\n")
        
        print(f"✓ Подробный отчет сохранен: {output_file}")
        return True
    
    def check_minimum_distances(self, min_percent=1.0):
        """
        Проверяет, есть ли расстояния меньше минимального.
        
        Параметры:
        - min_percent: минимальное ожидаемое расстояние в процентах
        """
        if not self.analysis_results:
            print("❌ Сначала выполните анализ!")
            return False
        
        percent_distances = self.analysis_results['percent_distances']
        violations = [d for d in percent_distances if d < min_percent]
        
        print(f"\n" + "=" * 60)
        print(f"ПРОВЕРКА МИНИМАЛЬНЫХ РАССТОЯНИЙ (>{min_percent}%)")
        print("=" * 60)
        
        if violations:
            print(f"❌ НАЙДЕНЫ НАРУШЕНИЯ: {len(violations)} расстояний меньше {min_percent}%")
            print(f"Нарушающие расстояния:")
            for i, violation in enumerate(violations[:10]):  # Показываем первые 10
                print(f"  {i+1:2d}. {violation:.3f}%")
            if len(violations) > 10:
                print(f"  ... и еще {len(violations) - 10} нарушений")
            
            print(f"\nСамое маленькое расстояние: {min(violations):.3f}%")
            print(f"Процент нарушений: {len(violations)/len(percent_distances)*100:.1f}%")
        else:
            print(f"✓ ВСЕ РАССТОЯНИЯ БОЛЬШЕ {min_percent}%")
            print(f"Минимальное расстояние: {min(percent_distances):.3f}%")
        
        return len(violations) == 0

def main():
    """
    Основная функция для анализа зигзагов.
    """
    print("Анализатор расстояний между вершинами зигзага")
    print("=" * 80)
    
    try:
        # Запрашиваем файл данных
        while True:
            file_input = input("Введите путь к файлу с данными (по умолчанию processed_data/ml_data.csv): ").strip()
            if file_input == "":
                data_file = "processed_data/ml_data.csv"
                break
            elif os.path.exists(file_input):
                data_file = file_input
                break
            else:
                print(f"❌ Файл {file_input} не найден! Попробуйте еще раз.")
        
        # Создаем анализатор
        analyzer = ZigZagAnalyzer(data_file)
        
        # Загружаем данные
        analyzer.load_data()
        
        # Анализируем расстояния
        if not analyzer.analyze_zigzag_distances():
            return
        
        # Выводим таблицу результатов
        analyzer.print_analysis_table()
        
        # Проверяем минимальные расстояния
        # Извлекаем процент из названия колонки
        import re
        match = re.search(r'(\d+\.?\d*)', analyzer.zigzag_column)
        if match:
            expected_min_percent = float(match.group(1))
            analyzer.check_minimum_distances(expected_min_percent)
        else:
            analyzer.check_minimum_distances(1.0)  # По умолчанию 1%
        
        # Сохраняем подробный отчет
        analyzer.save_detailed_report()
        
        print("\n" + "=" * 80)
        print("✓ Анализ завершен успешно!")
        print("✓ Подробный отчет сохранен в файл: zigzag_analysis_detailed.txt")
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()