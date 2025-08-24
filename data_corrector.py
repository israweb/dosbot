#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
import time
import os
warnings.filterwarnings('ignore')

def quick_data_check():
    """
    Быстрая проверка целостности исходных данных с выбором файла.
    """
    # Показываем доступные файлы в папке data
    data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    
    if not data_files:
        print("❌ В папке data не найдены CSV файлы!")
        return None, None
    
    print("Доступные файлы для проверки:")
    for i, file in enumerate(data_files, 1):
        print(f"  {i}. {file}")
    
    while True:
        try:
            choice = input(f"\nВыберите файл (1-{len(data_files)}): ").strip()
            file_index = int(choice) - 1
            
            if 0 <= file_index < len(data_files):
                file_path = f"data/{data_files[file_index]}"
                print(f"✓ Выбран файл: {file_path}")
                break
            else:
                print("❌ Неверный номер файла!")
        except ValueError:
            print("❌ Введите число!")
        except KeyboardInterrupt:
            print("\n❌ Операция отменена пользователем")
            return None, None
    chunk_size = 10000
    
    print("="*60)
    print("БЫСТРАЯ ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ")
    print("="*60)
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return None, None
    
    print(f"Файл: {file_path}")
    print(f"Размер части: {chunk_size:,} записей")
    print(f"Режим: Только проверка (без исправления)")
    
    # Инициализируем статистику
    total_records = 0
    total_missing = 0
    total_duplicates = 0
    total_invalid = 0
    column_names = []
    start_time = None
    end_time = None
    interval_minutes = None
    chunk_stats = []
    
    print(f"\nНачинаем анализ данных...")
    start_analysis = time.time()
    
    # Обрабатываем файл по частям
    chunk_num = 1
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        print(f"Обработка части {chunk_num} ({len(chunk):,} записей)...")
        
        # Сохраняем названия столбцов из первой части
        if chunk_num == 1:
            column_names = list(chunk.columns)
            print(f"✓ Найдено {len(column_names)} столбцов")
            print(f"✓ Столбцы: {', '.join(column_names)}")
        
        # Определяем интервал по времени (только для первой части)
        if chunk_num == 1:
            chunk['Open time'] = pd.to_datetime(chunk['Open time'])
            time_diff = chunk['Open time'].diff().dropna()
            if len(time_diff) > 0:
                interval_minutes = int(time_diff.mode().iloc[0].total_seconds() / 60)
        
        # Конвертируем время
        chunk['Open time'] = pd.to_datetime(chunk['Open time'])
        
        # Удаляем строки с NaT значениями
        chunk = chunk.dropna(subset=['Open time'])
        
        if len(chunk) == 0:
            print(f"  ⚠️ Часть {chunk_num} содержит только невалидные даты, пропускаем")
            chunk_num += 1
            continue
        
        chunk = chunk.sort_values('Open time').reset_index(drop=True)
        
        # Базовая информация
        chunk_start_time = chunk['Open time'].iloc[0]
        chunk_end_time = chunk['Open time'].iloc[-1]
        actual_records = len(chunk)
        
        # Проверяем пропуски
        missing = check_missing_in_chunk(chunk, chunk_start_time, chunk_end_time, interval_minutes)
        
        # Проверяем дубликаты
        duplicates = chunk.duplicated(subset=['Open time'], keep=False).sum()
        
        # Проверяем валидность
        invalid = check_validity_in_chunk(chunk)
        
        # Обновляем общую статистику
        total_records += actual_records
        total_missing += missing
        total_duplicates += duplicates
        total_invalid += invalid
        
        # Определяем временные границы
        if chunk_num == 1:
            start_time = chunk_start_time
        end_time = chunk_end_time
        
        chunk_stats.append({
            'chunk_num': chunk_num,
            'start_time': chunk_start_time,
            'end_time': chunk_end_time,
            'records': actual_records,
            'missing': missing,
            'duplicates': duplicates,
            'invalid': invalid
        })
        
        print(f"  ✓ Часть {chunk_num} проанализирована")
        print(f"  ✓ Пропусков: {missing:,}")
        print(f"  ✓ Дубликатов: {duplicates:,}")
        print(f"  ✓ Невалидных: {invalid:,}")
        
        chunk_num += 1
    
    # Вычисляем финальную статистику
    if start_time and end_time:
        total_days = (end_time - start_time).days
        if interval_minutes:
            expected_minutes = total_days * 24 * 60
            expected_records = expected_minutes // interval_minutes
        else:
            expected_records = total_records
        
        completeness = (total_records / expected_records) * 100 if expected_records > 0 else 100
    else:
        expected_records = total_records
        completeness = 100
    
    elapsed_time = time.time() - start_analysis
    
    # Выводим финальный отчет
    print(f"\n" + "="*60)
    print("ФИНАЛЬНЫЙ ОТЧЕТ")
    print("="*60)
    
    print(f"Период данных:")
    print(f"  - Начало: {start_time}")
    print(f"  - Конец: {end_time}")
    print(f"  - Продолжительность: {(end_time - start_time).days} дней")
    
    print(f"\nОбщая статистика:")
    print(f"  - Обработано частей: {len(chunk_stats)}")
    print(f"  - Ожидается записей: {expected_records:,}")
    print(f"  - Фактически записей: {total_records:,}")
    print(f"  - Разница: {expected_records - total_records:,}")
    print(f"  - Полнота данных: {completeness:.2f}%")
    
    print(f"\nПроблемы:")
    print(f"  - Пропущено записей: {total_missing:,}")
    print(f"  - Дубликатов: {total_duplicates:,}")
    print(f"  - Невалидных записей: {total_invalid:,}")
    
    if total_missing > 0:
        missing_percent = (total_missing / expected_records) * 100
        print(f"  - Процент пропусков: {missing_percent:.2f}%")
    
    print(f"\nСтруктура данных:")
    print(f"  - Количество столбцов: {len(column_names)}")
    print(f"  - Интервал данных: {interval_minutes} минут")
    
    print(f"\nСписок столбцов:")
    for i, col in enumerate(column_names, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ДЛЯ ДАЛЬНЕЙШЕГО АНАЛИЗА")
    print("="*60)
    
    print(f"Названия столбцов ({len(column_names)}):")
    for i, col in enumerate(column_names, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nСтатистика для ML модели:")
    print(f"  - Полнота данных: {completeness:.2f}%")
    print(f"  - Качество данных: {'Отличное' if total_missing + total_duplicates + total_invalid == 0 else 'Требует внимания'}")
    print(f"  - Рекомендуется для ML: {'Да' if completeness > 95 else 'С осторожностью'}")
    
    print(f"\n⏱️ Время анализа: {elapsed_time:.1f} секунд ({elapsed_time/60:.1f} минут)")
    print(f"\n" + "="*60)
    print("✓ Анализ завершен!")
    
    # Возвращаем результаты для дальнейшего использования
    stats = {
        'total_records': total_records,
        'expected_records': expected_records,
        'completeness': completeness,
        'missing_records': total_missing,
        'duplicate_records': total_duplicates,
        'invalid_records': total_invalid,
        'start_time': start_time,
        'end_time': end_time,
        'interval_minutes': interval_minutes,
        'column_count': len(column_names),
        'column_names': column_names
    }
    
    return column_names, stats

def check_missing_in_chunk(chunk, start_time, end_time, interval_minutes):
    """
    Проверяет пропуски в части данных.
    """
    if interval_minutes is None:
        return 0
    
    try:
        # Создаем полный временной ряд для части
        full_timeline = pd.date_range(
            start=start_time, 
            end=end_time, 
            freq=f'{interval_minutes}T'
        )
        
        # Находим пропущенные записи
        existing_times = set(chunk['Open time'])
        missing_times = [t for t in full_timeline if t not in existing_times]
        
        return len(missing_times)
    except Exception as e:
        print(f"    ⚠️ Ошибка при проверке пропусков: {e}")
        return 0

def check_validity_in_chunk(chunk):
    """
    Проверяет валидность данных в части.
    """
    invalid_count = 0
    
    # Проверяем логические ошибки
    if 'High' in chunk.columns and 'Low' in chunk.columns:
        invalid_high_low = (chunk['High'] < chunk['Low']).sum()
        invalid_count += invalid_high_low
    
    # Проверяем отрицательные цены
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        if col in chunk.columns:
            invalid_count += (chunk[col] < 0).sum()
    
    # Проверяем отрицательный объем
    if 'Volume' in chunk.columns:
        invalid_count += (chunk['Volume'] < 0).sum()
    
    return invalid_count

def check_price_jumps(df, jump_threshold=40):
    """
    Проверяет аномальные скачки цены больше заданного процента.
    
    Параметры:
    - df: DataFrame с данными
    - jump_threshold: порог скачка в процентах (по умолчанию 40%)
    
    Возвращает:
    - список аномальных скачков с информацией
    """
    print(f"\n🔍 Проверка аномальных скачков цены больше {jump_threshold}%...")
    
    if 'Close' not in df.columns:
        print("❌ Колонка 'Close' не найдена!")
        return []
    
    # Вычисляем процентное изменение цены между соседними свечами
    df['price_change_pct'] = df['Close'].pct_change() * 100
    
    # Находим скачки больше порога
    jump_mask = abs(df['price_change_pct']) > jump_threshold
    jump_indices = df[jump_mask].index.tolist()
    
    if len(jump_indices) == 0:
        print(f"✅ Аномальных скачков больше {jump_threshold}% не найдено!")
        return []
    
    print(f"⚠️ Найдено {len(jump_indices)} аномальных скачков:")
    
    anomalies = []
    for idx in jump_indices:
        if idx == 0:  # Пропускаем первую запись
            continue
            
        current_row = df.iloc[idx]
        prev_row = df.iloc[idx-1]
        
        time_str = current_row['Open time'].strftime('%Y-%m-%d %H:%M:%S') if 'Open time' in df.columns else f"Индекс {idx}"
        change_pct = current_row['price_change_pct']
        prev_price = prev_row['Close']
        curr_price = current_row['Close']
        
        direction = "⬆️" if change_pct > 0 else "⬇️"
        
        anomaly_info = {
            'index': idx,
            'time': time_str,
            'prev_price': prev_price,
            'curr_price': curr_price,
            'change_pct': change_pct,
            'direction': direction
        }
        
        anomalies.append(anomaly_info)
        
        print(f"  {direction} {time_str}: {prev_price:.2f} → {curr_price:.2f} ({change_pct:+.1f}%)")
    
    return anomalies

def fix_price_jumps_new(df, jump_threshold=40):
    """
    Исправляет скачки по логике пользователя:
    - Находит скачок (|% изменения| > jump_threshold)
    - Запоминает цену до скачка (P1)
    - Ищет вперед первую свечу, у которой цена отличается от P1 менее чем на jump_threshold
    - Все свечи между ними (включая скачки) заменяет на линейную интерполяцию между P1 и P2
    - Продолжает с конца интерполяции
    """
    df_fixed = df.copy()
    fixed_count = 0
    i = 1
    n = len(df_fixed)
    while i < n:
        prev_close = df_fixed.iloc[i-1]['Close']
        curr_close = df_fixed.iloc[i]['Close']
        change_pct = abs((curr_close - prev_close) / prev_close * 100)
        if change_pct > jump_threshold:
            # Найти первую нормальную свечу после скачка
            j = i + 1
            while j < n:
                next_close = df_fixed.iloc[j]['Close']
                next_change = abs((next_close - prev_close) / prev_close * 100)
                if next_change < jump_threshold:
                    break
                j += 1
            if j < n:
                # Интерполируем все свечи с i по j-1 включительно
                num_steps = j - i + 1
                for k in range(num_steps):
                    idx = i + k
                    interp = (k + 1) / (num_steps + 1)
                    corrected_price = prev_close + (df_fixed.iloc[j]['Close'] - prev_close) * interp
                    price_ratio = corrected_price / df_fixed.iloc[idx]['Close']
                    for col in ['Open', 'High', 'Low', 'Close']:
                        if col in df_fixed.columns:
                            df_fixed.iloc[idx, df_fixed.columns.get_loc(col)] *= price_ratio
                    fixed_count += 1
                print(f"  ✅ Исправлено {num_steps} свечей с {df_fixed.iloc[i]['Open time']} по {df_fixed.iloc[j]['Open time']}")
                i = j  # Продолжаем с конца интерполяции
            else:
                i += 1
        else:
            i += 1
    return df_fixed, fixed_count

def find_jump_sequences(anomalies):
    """
    Группирует аномальные скачки в последовательности (серии подряд идущих скачков).
    """
    if not anomalies:
        return []
    
    sequences = []
    current_sequence = [anomalies[0]]
    
    for i in range(1, len(anomalies)):
        # Если текущий скачок идет сразу после предыдущего
        if anomalies[i]['index'] == anomalies[i-1]['index'] + 1:
            current_sequence.append(anomalies[i])
        else:
            # Завершаем текущую последовательность и начинаем новую
            sequences.append(current_sequence)
            current_sequence = [anomalies[i]]
    
    # Добавляем последнюю последовательность
    sequences.append(current_sequence)
    
    return sequences

def fix_price_jumps(df, anomalies, jump_threshold=40):
    """
    Исправляет аномальные скачки цены, обрабатывая последовательности скачков целиком.
    """
    if not anomalies:
        return df, 0
    
    print(f"\n🔧 ИСПРАВЛЕНИЕ АНОМАЛЬНЫХ СКАЧКОВ ЦЕНЫ")
    print("=" * 60)
    
    # Группируем скачки в последовательности
    jump_sequences = find_jump_sequences(anomalies)
    print(f"📊 Найдено {len(jump_sequences)} последовательностей скачков:")
    
    for i, seq in enumerate(jump_sequences, 1):
        print(f"  Последовательность {i}: {len(seq)} свечей (индексы {seq[0]['index']}-{seq[-1]['index']})")
    
    fixed_count = 0
    df_fixed = df.copy()
    
    for seq_num, sequence in enumerate(jump_sequences, 1):
        print(f"\n[{seq_num}/{len(jump_sequences)}] Последовательность аномальных скачков:")
        
        first_jump = sequence[0]
        last_jump = sequence[-1]
        
        start_idx = first_jump['index']
        end_idx = last_jump['index']
        
        print(f"  📅 Начало: {first_jump['time']}")
        print(f"  📅 Конец: {last_jump['time']}")
        print(f"  📊 Количество аномальных свечей: {len(sequence)}")
        
        # Находим "нормальную" цену до последовательности скачков
        before_idx = start_idx - 1
        if before_idx < 0:
            print(f"  ❌ Нет данных до последовательности скачков")
            continue
        
        # Находим "нормальную" цену после последовательности скачков
        after_idx = end_idx + 1
        if after_idx >= len(df_fixed):
            print(f"  ❌ Нет данных после последовательности скачков")
            continue
        
        before_price = df_fixed.iloc[before_idx]['Close']
        after_price = df_fixed.iloc[after_idx]['Close']
        
        # Проверяем, отличаются ли "нормальные" цены больше чем на порог
        price_diff = abs((after_price - before_price) / before_price * 100)
        
        print(f"  📊 Цена до последовательности: {before_price:.2f}")
        print(f"  📊 Цена после последовательности: {after_price:.2f}")
        print(f"  📊 Разность нормальных цен: {price_diff:.1f}%")
        
        if price_diff > jump_threshold:
            print(f"  ⚠️ Цены до и после отличаются на {price_diff:.1f}% (> {jump_threshold}%)")
            print(f"  ❌ Исправление невозможно (возможен реальный тренд)")
            continue
        
        # Исправление возможно
        print(f"  ✅ Исправление возможно (разность {price_diff:.1f}% < {jump_threshold}%)")
        
        # Показываем, что будем исправлять
        print(f"  💡 Заменим {len(sequence)} аномальных свечей интерполированными значениями")
        
        while True:
            try:
                choice = input("  🤔 Исправить эту последовательность скачков? (д/н, по умолчанию 'д'): ").strip().lower()
                if choice == "" or choice in ["д", "да", "y", "yes"]:
                    # Исправляем все свечи в последовательности
                    num_steps = end_idx - start_idx + 1
                    
                    for step in range(num_steps):
                        candle_idx = start_idx + step
                        # Линейная интерполяция между before_price и after_price
                        interpolation_factor = (step + 1) / (num_steps + 1)
                        corrected_price = before_price + (after_price - before_price) * interpolation_factor
                        
                        # Получаем текущую цену для расчета коэффициента
                        current_price = df_fixed.iloc[candle_idx]['Close']
                        price_ratio = corrected_price / current_price
                        
                        # Исправляем все цены для этой свечи пропорционально
                        price_columns = ['Open', 'High', 'Low', 'Close']
                        for col in price_columns:
                            if col in df_fixed.columns:
                                df_fixed.iloc[candle_idx, df_fixed.columns.get_loc(col)] *= price_ratio
                        
                        time_str = df_fixed.iloc[candle_idx]['Open time']
                        print(f"    ✅ Свеча {candle_idx} ({time_str}): {current_price:.2f} → {corrected_price:.2f}")
                        fixed_count += 1
                    
                    break
                elif choice in ["н", "нет", "n", "no"]:
                    print(f"  ⏭️ Последовательность пропущена")
                    break
                else:
                    print("  ❌ Введите 'д' (да) или 'н' (нет)")
            except KeyboardInterrupt:
                print("\n❌ Операция отменена пользователем")
                return df_fixed, fixed_count
    
    # Пересчитываем процентные изменения
    df_fixed['price_change_pct'] = df_fixed['Close'].pct_change() * 100
    
    print(f"\n✅ Исправлено {fixed_count} аномальных свечей в {len(jump_sequences)} последовательностях")
    return df_fixed, fixed_count

def ask_for_fix():
    """
    Спрашивает пользователя о необходимости исправления данных.
    """
    print(f"\n" + "="*60)
    print("ИСПРАВЛЕНИЕ ДАННЫХ")
    print("="*60)
    
    print("Обнаружены проблемы в данных:")
    print("  - Пропущенные записи")
    print("  - Дубликаты")
    print("  - Невалидные записи")
    print("  - Возможные аномальные скачки цены")
    
    print(f"\nВарианты действий:")
    print("1. Создать исправленный файл (удалить дубликаты, невалидные записи, проверить скачки цены, заполнить пропуски)")
    print("2. Пропустить исправление")
    
    while True:
        try:
            choice = input("\nВыберите действие (1-2, по умолчанию 1): ").strip()
            if choice == "":
                choice = "1"
            
            if choice in ["1", "2"]:
                return choice
            else:
                print("❌ Выберите 1 или 2!")
                
        except ValueError:
            print("❌ Введите корректное число!")

def fix_data_file():
    """
    Исправляет данные: удаляет дубликаты, невалидные записи и заполняет пропуски.
    """
    file_path = "data/btc_15m_data_2018_to_2025.csv"
    
    # Создаем папку processed_data если её нет
    if not os.path.exists('processed_data'):
        os.makedirs('processed_data')
        print("📁 Создана папка: processed_data")
    
    output_file = "processed_data/input_data.csv"
    
    print(f"\nИсправление данных...")
    print(f"Исходный файл: {file_path}")
    print(f"Исправленный файл: {output_file}")
    
    start_time = time.time()
    
    # Загружаем весь файл
    print("Загрузка данных...")
    df = pd.read_csv(file_path)
    original_count = len(df)
    print(f"Загружено {original_count:,} записей")
    
    # Конвертируем время
    df['Open time'] = pd.to_datetime(df['Open time'])
    
    # Удаляем строки с невалидными датами
    print("Удаление невалидных дат...")
    df = df.dropna(subset=['Open time'])
    after_dates = len(df)
    print(f"Удалено {original_count - after_dates:,} записей с невалидными датами")
    
    # Удаляем дубликаты
    print("Удаление дубликатов...")
    df = df.drop_duplicates(subset=['Open time'], keep='first')
    after_duplicates = len(df)
    print(f"Удалено {after_dates - after_duplicates:,} дубликатов")
    
    # Исправляем невалидные записи
    print("Исправление невалидных записей...")
    invalid_count = 0
    
    # Исправляем High < Low
    if 'High' in df.columns and 'Low' in df.columns:
        invalid_high_low = df['High'] < df['Low']
        if invalid_high_low.sum() > 0:
            df.loc[invalid_high_low, 'High'] = df.loc[invalid_high_low, 'Low']
            invalid_count += invalid_high_low.sum()
    
    # Исправляем отрицательные цены
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        if col in df.columns:
            negative_prices = df[col] < 0
            if negative_prices.sum() > 0:
                df.loc[negative_prices, col] = abs(df.loc[negative_prices, col])
                invalid_count += negative_prices.sum()
    
    # Исправляем отрицательный объем
    if 'Volume' in df.columns:
        negative_volume = df['Volume'] < 0
        if negative_volume.sum() > 0:
            df.loc[negative_volume, 'Volume'] = abs(df.loc[negative_volume, 'Volume'])
            invalid_count += negative_volume.sum()
    
    print(f"Исправлено {invalid_count:,} невалидных записей")
    
    # Сортируем по времени
    df = df.sort_values('Open time').reset_index(drop=True)
    
    # Проверяем и исправляем аномальные скачки цены
    df, jump_fixes = fix_price_jumps_new(df, jump_threshold=40)
    
    # Определяем интервал
    time_diff = df['Open time'].diff().dropna()
    if len(time_diff) > 0:
        interval_minutes = int(time_diff.mode().iloc[0].total_seconds() / 60)
    else:
        interval_minutes = 15
    
    # Заполняем пропуски средними значениями
    print("Заполнение пропусков...")
    start_time_fill = df['Open time'].iloc[0]
    end_time_fill = df['Open time'].iloc[-1]
    
    # Создаем полный временной ряд
    full_timeline = pd.date_range(
        start=start_time_fill, 
        end=end_time_fill, 
        freq=f'{interval_minutes}T'
    )
    
    # Создаем DataFrame с полным временным рядом
    full_df = pd.DataFrame({'Open time': full_timeline})
    
    # Объединяем с существующими данными
    merged_df = pd.merge(full_df, df, on='Open time', how='left')
    
    # Заполняем пропуски средними значениями между предыдущим и последующим
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote asset volume', 
                      'Number of trades', 'Taker buy base asset volume', 
                      'Taker buy quote asset volume']
    
    for col in numeric_columns:
        if col in merged_df.columns:
            # Используем интерполяцию для заполнения пропусков
            merged_df[col] = merged_df[col].interpolate(method='linear')
            
            # Если остались пропуски в начале или конце, заполняем методом forward/backward fill
            merged_df[col] = merged_df[col].fillna(method='ffill').fillna(method='bfill')
    
    # Заполняем остальные столбцы методом forward fill
    other_columns = ['Close time', 'Ignore']
    for col in other_columns:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(method='ffill').fillna(method='bfill')
    
    filled_count = len(merged_df) - len(df)
    print(f"Заполнено {filled_count:,} пропущенных записей")
    
    # Сохраняем исправленный файл
    print("Сохранение исправленного файла...")
    merged_df.to_csv(output_file, index=False)
    
    elapsed_time = time.time() - start_time
    
    print(f"\n" + "="*60)
    print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
    print("="*60)
    
    print(f"Исходный файл: {original_count:,} записей")
    print(f"Исправленный файл: {len(merged_df):,} записей")
    print(f"Изменения:")
    print(f"  - Удалено невалидных дат: {original_count - after_dates:,}")
    print(f"  - Удалено дубликатов: {after_dates - after_duplicates:,}")
    print(f"  - Исправлено невалидных записей: {invalid_count:,}")
    print(f"  - Исправлено аномальных скачков цены: {jump_fixes:,}")
    print(f"  - Заполнено пропусков: {filled_count:,}")
    print(f"  - Чистый прирост: {len(merged_df) - original_count:,}")
    
    print(f"\nФайл сохранен: {output_file}")
    print(f"⏱️ Время исправления: {elapsed_time:.1f} секунд ({elapsed_time/60:.1f} минут)")
    
    return output_file

if __name__ == "__main__":
    # Запускаем быструю проверку
    column_names, stats = quick_data_check()
    
    # Сохраняем результаты в файл для дальнейшего использования
    if column_names and stats:
        print(f"\nСохранение результатов...")
        
        # Сохраняем список столбцов
        with open('column_names.txt', 'w', encoding='utf-8') as f:
            f.write("Список столбцов исходного файла:\n")
            for i, col in enumerate(column_names, 1):
                f.write(f"{i:2d}. {col}\n")
        
        # Сохраняем статистику
        with open('data_statistics.txt', 'w', encoding='utf-8') as f:
            f.write("Статистика данных:\n")
            f.write(f"Всего записей: {stats['total_records']:,}\n")
            f.write(f"Ожидалось записей: {stats['expected_records']:,}\n")
            f.write(f"Полнота данных: {stats['completeness']:.2f}%\n")
            f.write(f"Пропущено записей: {stats['missing_records']:,}\n")
            f.write(f"Дубликатов: {stats['duplicate_records']:,}\n")
            f.write(f"Невалидных записей: {stats['invalid_records']:,}\n")
            f.write(f"Начало данных: {stats['start_time']}\n")
            f.write(f"Конец данных: {stats['end_time']}\n")
            f.write(f"Интервал: {stats['interval_minutes']} минут\n")
            f.write(f"Количество столбцов: {stats['column_count']}\n")
        
        print(f"✓ Результаты сохранены в файлы:")
        print(f"  - column_names.txt (список столбцов)")
        print(f"  - data_statistics.txt (статистика)")
        
        # Спрашиваем о необходимости исправления
        if stats['missing_records'] > 0 or stats['duplicate_records'] > 0 or stats['invalid_records'] > 0:
            fix_choice = ask_for_fix()
            
            if fix_choice == "1":
                fixed_file = fix_data_file()
                print(f"\n✓ Исправленный файл создан: {fixed_file}")
            else:
                print(f"\n✓ Исправление пропущено.")
        else:
            print(f"\n✓ Данные в отличном состоянии! Исправления не требуются.") 