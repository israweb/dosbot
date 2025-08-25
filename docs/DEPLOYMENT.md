# Руководство по Развертыванию

Это руководство описывает различные способы развертывания Crypto Trading Bot в различных окружениях.

## 📋 Содержание

- [Требования к Системе](#требования-к-системе)
- [Локальное Развертывание](#локальное-развертывание)
- [Docker Развертывание](#docker-развертывание)
- [Облачное Развертывание](#облачное-развертывание)
- [Конфигурация Окружения](#конфигурация-окружения)
- [Мониторинг и Логирование](#мониторинг-и-логирование)

## 🖥️ Требования к Системе

### Минимальные Требования
- **CPU**: 2+ ядра
- **RAM**: 4GB+
- **Диск**: 10GB+ свободного места
- **ОС**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+

### Рекомендуемые Требования
- **CPU**: 4+ ядра
- **RAM**: 8GB+
- **Диск**: 50GB+ SSD
- **Сеть**: Стабильное интернет-соединение

### Программное Обеспечение
- Python 3.9+
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

## 🏠 Локальное Развертывание

### 1. Подготовка Окружения

```bash
# Клонирование репозитория
git clone https://github.com/israweb/dosbot.git
cd crypto-trading-bot

# Создание виртуального окружения
python -m venv .venv

# Активация (Linux/Mac)
source .venv/bin/activate

# Активация (Windows)
.venv\Scripts\activate

# Обновление pip
python -m pip install --upgrade pip
```

### 2. Установка Зависимостей

```bash
# Установка основных зависимостей
pip install -r requirements.txt

# Установка зависимостей для разработки (опционально)
pip install -r requirements-dev.txt
```

### 3. Конфигурация

```bash
# Создание файла окружения
cp .env.example .env

# Редактирование конфигурации
nano .env  # или любой другой редактор
```

### 4. Запуск

```bash
# Проверка конфигурации
python -c "from src.config import Config; print('Config OK')"

# Запуск тестов
pytest tests/ -v

# Запуск приложения
python src/main.py
```

## 🐳 Docker Развертывание

### 1. Быстрый Запуск

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f
```

### 2. Отдельные Сервисы

```bash
# Только основное приложение
docker-compose up app

# С базой данных
docker-compose up app postgres

# Полная инфраструктура
docker-compose up
```

### 3. Управление

```bash
# Остановка сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart app

# Просмотр статуса
docker-compose ps
```

### 4. Масштабирование

```bash
# Запуск нескольких экземпляров приложения
docker-compose up --scale app=3

# Балансировка нагрузки через nginx
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## ☁️ Облачное Развертывание

### AWS ECS

#### 1. Подготовка

```bash
# Установка AWS CLI
pip install awscli

# Конфигурация
aws configure

# Создание ECR репозитория
aws ecr create-repository --repository-name crypto-trading-bot
```

#### 2. Сборка и Публикация Образа

```bash
# Получение токена для Docker
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Сборка образа
docker build -t crypto-trading-bot .

# Тегирование
docker tag crypto-trading-bot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-trading-bot:latest

# Публикация
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-trading-bot:latest
```

#### 3. Развертывание ECS

```bash
# Создание кластера
aws ecs create-cluster --cluster-name crypto-trading-cluster

# Создание task definition (см. aws/task-definition.json)
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json

# Создание сервиса
aws ecs create-service --cluster crypto-trading-cluster --service-name crypto-trading-service --task-definition crypto-trading-bot --desired-count 1
```

### Google Cloud Run

#### 1. Подготовка

```bash
# Установка gcloud CLI
# Следуйте инструкциям: https://cloud.google.com/sdk/docs/install

# Аутентификация
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Включение необходимых API
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 2. Развертывание

```bash
# Сборка и развертывание одной командой
gcloud run deploy crypto-trading-bot \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "$(cat .env | tr '\n' ',')"
```

### Azure Container Instances

#### 1. Подготовка

```bash
# Установка Azure CLI
# Следуйте инструкциям: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Аутентификация
az login

# Создание группы ресурсов
az group create --name crypto-trading-rg --location eastus

# Создание Container Registry
az acr create --resource-group crypto-trading-rg --name cryptotradingacr --sku Basic
```

#### 2. Развертывание

```bash
# Сборка и публикация образа
az acr build --registry cryptotradingacr --image crypto-trading-bot .

# Создание container instance
az container create \
    --resource-group crypto-trading-rg \
    --name crypto-trading-bot \
    --image cryptotradingacr.azurecr.io/crypto-trading-bot:latest \
    --cpu 2 \
    --memory 4 \
    --registry-login-server cryptotradingacr.azurecr.io \
    --registry-username cryptotradingacr \
    --registry-password $(az acr credential show --name cryptotradingacr --query "passwords[0].value" -o tsv) \
    --environment-variables $(cat .env)
```

### Kubernetes

#### 1. Подготовка Манифестов

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: crypto-trading

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: crypto-trading-config
  namespace: crypto-trading
data:
  # Не секретные конфигурации
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: crypto-trading-secrets
  namespace: crypto-trading
type: Opaque
data:
  # Base64 encoded секреты
  API_KEY: <base64-encoded-api-key>
  API_SECRET: <base64-encoded-api-secret>

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-trading-bot
  namespace: crypto-trading
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crypto-trading-bot
  template:
    metadata:
      labels:
        app: crypto-trading-bot
    spec:
      containers:
      - name: crypto-trading-bot
        image: your-registry/crypto-trading-bot:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: crypto-trading-config
        - secretRef:
            name: crypto-trading-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 2. Развертывание

```bash
# Применение манифестов
kubectl apply -f k8s/

# Проверка статуса
kubectl get pods -n crypto-trading
kubectl get services -n crypto-trading

# Просмотр логов
kubectl logs -f deployment/crypto-trading-bot -n crypto-trading
```

## 🔧 Конфигурация Окружения

### Переменные Окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# API Configuration
API_KEY=your_exchange_api_key
API_SECRET=your_exchange_api_secret
BASE_URL=https://api.binance.com

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_trading
REDIS_URL=redis://localhost:6379/0

# Trading Configuration
SYMBOL=BTCUSDT
TIMEFRAME=1h
MAX_POSITION_SIZE=1000
STOP_LOSS_PERCENT=2.0
TAKE_PROFIT_PERCENT=5.0

# ML Configuration
MODEL_UPDATE_INTERVAL=3600
FEATURE_WINDOW=100
PREDICTION_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
```

### Секреты в Облаке

#### AWS Secrets Manager

```bash
# Создание секрета
aws secretsmanager create-secret \
    --name crypto-trading-bot/prod \
    --description "Production secrets for crypto trading bot" \
    --secret-string file://secrets.json
```

#### Google Secret Manager

```bash
# Создание секрета
gcloud secrets create crypto-trading-api-key --data-file=api_key.txt
gcloud secrets create crypto-trading-api-secret --data-file=api_secret.txt
```

#### Azure Key Vault

```bash
# Создание Key Vault
az keyvault create --name crypto-trading-kv --resource-group crypto-trading-rg --location eastus

# Добавление секретов
az keyvault secret set --vault-name crypto-trading-kv --name api-key --value "your-api-key"
az keyvault secret set --vault-name crypto-trading-kv --name api-secret --value "your-api-secret"
```

## 📊 Мониторинг и Логирование

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

### ELK Stack

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logging/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

## 🔍 Troubleshooting

### Общие Проблемы

1. **Проблемы с зависимостями**
```bash
# Очистка кэша pip
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

2. **Проблемы с Docker**
```bash
# Очистка Docker
docker system prune -a
docker-compose down -v
docker-compose up --build
```

3. **Проблемы с правами доступа**
```bash
# Linux/Mac
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

### Логи и Диагностика

```bash
# Просмотр логов приложения
tail -f logs/trading.log

# Docker логи
docker-compose logs -f app

# Kubernetes логи
kubectl logs -f deployment/crypto-trading-bot -n crypto-trading

# Системные ресурсы
htop
docker stats
kubectl top pods -n crypto-trading
```

## 🔄 Обновление и Откат

### Rolling Update

```bash
# Docker Compose
docker-compose pull
docker-compose up -d

# Kubernetes
kubectl set image deployment/crypto-trading-bot crypto-trading-bot=your-registry/crypto-trading-bot:v2.0.0 -n crypto-trading
kubectl rollout status deployment/crypto-trading-bot -n crypto-trading
```

### Откат

```bash
# Kubernetes
kubectl rollout undo deployment/crypto-trading-bot -n crypto-trading

# Docker Compose
docker-compose down
git checkout previous-version
docker-compose up --build
```

## 📞 Поддержка

Для получения помощи:
1. Проверьте [FAQ](FAQ.md)
2. Создайте [Issue](https://github.com/israweb/dosbot/issues)
3. Обратитесь к [документации API](API.md)
