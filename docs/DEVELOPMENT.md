# Руководство по Разработке

Это руководство описывает процесс разработки, настройку локальной среды и лучшие практики для работы с проектом Crypto Trading Bot.

## 📋 Содержание

- [Быстрый Старт](#быстрый-старт)
- [Настройка Среды Разработки](#настройка-среды-разработки)
- [Структура Проекта](#структура-проекта)
- [Стандарты Кодирования](#стандарты-кодирования)
- [Тестирование](#тестирование)
- [Отладка](#отладка)
- [Контрибьюция](#контрибьюция)

## 🚀 Быстрый Старт

### Предварительные Требования

- Python 3.9+
- Git 2.30+
- Docker 20.10+ (опционально)
- IDE/редактор (рекомендуется VS Code или PyCharm)

### Установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/israweb/dosbot.git
cd crypto-trading-bot

# 2. Создание виртуального окружения
python -m venv .venv

# 3. Активация виртуального окружения
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 4. Обновление pip
python -m pip install --upgrade pip

# 5. Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Настройка окружения
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# 7. Создание необходимых директорий
mkdir -p data processed_data logs models charts

# 8. Запуск тестов
pytest tests/ -v

# 9. Проверка линтеров
flake8 src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
```

## 🛠️ Настройка Среды Разработки

### VS Code

Рекомендуемые расширения:

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.pylint",
        "ms-toolsai.jupyter",
        "ms-vscode.docker",
        "redhat.vscode-yaml",
        "ms-vscode.vscode-json"
    ]
}
```

Настройки VS Code:

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false,
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

Конфигурация отладки:

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main Application",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: ZigZag Analyzer",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/zigzag_analyzer.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### PyCharm

Настройки для PyCharm:

1. **Интерпретатор Python**: Настройте виртуальное окружение `.venv`
2. **Code Style**: 
   - Python → Black formatter
   - Imports → isort с профилем black
3. **Inspections**: Включите flake8
4. **Run Configurations**: Создайте конфигурации для main.py и тестов

### Pre-commit Hooks

```bash
# Установка pre-commit
pip install pre-commit

# Установка хуков
pre-commit install
```

Конфигурация `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=88]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile, black]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [--skip, B101,B601]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

## 📁 Структура Проекта

```
crypto-trading-bot/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml             # CI pipeline
│       └── release.yml        # Release automation
├── docs/                      # Документация
│   ├── DEPLOYMENT.md          # Руководство по развертыванию
│   ├── ENVIRONMENT.md         # Конфигурация окружения
│   ├── DEVELOPMENT.md         # Руководство по разработке
│   └── API.md                 # API документация
├── src/                       # Основной код приложения
│   ├── bot/                   # Торговый бот
│   │   └── __init__.py
│   ├── models/                # ML модели
│   │   └── model.py
│   ├── utils/                 # Утилиты
│   │   └── helpers.py
│   ├── config.py              # Конфигурация
│   └── main.py                # Точка входа
├── tests/                     # Тесты
│   ├── __init__.py
│   ├── test_basic.py          # Базовые тесты
│   ├── test_bot.py            # Тесты бота
│   ├── test_config.py         # Тесты конфигурации
│   └── test_zigzag_analyzer.py # Тесты ZigZag анализатора
├── data/                      # Исходные данные
├── processed_data/            # Обработанные данные
├── logs/                      # Файлы логов
├── models/                    # Сохраненные ML модели
├── charts/                    # Графики и визуализации
├── scripts/                   # Скрипты автоматизации
├── requirements.txt           # Основные зависимости
├── requirements-dev.txt       # Зависимости для разработки
├── pyproject.toml            # Конфигурация проекта
├── pytest.ini               # Конфигурация pytest
├── .env.example              # Пример переменных окружения
├── .gitignore               # Git ignore файл
├── Dockerfile               # Docker образ
├── docker-compose.yml       # Docker Compose конфигурация
└── README.md                # Основная документация
```

### Описание Модулей

#### `src/bot/`
Основная логика торгового бота:
- `__init__.py` - Инициализация модуля
- `crypto_bot.py` - Основной класс бота
- `strategies/` - Торговые стратегии
- `indicators/` - Технические индикаторы

#### `src/models/`
Модели машинного обучения:
- `model.py` - Базовый класс модели
- `zigzag_model.py` - ZigZag модель
- `predictors/` - Различные предикторы

#### `src/utils/`
Вспомогательные утилиты:
- `helpers.py` - Общие функции
- `data_processor.py` - Обработка данных
- `logger.py` - Настройка логирования
- `metrics.py` - Метрики и мониторинг

## 📝 Стандарты Кодирования

### Python Style Guide

Проект следует [PEP 8](https://pep8.org/) с некоторыми дополнениями:

- **Длина строки**: 88 символов (Black default)
- **Импорты**: Сортировка с помощью isort
- **Форматирование**: Black formatter
- **Линтинг**: flake8 с дополнительными правилами

### Именование

```python
# Классы - PascalCase
class CryptoBot:
    pass

# Функции и переменные - snake_case
def calculate_zigzag_points():
    max_position_size = 1000

# Константы - UPPER_SNAKE_CASE
API_TIMEOUT = 30
DEFAULT_TIMEFRAME = "1h"

# Приватные методы - префикс _
def _internal_method(self):
    pass

# Защищенные атрибуты - префикс _
self._api_client = None
```

### Документация

Используйте Google Style docstrings:

```python
def calculate_zigzag(data: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """Вычисляет ZigZag индикатор для временного ряда.
    
    Args:
        data: DataFrame с ценовыми данными (OHLCV)
        threshold: Минимальный процент изменения для ZigZag точки
        
    Returns:
        DataFrame с добавленными ZigZag точками
        
    Raises:
        ValueError: Если данные пусты или threshold некорректный
        
    Example:
        >>> data = pd.DataFrame({'close': [100, 105, 95, 110]})
        >>> zigzag_data = calculate_zigzag(data, threshold=0.05)
    """
    if data.empty:
        raise ValueError("Data cannot be empty")
    
    if not 0 < threshold < 1:
        raise ValueError("Threshold must be between 0 and 1")
    
    # Реализация...
    return data
```

### Type Hints

Используйте аннотации типов:

```python
from typing import Dict, List, Optional, Union
import pandas as pd

def process_market_data(
    data: pd.DataFrame,
    symbols: List[str],
    config: Dict[str, Union[str, int, float]]
) -> Optional[pd.DataFrame]:
    """Обработка рыночных данных."""
    pass
```

### Обработка Ошибок

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TradingError(Exception):
    """Базовое исключение для торговых операций."""
    pass

class APIError(TradingError):
    """Ошибка API запроса."""
    pass

def fetch_market_data(symbol: str) -> Optional[pd.DataFrame]:
    """Получение рыночных данных с обработкой ошибок."""
    try:
        # API запрос
        response = api_client.get_klines(symbol)
        return pd.DataFrame(response)
    except requests.RequestException as e:
        logger.error(f"API request failed for {symbol}: {e}")
        raise APIError(f"Failed to fetch data for {symbol}") from e
    except Exception as e:
        logger.exception(f"Unexpected error fetching data for {symbol}")
        return None
```

## 🧪 Тестирование

### Структура Тестов

```python
# tests/test_crypto_bot.py
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.bot.crypto_bot import CryptoBot
from src.config import Config

class TestCryptoBot:
    """Тесты для класса CryptoBot."""
    
    @pytest.fixture
    def mock_config(self):
        """Мок конфигурации для тестов."""
        config = Mock(spec=Config)
        config.API_KEY = "test_key"
        config.API_SECRET = "test_secret"
        config.SYMBOL = "BTCUSDT"
        return config
    
    @pytest.fixture
    def crypto_bot(self, mock_config):
        """Экземпляр CryptoBot для тестов."""
        return CryptoBot(mock_config)
    
    def test_initialization(self, crypto_bot, mock_config):
        """Тест инициализации бота."""
        assert crypto_bot.config == mock_config
        assert crypto_bot.api_client is not None
    
    @patch('src.bot.crypto_bot.requests.get')
    def test_fetch_market_data_success(self, mock_get, crypto_bot):
        """Тест успешного получения рыночных данных."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = [
            [1640995200000, "47000", "48000", "46000", "47500", "100"]
        ]
        mock_get.return_value = mock_response
        
        # Act
        result = crypto_bot.fetch_market_data()
        
        # Assert
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
    
    def test_fetch_market_data_api_error(self, crypto_bot):
        """Тест обработки ошибки API."""
        with patch('src.bot.crypto_bot.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")
            
            with pytest.raises(APIError):
                crypto_bot.fetch_market_data()
    
    @pytest.mark.parametrize("symbol,expected", [
        ("BTCUSDT", True),
        ("ETHUSDT", True),
        ("INVALID", False),
    ])
    def test_validate_symbol(self, crypto_bot, symbol, expected):
        """Параметризованный тест валидации символов."""
        result = crypto_bot.validate_symbol(symbol)
        assert result == expected
```

### Запуск Тестов

```bash
# Все тесты
pytest

# Тесты с покрытием
pytest --cov=src --cov-report=html

# Конкретный файл
pytest tests/test_crypto_bot.py

# Конкретный тест
pytest tests/test_crypto_bot.py::TestCryptoBot::test_initialization

# Параллельное выполнение
pytest -n auto

# Только быстрые тесты
pytest -m "not slow"

# Подробный вывод
pytest -v -s
```

### Маркеры Тестов

```python
# pytest.ini
[tool:pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests that require API access

# Использование в тестах
@pytest.mark.slow
def test_long_running_operation():
    pass

@pytest.mark.integration
def test_database_integration():
    pass
```

## 🐛 Отладка

### Логирование

```python
# src/utils/logger.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = None, level: str = "INFO") -> logging.Logger:
    """Настройка логгера с ротацией файлов."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый хендлер с ротацией
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Использование
logger = setup_logger(__name__, "logs/trading.log", "DEBUG")
logger.info("Application started")
```

### Профилирование

```python
# Декоратор для профилирования
import functools
import time
from typing import Callable

def profile_time(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Использование
@profile_time
def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    # Вычисления...
    return data
```

### Отладка с pdb

```python
import pdb

def problematic_function(data):
    # Точка останова
    pdb.set_trace()
    
    # Код для отладки
    result = complex_calculation(data)
    return result

# В командной строке:
# (Pdb) p data  # печать переменной
# (Pdb) n       # следующая строка
# (Pdb) s       # шаг в функцию
# (Pdb) c       # продолжить выполнение
```

## 🤝 Контрибьюция

### Процесс Разработки

1. **Fork репозитория**
2. **Создание ветки для фичи**:
   ```bash
   git checkout -b feature/new-trading-strategy
   ```
3. **Разработка и тестирование**
4. **Коммиты** (следуйте [Conventional Commits](https://www.conventionalcommits.org/)):
   ```bash
   git commit -m "feat: add new trading strategy"
   git commit -m "fix: resolve API timeout issue"
   git commit -m "docs: update trading strategy documentation"
   ```
5. **Push и создание Pull Request**

### Типы Коммитов

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг без изменения функциональности
- `test:` - добавление или изменение тестов
- `chore:` - обновление зависимостей, конфигурации

### Pull Request Checklist

- [ ] Код соответствует стандартам проекта
- [ ] Все тесты проходят
- [ ] Добавлены тесты для новой функциональности
- [ ] Документация обновлена
- [ ] Changelog обновлен (для значительных изменений)
- [ ] Pre-commit хуки проходят

### Code Review

Критерии для ревью:
- **Функциональность**: Код работает корректно
- **Читаемость**: Код легко понимается
- **Тестируемость**: Код покрыт тестами
- **Производительность**: Нет очевидных проблем с производительностью
- **Безопасность**: Нет уязвимостей безопасности

## 📚 Дополнительные Ресурсы

### Полезные Команды

```bash
# Анализ кода
flake8 src/ --statistics
black --diff src/
isort --diff src/

# Безопасность
bandit -r src/
safety check

# Зависимости
pip-audit
pipdeptree

# Документация
sphinx-build -b html docs/ docs/_build/

# Docker разработка
docker-compose -f docker-compose.dev.yml up
docker-compose exec app bash
```

### Рекомендуемые Библиотеки

- **Тестирование**: pytest, pytest-cov, pytest-mock
- **Линтинг**: flake8, black, isort, bandit
- **Типизация**: mypy, pydantic
- **Документация**: sphinx, mkdocs
- **Мониторинг**: prometheus-client, structlog
- **Async**: asyncio, aiohttp, asyncpg

### Обучающие Материалы

- [Python Best Practices](https://docs.python-guide.org/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/)
- [Clean Code Python](https://github.com/zedr/clean-code-python)
- [Python Patterns](https://python-patterns.guide/)
