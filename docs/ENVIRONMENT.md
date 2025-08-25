# Конфигурация Окружения

Это руководство описывает настройку переменных окружения и конфигурации для различных сред развертывания.

## 📋 Содержание

- [Переменные Окружения](#переменные-окружения)
- [Конфигурационные Файлы](#конфигурационные-файлы)
- [Секреты и Безопасность](#секреты-и-безопасность)
- [Среды Развертывания](#среды-развертывания)
- [Валидация Конфигурации](#валидация-конфигурации)

## 🔧 Переменные Окружения

### Основные Переменные

```bash
# =============================================================================
# ОСНОВНАЯ КОНФИГУРАЦИЯ
# =============================================================================

# Окружение (development, staging, production)
ENVIRONMENT=development

# Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Путь к файлу логов
LOG_FILE=logs/trading.log

# =============================================================================
# API КОНФИГУРАЦИЯ
# =============================================================================

# API ключи биржи (ОБЯЗАТЕЛЬНО для продакшена)
API_KEY=your_exchange_api_key_here
API_SECRET=your_exchange_api_secret_here

# Базовый URL API биржи
BASE_URL=https://api.binance.com

# Таймаут запросов (секунды)
API_TIMEOUT=30

# Максимальное количество повторных попыток
MAX_RETRIES=3

# =============================================================================
# ТОРГОВАЯ КОНФИГУРАЦИЯ
# =============================================================================

# Торговая пара
SYMBOL=BTCUSDT

# Временной интервал для анализа
TIMEFRAME=1h

# Максимальный размер позиции (USDT)
MAX_POSITION_SIZE=1000

# Процент стоп-лосса
STOP_LOSS_PERCENT=2.0

# Процент тейк-профита
TAKE_PROFIT_PERCENT=5.0

# Минимальный размер ордера
MIN_ORDER_SIZE=10

# =============================================================================
# МАШИННОЕ ОБУЧЕНИЕ
# =============================================================================

# Интервал обновления модели (секунды)
MODEL_UPDATE_INTERVAL=3600

# Размер окна для признаков
FEATURE_WINDOW=100

# Порог для принятия торговых решений
PREDICTION_THRESHOLD=0.7

# Путь к сохраненной модели
MODEL_PATH=models/zigzag_model.pkl

# Количество эпох для обучения
TRAINING_EPOCHS=100

# Размер батча
BATCH_SIZE=32

# Скорость обучения
LEARNING_RATE=0.001

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================

# URL подключения к PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_trading

# URL подключения к Redis
REDIS_URL=redis://localhost:6379/0

# Максимальное количество соединений в пуле
DB_POOL_SIZE=10

# Таймаут подключения к БД (секунды)
DB_TIMEOUT=30

# =============================================================================
# МОНИТОРИНГ И МЕТРИКИ
# =============================================================================

# Порт для Prometheus метрик
PROMETHEUS_PORT=9090

# Порт для Grafana
GRAFANA_PORT=3000

# Интервал сбора метрик (секунды)
METRICS_INTERVAL=60

# Включить детальные метрики (true/false)
DETAILED_METRICS=false

# =============================================================================
# БЕЗОПАСНОСТЬ
# =============================================================================

# Секретный ключ для JWT токенов
JWT_SECRET=your_jwt_secret_key_here

# Ключ для шифрования чувствительных данных
ENCRYPTION_KEY=your_encryption_key_here

# Время жизни JWT токена (секунды)
JWT_EXPIRATION=3600

# Включить HTTPS (true/false)
ENABLE_HTTPS=false

# =============================================================================
# УВЕДОМЛЕНИЯ
# =============================================================================

# Telegram Bot Token для уведомлений
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Telegram Chat ID для отправки уведомлений
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Email настройки для уведомлений
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password

# Webhook URL для уведомлений
WEBHOOK_URL=https://your-webhook-url.com/notifications

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
# =============================================================================

# Часовой пояс
TIMEZONE=UTC

# Максимальное количество воркеров
MAX_WORKERS=4

# Интервал между торговыми циклами (секунды)
TRADING_INTERVAL=60

# Включить режим отладки (true/false)
DEBUG_MODE=false

# Путь к директории с данными
DATA_DIR=data/

# Путь к директории с обработанными данными
PROCESSED_DATA_DIR=processed_data/

# Максимальный размер файла лога (MB)
MAX_LOG_SIZE=100

# Количество файлов логов для ротации
LOG_BACKUP_COUNT=5
```

### Создание .env файла

```bash
# Создание из шаблона
cp .env.example .env

# Редактирование
nano .env  # или любой другой редактор
```

## 📁 Конфигурационные Файлы

### src/config.py

```python
import os
from typing import Optional
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Основная конфигурация приложения."""
    
    # Основные настройки
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/trading.log")
    
    # API настройки
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    BASE_URL = os.getenv("BASE_URL", "https://api.binance.com")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Торговые настройки
    SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
    TIMEFRAME = os.getenv("TIMEFRAME", "1h")
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "1000"))
    STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "2.0"))
    TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "5.0"))
    MIN_ORDER_SIZE = float(os.getenv("MIN_ORDER_SIZE", "10"))
    
    # ML настройки
    MODEL_UPDATE_INTERVAL = int(os.getenv("MODEL_UPDATE_INTERVAL", "3600"))
    FEATURE_WINDOW = int(os.getenv("FEATURE_WINDOW", "100"))
    PREDICTION_THRESHOLD = float(os.getenv("PREDICTION_THRESHOLD", "0.7"))
    MODEL_PATH = os.getenv("MODEL_PATH", "models/zigzag_model.pkl")
    TRAINING_EPOCHS = int(os.getenv("TRAINING_EPOCHS", "100"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.001"))
    
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))
    
    # Мониторинг
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))
    GRAFANA_PORT = int(os.getenv("GRAFANA_PORT", "3000"))
    METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", "60"))
    DETAILED_METRICS = os.getenv("DETAILED_METRICS", "false").lower() == "true"
    
    # Безопасность
    JWT_SECRET = os.getenv("JWT_SECRET")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "3600"))
    ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    
    # Уведомления
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # Дополнительные настройки
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    TRADING_INTERVAL = int(os.getenv("TRADING_INTERVAL", "60"))
    DATA_DIR = os.getenv("DATA_DIR", "data/")
    PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "processed_data/")
    MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", "100"))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    @classmethod
    def validate(cls) -> bool:
        """Валидация обязательных настроек."""
        required_vars = []
        
        if cls.ENVIRONMENT == "production":
            required_vars.extend([
                ("API_KEY", cls.API_KEY),
                ("API_SECRET", cls.API_SECRET),
                ("JWT_SECRET", cls.JWT_SECRET),
                ("ENCRYPTION_KEY", cls.ENCRYPTION_KEY),
            ])
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Получение конфигурации базы данных."""
        return {
            "url": cls.DATABASE_URL,
            "pool_size": cls.DB_POOL_SIZE,
            "timeout": cls.DB_TIMEOUT,
        }
    
    @classmethod
    def get_trading_config(cls) -> dict:
        """Получение торговой конфигурации."""
        return {
            "symbol": cls.SYMBOL,
            "timeframe": cls.TIMEFRAME,
            "max_position_size": cls.MAX_POSITION_SIZE,
            "stop_loss_percent": cls.STOP_LOSS_PERCENT,
            "take_profit_percent": cls.TAKE_PROFIT_PERCENT,
            "min_order_size": cls.MIN_ORDER_SIZE,
            "trading_interval": cls.TRADING_INTERVAL,
        }
    
    @classmethod
    def get_ml_config(cls) -> dict:
        """Получение конфигурации ML."""
        return {
            "model_update_interval": cls.MODEL_UPDATE_INTERVAL,
            "feature_window": cls.FEATURE_WINDOW,
            "prediction_threshold": cls.PREDICTION_THRESHOLD,
            "model_path": cls.MODEL_PATH,
            "training_epochs": cls.TRAINING_EPOCHS,
            "batch_size": cls.BATCH_SIZE,
            "learning_rate": cls.LEARNING_RATE,
        }

# Создание экземпляра конфигурации
config = Config()
```

## 🔐 Секреты и Безопасность

### Управление Секретами

#### 1. Локальная Разработка

```bash
# Создание .env файла с секретами
cat > .env << EOF
API_KEY=your_development_api_key
API_SECRET=your_development_api_secret
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
EOF

# Установка правильных прав доступа
chmod 600 .env
```

#### 2. Docker Secrets

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: crypto-trading-bot:latest
    secrets:
      - api_key
      - api_secret
      - jwt_secret
    environment:
      - API_KEY_FILE=/run/secrets/api_key
      - API_SECRET_FILE=/run/secrets/api_secret
      - JWT_SECRET_FILE=/run/secrets/jwt_secret

secrets:
  api_key:
    file: ./secrets/api_key.txt
  api_secret:
    file: ./secrets/api_secret.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

#### 3. Kubernetes Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: crypto-trading-secrets
  namespace: crypto-trading
type: Opaque
data:
  api-key: <base64-encoded-api-key>
  api-secret: <base64-encoded-api-secret>
  jwt-secret: <base64-encoded-jwt-secret>
  encryption-key: <base64-encoded-encryption-key>
```

```bash
# Создание секрета из командной строки
kubectl create secret generic crypto-trading-secrets \
  --from-literal=api-key=your_api_key \
  --from-literal=api-secret=your_api_secret \
  --from-literal=jwt-secret=your_jwt_secret \
  --from-literal=encryption-key=your_encryption_key \
  -n crypto-trading
```

### Шифрование Конфигурации

```python
# utils/encryption.py
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigEncryption:
    """Утилита для шифрования/дешифрования конфигурации."""
    
    def __init__(self, password: str):
        self.password = password.encode()
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """Генерация ключа из пароля."""
        salt = b'crypto_trading_salt'  # В продакшене используйте случайную соль
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_config(self, config_data: dict) -> str:
        """Шифрование конфигурации."""
        import json
        config_json = json.dumps(config_data)
        encrypted_data = self.fernet.encrypt(config_json.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_config(self, encrypted_config: str) -> dict:
        """Дешифрование конфигурации."""
        import json
        encrypted_data = base64.urlsafe_b64decode(encrypted_config.encode())
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())

# Использование
# encryption = ConfigEncryption("your_master_password")
# encrypted = encryption.encrypt_config({"api_key": "secret_key"})
# decrypted = encryption.decrypt_config(encrypted)
```

## 🌍 Среды Развертывания

### Development (.env.development)

```bash
ENVIRONMENT=development
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Тестовые API ключи
API_KEY=test_api_key
API_SECRET=test_api_secret
BASE_URL=https://testnet.binance.vision

# Локальная база данных
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/1

# Минимальные размеры для тестирования
MAX_POSITION_SIZE=10
MIN_ORDER_SIZE=1

# Быстрые интервалы для тестирования
MODEL_UPDATE_INTERVAL=60
TRADING_INTERVAL=10
```

### Staging (.env.staging)

```bash
ENVIRONMENT=staging
DEBUG_MODE=false
LOG_LEVEL=INFO

# Staging API ключи
API_KEY=staging_api_key
API_SECRET=staging_api_secret
BASE_URL=https://testnet.binance.vision

# Staging база данных
DATABASE_URL=postgresql://user:pass@staging-db:5432/crypto_trading
REDIS_URL=redis://staging-redis:6379/0

# Умеренные размеры для staging
MAX_POSITION_SIZE=100
MIN_ORDER_SIZE=5

# Стандартные интервалы
MODEL_UPDATE_INTERVAL=1800
TRADING_INTERVAL=30
```

### Production (.env.production)

```bash
ENVIRONMENT=production
DEBUG_MODE=false
LOG_LEVEL=WARNING

# Продакшен API ключи (должны быть в секретах)
API_KEY=${API_KEY}
API_SECRET=${API_SECRET}
BASE_URL=https://api.binance.com

# Продакшен база данных
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}

# Продакшен размеры
MAX_POSITION_SIZE=1000
MIN_ORDER_SIZE=10

# Продакшен интервалы
MODEL_UPDATE_INTERVAL=3600
TRADING_INTERVAL=60

# Безопасность
ENABLE_HTTPS=true
JWT_EXPIRATION=1800

# Мониторинг
DETAILED_METRICS=true
METRICS_INTERVAL=30
```

## ✅ Валидация Конфигурации

### Скрипт Валидации

```python
# scripts/validate_config.py
#!/usr/bin/env python3
"""Скрипт для валидации конфигурации."""

import os
import sys
from typing import List, Tuple
from src.config import Config

def validate_environment_variables() -> List[str]:
    """Валидация переменных окружения."""
    errors = []
    
    # Проверка обязательных переменных для продакшена
    if Config.ENVIRONMENT == "production":
        required_vars = [
            "API_KEY", "API_SECRET", "JWT_SECRET", "ENCRYPTION_KEY",
            "DATABASE_URL", "REDIS_URL"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
    
    # Проверка числовых значений
    numeric_vars = [
        ("API_TIMEOUT", Config.API_TIMEOUT),
        ("MAX_RETRIES", Config.MAX_RETRIES),
        ("MAX_POSITION_SIZE", Config.MAX_POSITION_SIZE),
        ("STOP_LOSS_PERCENT", Config.STOP_LOSS_PERCENT),
        ("TAKE_PROFIT_PERCENT", Config.TAKE_PROFIT_PERCENT),
    ]
    
    for var_name, var_value in numeric_vars:
        if var_value <= 0:
            errors.append(f"Invalid value for {var_name}: {var_value} (must be > 0)")
    
    # Проверка процентных значений
    if not (0 < Config.STOP_LOSS_PERCENT < 100):
        errors.append(f"STOP_LOSS_PERCENT must be between 0 and 100, got: {Config.STOP_LOSS_PERCENT}")
    
    if not (0 < Config.TAKE_PROFIT_PERCENT < 100):
        errors.append(f"TAKE_PROFIT_PERCENT must be between 0 and 100, got: {Config.TAKE_PROFIT_PERCENT}")
    
    # Проверка URL
    if Config.DATABASE_URL and not Config.DATABASE_URL.startswith(('postgresql://', 'sqlite://')):
        errors.append(f"Invalid DATABASE_URL format: {Config.DATABASE_URL}")
    
    if not Config.REDIS_URL.startswith('redis://'):
        errors.append(f"Invalid REDIS_URL format: {Config.REDIS_URL}")
    
    return errors

def validate_file_paths() -> List[str]:
    """Валидация путей к файлам и директориям."""
    errors = []
    
    # Проверка директорий
    directories = [
        Config.DATA_DIR,
        Config.PROCESSED_DATA_DIR,
        os.path.dirname(Config.LOG_FILE),
        os.path.dirname(Config.MODEL_PATH),
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {directory}: {e}")
    
    return errors

def validate_trading_parameters() -> List[str]:
    """Валидация торговых параметров."""
    errors = []
    
    # Проверка логики торговых параметров
    if Config.STOP_LOSS_PERCENT >= Config.TAKE_PROFIT_PERCENT:
        errors.append("STOP_LOSS_PERCENT should be less than TAKE_PROFIT_PERCENT")
    
    if Config.MIN_ORDER_SIZE >= Config.MAX_POSITION_SIZE:
        errors.append("MIN_ORDER_SIZE should be less than MAX_POSITION_SIZE")
    
    # Проверка временных интервалов
    if Config.TRADING_INTERVAL < 10:
        errors.append("TRADING_INTERVAL should be at least 10 seconds")
    
    if Config.MODEL_UPDATE_INTERVAL < 300:
        errors.append("MODEL_UPDATE_INTERVAL should be at least 300 seconds (5 minutes)")
    
    return errors

def main():
    """Основная функция валидации."""
    print("🔍 Validating configuration...")
    
    all_errors = []
    
    # Валидация переменных окружения
    env_errors = validate_environment_variables()
    all_errors.extend(env_errors)
    
    # Валидация путей
    path_errors = validate_file_paths()
    all_errors.extend(path_errors)
    
    # Валидация торговых параметров
    trading_errors = validate_trading_parameters()
    all_errors.extend(trading_errors)
    
    if all_errors:
        print("❌ Configuration validation failed:")
        for error in all_errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("✅ Configuration validation passed!")
        print(f"Environment: {Config.ENVIRONMENT}")
        print(f"Log Level: {Config.LOG_LEVEL}")
        print(f"Trading Symbol: {Config.SYMBOL}")
        print(f"Timeframe: {Config.TIMEFRAME}")

if __name__ == "__main__":
    main()
```

### Использование

```bash
# Валидация конфигурации
python scripts/validate_config.py

# Валидация в Docker
docker run --env-file .env crypto-trading-bot python scripts/validate_config.py

# Валидация в CI/CD
pytest tests/test_config_validation.py
```

## 🔄 Автоматическая Настройка

### Скрипт Инициализации

```bash
#!/bin/bash
# scripts/setup_environment.sh

set -e

echo "🚀 Setting up Crypto Trading Bot environment..."

# Создание необходимых директорий
mkdir -p data processed_data logs models charts

# Создание .env файла из шаблона
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Created .env file from template"
    else
        echo "⚠️  .env.example not found, creating basic .env file"
        cat > .env << EOF
ENVIRONMENT=development
LOG_LEVEL=INFO
SYMBOL=BTCUSDT
TIMEFRAME=1h
MAX_POSITION_SIZE=100
STOP_LOSS_PERCENT=2.0
TAKE_PROFIT_PERCENT=5.0
EOF
    fi
fi

# Генерация секретных ключей
if ! grep -q "JWT_SECRET=" .env || [ "$(grep JWT_SECRET= .env | cut -d= -f2)" = "your_jwt_secret_key_here" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
    echo "🔑 Generated JWT_SECRET"
fi

if ! grep -q "ENCRYPTION_KEY=" .env || [ "$(grep ENCRYPTION_KEY= .env | cut -d= -f2)" = "your_encryption_key_here" ]; then
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
    echo "🔑 Generated ENCRYPTION_KEY"
fi

# Установка правильных прав доступа
chmod 600 .env
chmod +x scripts/*.sh

# Валидация конфигурации
echo "🔍 Validating configuration..."
python scripts/validate_config.py

echo "✅ Environment setup completed!"
echo "📝 Please edit .env file with your API credentials"
echo "🚀 Run 'docker-compose up' to start the application"
```

```bash
# Запуск скрипта настройки
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

<function_calls>
<invoke name="todo_list">
<parameter name="todos">[{"content": "Create comprehensive deployment documentation", "id": "13", "priority": "high", "status": "completed"}, {"content": "Document Docker environment setup", "id": "14", "priority": "high", "status": "completed"}, {"content": "Create cloud deployment guide", "id": "15", "priority": "high", "status": "completed"}, {"content": "Document environment variables and secrets", "id": "16", "priority": "high", "status": "completed"}, {"content": "Create development setup guide", "id": "17", "priority": "medium", "status": "in_progress"}, {"content": "Document CI/CD pipeline configuration", "id": "18", "priority": "medium", "status": "pending"}]
