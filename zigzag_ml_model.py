#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class ZigZagMLModel:
    """
    Модель машинного обучения для предсказания вершин зигзага.
    """
    
    def __init__(self, data_file=None, deviation=1.0):
        """
        Инициализация модели.
        
        Параметры:
        - data_file: путь к файлу с данными и метками зигзага
        - deviation: отклонение зигзага в процентах
        """
        self.data_file = data_file or "processed_data/ml_data.csv"
        self.deviation = deviation
        self.zigzag_column = f"zigzag ({deviation}%)"
        self.data = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.models = {}
        self.best_model = None
        self.feature_names = []
        
    def load_data(self):
        """
        Загружает данные и подготавливает их для обучения.
        """
        print("Загрузка данных для обучения модели...")
        print("=" * 60)
        
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Файл {self.data_file} не найден!")
        
        # Загружаем данные
        self.data = pd.read_csv(self.data_file)
        print(f"Загружены данные: {len(self.data)} записей")
        
        # Проверяем наличие колонки с метками
        if self.zigzag_column not in self.data.columns:
            # Пробуем найти колонку с зигзагом
            zigzag_columns = [col for col in self.data.columns if 'zigzag' in col.lower()]
            if zigzag_columns:
                print(f"Найдены колонки зигзага: {zigzag_columns}")
                print(f"Используем первую: {zigzag_columns[0]}")
                self.zigzag_column = zigzag_columns[0]
            else:
                raise ValueError(f"Колонка '{self.zigzag_column}' не найдена в файле!")
        
        # Проверяем расстояние между зигзагами
        self.check_zigzag_distances()
        
        # Показываем статистику меток
        label_counts = self.data[self.zigzag_column].value_counts()
        print(f"\nСтатистика меток:")
        print(f"- Нет вершины (0): {label_counts.get(0, 0)} записей")
        print(f"- Минимумы (-1): {label_counts.get(-1, 0)} записей")
        print(f"- Максимумы (1): {label_counts.get(1, 0)} записей")
        
        return self.data
    
    def check_zigzag_distances(self):
        """
        Проверяет, что расстояние между соседними зигзагами не меньше заданного отклонения.
        Останавливает скрипт при обнаружении меньшего расстояния.
        """
        print(f"\nПроверка расстояний между зигзагами (минимум {self.deviation}%)...")
        
        # Находим все точки зигзага
        zigzag_points = self.data[self.data[self.zigzag_column] != 0]
        
        if len(zigzag_points) < 2:
            print("✓ Найдено менее 2 точек зигзага, проверка не требуется")
            return
        
        print(f"✓ Найдено {len(zigzag_points)} точек зигзага")
        
        # Проверяем расстояния между соседними точками
        for i in range(1, len(zigzag_points)):
            prev_idx = zigzag_points.index[i-1]
            curr_idx = zigzag_points.index[i]
            
            prev_price = zigzag_points.iloc[i-1]['Close']
            curr_price = zigzag_points.iloc[i]['Close']
            
            # Вычисляем процентное изменение
            price_change_pct = abs((curr_price - prev_price) / prev_price * 100)
            
            if price_change_pct < self.deviation:
                print(f"❌ ОШИБКА: Расстояние между зигзагами {price_change_pct:.2f}% меньше минимального {self.deviation}%")
                print(f"   Индексы: {prev_idx} -> {curr_idx}")
                print(f"   Цены: {prev_price:.2f} -> {curr_price:.2f}")
                print(f"   Время: {zigzag_points.iloc[i-1]['Open time']} -> {zigzag_points.iloc[i]['Open time']}")
                raise ValueError(f"Расстояние между зигзагами {price_change_pct:.2f}% меньше минимального {self.deviation}%")
        
        print(f"✓ Все расстояния между зигзагами больше {self.deviation}%")
    
    def create_features(self, window_sizes=[5, 10, 20, 50]):
        """
        Создает признаки для обучения модели.
        
        Параметры:
        - window_sizes: размеры окон для технических индикаторов
        """
        print("\nСоздание признаков для модели...")
        
        if self.data is None:
            self.load_data()
        
        # Создаем копию данных
        df = self.data.copy()
        
        # Базовые признаки цены
        df['price_change'] = df['Close'].pct_change()
        df['high_low_ratio'] = df['High'] / df['Low']
        df['open_close_ratio'] = df['Open'] / df['Close']
        
        # Волатильность
        df['volatility'] = df['price_change'].rolling(window=20).std()
        
        # Технические индикаторы для разных окон
        for window in window_sizes:
            # Скользящие средние
            df[f'sma_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'ema_{window}'] = df['Close'].ewm(span=window).mean()
            
            # Отклонение от скользящих средних
            df[f'deviation_sma_{window}'] = (df['Close'] - df[f'sma_{window}']) / df[f'sma_{window}']
            df[f'deviation_ema_{window}'] = (df['Close'] - df[f'ema_{window}']) / df[f'ema_{window}']
            
            # Максимумы и минимумы в окне
            df[f'high_{window}'] = df['High'].rolling(window=window).max()
            df[f'low_{window}'] = df['Low'].rolling(window=window).min()
            
            # Позиция цены относительно максимума и минимума
            df[f'position_high_{window}'] = (df['Close'] - df[f'low_{window}']) / (df[f'high_{window}'] - df[f'low_{window}'])
            
            # RSI-подобный индикатор
            gains = df['price_change'].where(df['price_change'] > 0, 0)
            losses = -df['price_change'].where(df['price_change'] < 0, 0)
            avg_gains = gains.rolling(window=window).mean()
            avg_losses = losses.rolling(window=window).mean()
            df[f'rsi_{window}'] = 100 - (100 / (1 + avg_gains / avg_losses))
        
        # Признаки тренда
        df['trend_5'] = df['Close'] - df['Close'].shift(5)
        df['trend_10'] = df['Close'] - df['Close'].shift(10)
        df['trend_20'] = df['Close'] - df['Close'].shift(20)
        
        # Признаки импульса
        df['momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        df['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        df['momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        # Признаки объема (если есть)
        if 'Volume' in df.columns:
            df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
        
        # Удаляем NaN значения
        df = df.dropna()
        
        # Выбираем признаки для модели (исключаем метки и базовые цены)
        exclude_columns = [self.zigzag_column, 'Open', 'High', 'Low', 'Close', 'Open time']
        if 'Volume' in df.columns:
            exclude_columns.append('Volume')
        
        self.feature_names = [col for col in df.columns if col not in exclude_columns]
        
        # Подготавливаем данные для обучения
        self.X = df[self.feature_names]
        self.y = df[self.zigzag_column]
        
        print(f"Создано {len(self.feature_names)} признаков:")
        for i, feature in enumerate(self.feature_names[:10]):
            print(f"  {i+1}. {feature}")
        if len(self.feature_names) > 10:
            print(f"  ... и еще {len(self.feature_names) - 10} признаков")
        
        return self.X, self.y
    
    def prepare_data(self, test_size=0.2, random_state=42):
        """
        Разделяет данные на обучающую и тестовую выборки.
        """
        print("\nПодготовка данных для обучения...")
        
        if self.X is None or self.y is None:
            self.create_features()
        
        # Разделяем данные
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=random_state, stratify=self.y
        )
        
        # Масштабируем признаки
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"Обучающая выборка: {len(self.X_train)} записей")
        print(f"Тестовая выборка: {len(self.X_test)} записей")
        
        # Показываем распределение классов
        print(f"\nРаспределение классов в обучающей выборке:")
        train_counts = pd.Series(self.y_train).value_counts()
        for label, count in train_counts.items():
            direction = "Максимум" if label == 1 else "Минимум" if label == -1 else "Нет вершины"
            print(f"  {direction} ({label}): {count} записей")
        
        return self.X_train_scaled, self.X_test_scaled, self.y_train, self.y_test
    
    def train_models(self):
        """
        Обучает несколько моделей и выбирает лучшую.
        """
        print("\nОбучение моделей...")
        print("=" * 60)
        
        if self.X_train_scaled is None:
            self.prepare_data()
        
        # Определяем модели для тестирования
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        # Обучаем модели и оцениваем их
        results = {}
        
        for name, model in models.items():
            print(f"\nОбучение {name}...")
            
            # Обучаем модель
            model.fit(self.X_train_scaled, self.y_train)
            
            # Предсказываем на тестовой выборке
            y_pred = model.predict(self.X_test_scaled)
            
            # Оцениваем точность
            accuracy = accuracy_score(self.y_test, y_pred)
            
            # Кросс-валидация
            cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=5)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predictions': y_pred
            }
            
            print(f"  Точность на тестовой выборке: {accuracy:.4f}")
            print(f"  Кросс-валидация: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Выбираем лучшую модель
        best_model_name = max(results.keys(), key=lambda x: results[x]['cv_mean'])
        self.best_model = results[best_model_name]['model']
        self.models = results
        
        print(f"\nЛучшая модель: {best_model_name}")
        print(f"Точность: {results[best_model_name]['accuracy']:.4f}")
        
        return results
    
    def evaluate_model(self, model_name=None):
        """
        Оценивает производительность модели.
        """
        if model_name is None:
            model_name = list(self.models.keys())[0]
        
        model = self.models[model_name]['model']
        y_pred = self.models[model_name]['predictions']
        
        print(f"\nОценка модели: {model_name}")
        print("=" * 60)
        
        # Матрица ошибок
        print("Матрица ошибок:")
        cm = confusion_matrix(self.y_test, y_pred)
        print(cm)
        
        # Детальный отчет
        print("\nДетальный отчет:")
        print(classification_report(self.y_test, y_pred, 
                                  target_names=['Нет вершины', 'Минимум', 'Максимум']))
        
        # Важность признаков (для Random Forest и Gradient Boosting)
        if hasattr(model, 'feature_importances_'):
            print(f"\nТоп-10 важных признаков:")
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            for i, (_, row) in enumerate(feature_importance.head(10).iterrows()):
                print(f"  {i+1}. {row['feature']}: {row['importance']:.4f}")
    
    def predict_probability(self, current_data):
        """
        Предсказывает вероятность того, что текущая цена является вершиной зигзага.
        
        Параметры:
        - current_data: DataFrame с текущими данными (должен содержать те же признаки)
        
        Возвращает:
        - probabilities: вероятности для каждого класса
        """
        if self.best_model is None:
            raise ValueError("Модель не обучена! Сначала вызовите train_models()")
        
        # Подготавливаем данные
        if isinstance(current_data, pd.DataFrame):
            features = current_data[self.feature_names]
        else:
            features = current_data
        
        # Масштабируем признаки
        features_scaled = self.scaler.transform(features)
        
        # Предсказываем вероятности
        probabilities = self.best_model.predict_proba(features_scaled)
        
        return probabilities
    
    def save_model(self, filename='zigzag_model.pkl'):
        """
        Сохраняет обученную модель.
        """
        if self.best_model is None:
            raise ValueError("Модель не обучена!")
        
        model_data = {
            'model': self.best_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'models': self.models
        }
        
        joblib.dump(model_data, filename)
        print(f"✓ Модель сохранена: {filename}")
    
    def load_model(self, filename='zigzag_model.pkl'):
        """
        Загружает сохраненную модель.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл модели {filename} не найден!")
        
        model_data = joblib.load(filename)
        self.best_model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.models = model_data['models']
        
        print(f"✓ Модель загружена: {filename}")
    
    def plot_results(self):
        """
        Визуализирует результаты обучения.
        """
        if not self.models:
            print("Нет результатов для визуализации!")
            return
        
        # Создаем график с результатами
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Сравнение точности моделей
        model_names = list(self.models.keys())
        accuracies = [self.models[name]['accuracy'] for name in model_names]
        cv_means = [self.models[name]['cv_mean'] for name in model_names]
        
        x = np.arange(len(model_names))
        width = 0.35
        
        axes[0, 0].bar(x - width/2, accuracies, width, label='Тестовая точность')
        axes[0, 0].bar(x + width/2, cv_means, width, label='Кросс-валидация')
        axes[0, 0].set_xlabel('Модели')
        axes[0, 0].set_ylabel('Точность')
        axes[0, 0].set_title('Сравнение точности моделей')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(model_names, rotation=45)
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Матрица ошибок лучшей модели
        best_model_name = max(self.models.keys(), key=lambda x: self.models[x]['cv_mean'])
        y_pred = self.models[best_model_name]['predictions']
        cm = confusion_matrix(self.y_test, y_pred)
        
        im = axes[0, 1].imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        axes[0, 1].set_title(f'Матрица ошибок: {best_model_name}')
        axes[0, 1].set_xlabel('Предсказанный класс')
        axes[0, 1].set_ylabel('Истинный класс')
        
        # Добавляем текст в ячейки
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                axes[0, 1].text(j, i, format(cm[i, j], 'd'),
                               ha="center", va="center",
                               color="white" if cm[i, j] > thresh else "black")
        
        # 3. Важность признаков (если доступна)
        if hasattr(self.best_model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            top_features = feature_importance.head(15)
            axes[1, 0].barh(range(len(top_features)), top_features['importance'])
            axes[1, 0].set_yticks(range(len(top_features)))
            axes[1, 0].set_yticklabels(top_features['feature'])
            axes[1, 0].set_xlabel('Важность')
            axes[1, 0].set_title('Топ-15 важных признаков')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Распределение предсказаний
        axes[1, 1].hist(y_pred, bins=3, alpha=0.7, edgecolor='black')
        axes[1, 1].set_xlabel('Предсказанный класс')
        axes[1, 1].set_ylabel('Количество')
        axes[1, 1].set_title('Распределение предсказаний')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('zigzag_model_results.png', dpi=300, bbox_inches='tight')
        print("✓ График результатов сохранен: zigzag_model_results.png")
        plt.show()

def main():
    """
    Основная функция для обучения модели.
    """
    print("Обучение модели для предсказания вершин зигзага")
    print("=" * 80)
    
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
        
        # Создаем модель
        model = ZigZagMLModel(deviation=deviation)
        
        # Загружаем данные
        model.load_data()
        
        # Создаем признаки
        model.create_features()
        
        # Подготавливаем данные
        model.prepare_data()
        
        # Обучаем модели
        results = model.train_models()
        
        # Оцениваем лучшую модель
        best_model_name = max(results.keys(), key=lambda x: results[x]['cv_mean'])
        model.evaluate_model(best_model_name)
        
        # Визуализируем результаты
        model.plot_results()
        
        # Сохраняем модель
        model.save_model()
        
        print("\n" + "=" * 80)
        print("✓ Обучение модели завершено успешно!")
        print("✓ Модель готова для предсказания вершин зигзага")
        
    except Exception as e:
        print(f"Ошибка при обучении модели: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 