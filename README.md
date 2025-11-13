# University Schedule - Classroom Management Microservice

Production-ready микросервис для управления аудиторным фондом университета.

## 🏗️ Архитектура

- **ms-audit**: gRPC микросервис управления аудиториями (Python)
- **gateway**: FastAPI API Gateway для REST API
- **PostgreSQL**: База данных (без ORM)
- **Redis**: Кэширование
- **RabbitMQ**: Очереди сообщений
- **Prometheus**: Метрики
- **Grafana**: Визуализация метрик

## 🚀 Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (для разработки)

### Запуск инфраструктуры

```bash
# Клонировать репозиторий
git clone <repository-url>
cd university-schedule

# Сгенерировать gRPC код (если нужно)
cd ms-audit
python -m grpc_tools.protoc -I./proto --python_out=./proto/generated --grpc_python_out=./proto/generated --pyi_out=./proto/generated ./proto/classroom.proto
cd ..

# Запустить все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### Проверка работоспособности

```bash
# PostgreSQL
docker exec -it university-postgres psql -U university_user -d university_db -c "SELECT 1;"

# Redis
docker exec -it university-redis redis-cli -a redis_pass_secure_2024 PING

# Gateway API
curl http://localhost:8000/health

# RabbitMQ Management UI
open http://localhost:15672
# Login: university_user / Password: rabbitmq_pass_secure_2024

# Grafana
open http://localhost:3000
# Login: admin / Password: admin

# Prometheus
open http://localhost:9090
```

## 📡 API Endpoints

### Gateway (HTTP REST)

**Base URL**: `http://localhost:8000`

#### Аудитории

- `POST /api/classrooms/` - Создать аудиторию
- `GET /api/classrooms/{id}` - Получить аудиторию
- `PUT /api/classrooms/{id}` - Обновить аудиторию
- `DELETE /api/classrooms/{id}` - Удалить аудиторию
- `GET /api/classrooms/` - Список аудиторий
- `GET /api/classrooms/available` - Найти свободные аудитории
- `POST /api/classrooms/reserve` - Забронировать аудиторию
- `GET /api/classrooms/{id}/schedule` - Расписание аудитории

### ms-audit (gRPC)

**Address**: `localhost:50051`

Методы описаны в `ms-audit/proto/classroom.proto`

## 📊 База данных

### Таблицы

- `buildings` - Здания университета
- `classrooms` - Аудитории
- `classroom_schedules` - Расписание занятости
- `classroom_distances` - Кэш расстояний между аудиториями

### Миграции

```bash
# Применить миграции вручную
cd ms-audit
python db/migrations/migrate.py
```

## 🔧 Разработка

### Структура проекта

```
university-schedule/
├── compose.yaml              # Docker Compose
├── ms-audit/                 # Микросервис аудиторий
│   ├── proto/               # gRPC спецификации
│   ├── db/                  # База данных
│   ├── rpc/                 # gRPC сервисы
│   ├── services/            # Бизнес-логика
│   └── utils/               # Утилиты
├── gateway/                  # API Gateway
│   ├── routes/              # REST endpoints
│   ├── rpc_clients/         # RPC клиенты
│   └── middleware/          # Middleware
└── monitoring/              # Конфигурация мониторинга
```

### Переменные окружения

Основные переменные настроены в `compose.yaml`. Для локальной разработки создайте `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=university_db
DB_USER=university_user
DB_PASSWORD=university_pass_secure_2024

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_pass_secure_2024

GRPC_PORT=50051
LOG_LEVEL=DEBUG
```

## 🔒 Безопасность

- JWT аутентификация через Gateway
- Роли: `admin`, `staff`, `teacher`, `student`
- Все пароли должны быть изменены в production
- TLS/SSL для gRPC в production (настроить отдельно)

## 📈 Мониторинг

### Метрики Prometheus

- `rpc_requests_total` - Всего RPC запросов
- `rpc_duration_seconds` - Длительность RPC запросов
- `classrooms_total` - Всего аудиторий
- `available_classrooms` - Доступные аудитории

### Логирование

Структурированные JSON логи во всех сервисах.

```bash
# Просмотр логов
docker-compose logs -f ms-audit
docker-compose logs -f gateway
```

## 🧪 Тестирование

```bash
# ms-audit
cd ms-audit
pytest tests/

# gateway
cd gateway
pytest tests/
```

## 📝 Лицензия

MIT License

## 👥 Команда

Разработано для системы автоматического составления расписания университета.

