#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def analyze_zigzag_period():
    """
    Анализирует зигзаги в периоде 2018-01 для выявления проблемы.
    """
    # Загружаем данные
    data = pd.read_csv('processed_data/ml_data.csv')
    data['datetime'] = pd.to_datetime(data['Open time'])
    
    # Фильтруем данные для периода 2018-01 - 2018-04
    start_date = pd.to_datetime('2018-01-01')
    end_date = pd.to_datetime('2018-04-01')
    period_mask = (data['datetime'] >= start_date) & (data['datetime'] < end_date)
    period_data = data[period_mask].copy()
    
    print(f'=== АНАЛИЗ ПЕРИОДА 2018-01 - 2018-04 ===')
    print(f'Всего записей в периоде: {len(period_data)}')
    
    # Ищем колонку зигзага
    zigzag_columns = [col for col in data.columns if 'zigzag' in col.lower()]
    if zigzag_columns:
        zigzag_col = zigzag_columns[0]
        print(f'Колонка зигзага: {zigzag_col}')
    else:
        print('❌ Колонка зигзага не найдена!')
        return
    
    # Находим точки зигзага
    zigzag_points = period_data[period_data[zigzag_col] != 0]
    print(f'Точек зигзага в периоде: {len(zigzag_points)}')
    print(f'Максимумов (-1): {len(period_data[period_data[zigzag_col] == -1])}')
    print(f'Минимумов (1): {len(period_data[period_data[zigzag_col] == 1])}')
    
    print(f'\n=== ПЕРВЫЕ 15 ТОЧЕК ЗИГЗАГА ===')
    for i, (idx, row) in enumerate(zigzag_points.head(15).iterrows()):
        direction = 'MAX' if row[zigzag_col] == -1 else 'MIN'
        price = row['High'] if row[zigzag_col] == -1 else row['Low']
        print(f'{i+1:2d}. {direction} {row["datetime"].strftime("%Y-%m-%d %H:%M")} Цена: {price:.2f}')
    
    print(f'\n=== ПРОВЕРКА РАССТОЯНИЙ МЕЖДУ СОСЕДНИМИ ТОЧКАМИ ===')
    distances = []
    for i in range(1, min(11, len(zigzag_points))):
        prev_row = zigzag_points.iloc[i-1]
        curr_row = zigzag_points.iloc[i]
        
        prev_price = prev_row['High'] if prev_row[zigzag_col] == -1 else prev_row['Low']
        curr_price = curr_row['High'] if curr_row[zigzag_col] == -1 else curr_row['Low']
        
        change_pct = abs((curr_price - prev_price) / prev_price * 100)
        distances.append(change_pct)
        
        direction_prev = 'MAX' if prev_row[zigzag_col] == -1 else 'MIN'
        direction_curr = 'MAX' if curr_row[zigzag_col] == -1 else 'MIN'
        
        print(f'{i:2d}. {direction_prev}({prev_price:.2f}) -> {direction_curr}({curr_price:.2f}) = {change_pct:.3f}%')
        
        if change_pct < 5.0:
            print(f'    ❌ НАРУШЕНИЕ! Расстояние {change_pct:.3f}% < 5.0%')
    
    if distances:
        print(f'\n=== СТАТИСТИКА РАССТОЯНИЙ ===')
        print(f'Минимальное расстояние: {min(distances):.3f}%')
        print(f'Максимальное расстояние: {max(distances):.3f}%')
        print(f'Среднее расстояние: {np.mean(distances):.3f}%')
        print(f'Нарушений (< 5%): {sum(1 for d in distances if d < 5.0)}')
    
    # Сравним с другими периодами
    print(f'\n=== СРАВНЕНИЕ С ДРУГИМИ ПЕРИОДАМИ ===')
    
    # Период 2020-03 - 2020-06 (должен быть нормальным)
    start_date2 = pd.to_datetime('2020-03-01')
    end_date2 = pd.to_datetime('2020-06-01')
    period_mask2 = (data['datetime'] >= start_date2) & (data['datetime'] < end_date2)
    period_data2 = data[period_mask2].copy()
    zigzag_points2 = period_data2[period_data2[zigzag_col] != 0]
    
    print(f'Период 2020-03 - 2020-06: {len(zigzag_points2)} точек зигзага')
    
    # Период 2021-06 - 2021-09
    start_date3 = pd.to_datetime('2021-06-01')
    end_date3 = pd.to_datetime('2021-09-01')
    period_mask3 = (data['datetime'] >= start_date3) & (data['datetime'] < end_date3)
    period_data3 = data[period_mask3].copy()
    zigzag_points3 = period_data3[period_data3[zigzag_col] != 0]
    
    print(f'Период 2021-06 - 2021-09: {len(zigzag_points3)} точек зигзага')
    
    # Анализируем данные в начале файла
    print(f'\n=== АНАЛИЗ НАЧАЛА ДАННЫХ ===')
    first_100 = data.head(100)
    first_zigzag = first_100[first_100[zigzag_col] != 0]
    print(f'Первые 100 записей содержат {len(first_zigzag)} точек зигзага')
    
    if len(first_zigzag) > 0:
        print(f'Первые точки зигзага:')
        for i, (idx, row) in enumerate(first_zigzag.head(5).iterrows()):
            direction = 'MAX' if row[zigzag_col] == -1 else 'MIN'
            price = row['High'] if row[zigzag_col] == -1 else row['Low']
            print(f'  {i+1}. Индекс {idx}: {direction} {row["datetime"]} Цена: {price:.2f}')

if __name__ == "__main__":
    analyze_zigzag_period()