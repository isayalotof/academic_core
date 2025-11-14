# University Management System - MAX Mini-App

  

Комплексная система управления университетом с мини-приложением для мессенджера MAX. Включает автоматическое составление расписания, управление аудиториями, учебными процессами, тикетами и другими сервисами университета.

  

## 📋 Содержание

  

- [Обзор](#обзор)

- [Архитектура](#архитектура)

- [Основные возможности](#основные-возможности)

- [Быстрый старт](#быстрый-старт)

- [Микросервисы](#микросервисы)

- [API](#api)

- [Разработка](#разработка)

- [Мониторинг](#мониторинг)

- [Деплой](#деплой)

  

## 🎯 Обзор

  

Система представляет собой полнофункциональную платформу для управления университетом, состоящую из:

  

- **Backend**: Микросервисная архитектура на Python с gRPC

- **Frontend**: React + TypeScript мини-приложение для MAX

- **Bot**: Telegram/MAX бот для запуска мини-приложения

- **Infrastructure**: PostgreSQL, Redis, RabbitMQ, Prometheus, Grafana

  

### Основные функции

  

- 📅 **Автоматическое составление расписания** с учетом предпочтений преподавателей (LLM-агент на базе GigaChat)

- 🏫 **Управление аудиторным фондом** (здания, аудитории, бронирование)

- 👥 **Управление пользователями** (студенты, преподаватели, администраторы)

- 📚 **Учебная нагрузка** (дисциплины, группы, курсы)

- 🎫 **Система тикетов** для обращений и заявлений

- 📖 **LMS интеграция** (курсы, материалы)

- 📚 **Библиотека** (каталог, выдача книг)

- 🍽️ **Столовая** (меню, заказы)

- 📄 **Документооборот**

- 🎉 **События университета**

  

## 🏗️ Архитектура

  

### Микросервисы

  

```

┌─────────────┐

│   Frontend  │  React + TypeScript (MAX Mini-App)

│  (Nginx)    │

└──────┬──────┘

       │

┌──────▼──────┐

│   Gateway   │  FastAPI REST API Gateway

│  (FastAPI)  │

└──────┬──────┘

       │

   ┌───┴───┬──────────┬──────────┬──────────┬──────────┐

   │       │          │          │          │          │

┌──▼──┐ ┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐

│Auth │ │Core │  │Audit  │  │Schedule│  │Agent  │  │ ...   │

│gRPC │ │gRPC │  │gRPC   │  │gRPC    │  │gRPC   │  │gRPC   │

└─────┘ └─────┘  └───────┘  └────────┘  └───────┘  └───────┘

```

  

#### Список микросервисов

  

| Сервис | Порт | Описание |

|--------|------|----------|

| **ms-auth** | 50052 | Аутентификация и авторизация (JWT) |

| **ms-core** | 50054 | Базовые сущности (преподаватели, группы, студенты, нагрузки) |

| **ms-audit** | 50051 | Управление аудиториями и зданиями |

| **ms-schedule** | 50055 | Управление расписанием |

| **ms-agent** | 50053 | LLM-агент для автоматического составления расписания (GigaChat) |

| **ms-lms** | 50061 | Learning Management System |

| **ms-tickets** | 50056 | Система тикетов и обращений |

| **ms-events** | 50057 | События университета |

| **ms-library** | 50058 | Библиотека |

| **ms-documents** | 50059 | Документооборот |

| **ms-cafeteria** | 50060 | Столовая |

  

### Инфраструктура

  

- **PostgreSQL 15** - основная база данных

- **Redis 7** - кэширование

- **RabbitMQ 3.12** - очереди сообщений

- **Prometheus** - сбор метрик

- **Grafana** - визуализация метрик

- **Nginx** - reverse proxy и статика

  

## 🚀 Быстрый старт

  

### Требования

  

- Docker 20.10+

- Docker Compose 2.0+

- Python 3.11+ (для локальной разработки)

- Node.js 18+ (для разработки фронтенда)

  

### 1. Клонирование репозитория

  

```bash

git clone https://github.com/isayalotof/academic_core

cd academic_core

```

  

### 2. Настройка переменных окружения

  
  

Скопируйте `env.template` в файл `.env` в корне проекта и заполните все необходимые значения

  

```bash

cp env.template .env

  

nano .env

```

  
  

### 4. Запуск системы

  

```bash

# Запуск всех сервисов

docker-compose up --build

  

# Или в фоновом режиме

docker-compose up -d --build

```

  

### 5. Проверка работоспособности

  

```bash

# Gateway API

curl http://localhost:8000/health

  

# Frontend

open http://localhost

  

# API документация

open http://localhost:8000/docs

  

# Prometheus

open http://localhost:9090

  

# Grafana

open http://localhost:3000

# Login: admin / Password: admin

  

# RabbitMQ Management

open http://localhost:15672

# Login: university_user / Password: rabbitmq_pass_secure_2024

```

  

## 📦 Микросервисы

  

### ms-auth (Аутентификация)

  

**Порт**: 50052

  

Управление пользователями, ролями и JWT токенами.

  

**Роли**:

- `student` - Студент

- `teacher` - Преподаватель

- `staff` - Сотрудник учебного отдела

- `admin` - Администратор

  

**Особенности**:

- JWT access/refresh токены

- Защита от брутфорса (блокировка после N попыток)

- Хеширование паролей (bcrypt)

- Redis для хранения сессий

  

### ms-core (Базовые сущности)

  

**Порт**: 50054

  

Управление преподавателями, группами, студентами, дисциплинами и учебной нагрузкой.

  

**Основные функции**:

- CRUD операции для преподавателей, групп, студентов

- Управление учебной нагрузкой (загрузка из Excel)

- Предпочтения преподавателей для составления расписания

- Поиск и фильтрация

  

### ms-audit (Аудитории)

  

**Порт**: 50051

  

Управление аудиторным фондом университета.

  

**Функции**:

- Управление зданиями и аудиториями

- Поиск свободных аудиторий

- Бронирование аудиторий

- Расписание занятости аудиторий

- Кэширование расстояний между аудиториями

  

### ms-schedule (Расписание)

  

**Порт**: 50055

  

Управление расписанием занятий.

  

**Функции**:

- Просмотр расписания для групп, преподавателей, аудиторий

- Генерация расписания (через ms-agent)

- Экспорт в Excel, PDF, iCal

- Фильтрация по датам, группам, преподавателям

  

### ms-agent (LLM-агент)

  

**Порт**: 50053

  

Интеллектуальный агент для автоматического составления расписания на базе GigaChat.

  

**Функции**:

- Анализ учебной нагрузки

- Учет предпочтений преподавателей

- Оптимизация распределения аудиторий

- Генерация расписания с учетом ограничений

  

**Требования**:

- GigaChat API credentials (CLIENT_ID, CLIENT_SECRET)

  

### ms-lms (Learning Management System)

  

**Порт**: 50061

  

Интеграция с системой управления обучением.

  

**Функции**:

- Управление курсами

- Материалы для обучения

- Прогресс студентов

  

### ms-tickets (Тикеты)

  

**Порт**: 50056

  

Система обращений и заявлений.

  

**Функции**:

- Создание тикетов

- Назначение ответственных

- Статусы и приоритеты

- История изменений

  

### ms-events (События)

  

**Порт**: 50057

  

Управление событиями университета.

  

**Функции**:

- Создание и управление событиями

- Календарь событий

- Уведомления

  

### ms-library (Библиотека)

  

**Порт**: 50058

  

Управление библиотечным фондом.

  

**Функции**:

- Каталог книг

- Выдача и возврат

- Бронирование

  

### ms-documents (Документы)

  

**Порт**: 50059

  

Документооборот.

  

**Функции**:

- Хранение документов

- Версионирование

- Поиск

  

### ms-cafeteria (Столовая)

  

**Порт**: 50060

  

Управление столовой.

  

**Функции**:

- Меню

- Заказы

- Бронирование столов

  

## 📡 API

  

### Gateway (REST API)

  

**Base URL**: `http://localhost:8000/api`

  

#### Аутентификация

  

```http

POST /api/auth/register

POST /api/auth/login

POST /api/auth/refresh

POST /api/auth/logout

GET  /api/auth/me

```

  

#### Преподаватели

  

```http

GET    /api/teachers

POST   /api/teachers

GET    /api/teachers/{id}

PUT    /api/teachers/{id}

DELETE /api/teachers/{id}

GET    /api/teachers/{id}/preferences

POST   /api/teachers/{id}/preferences

```

  

#### Группы

  

```http

GET    /api/groups

POST   /api/groups

GET    /api/groups/{id}

PUT    /api/groups/{id}

DELETE /api/groups/{id}

```

  

#### Студенты

  

```http

GET    /api/students

POST   /api/students

GET    /api/students/{id}

PUT    /api/students/{id}

DELETE /api/students/{id}

```

  

#### Аудитории

  

```http

GET    /api/classrooms

POST   /api/classrooms

GET    /api/classrooms/{id}

PUT    /api/classrooms/{id}

DELETE /api/classrooms/{id}

GET    /api/classrooms/available

POST   /api/classrooms/reserve

GET    /api/classrooms/{id}/schedule

```

  

#### Расписание

  

```http

GET    /api/schedule/group/{groupId}

GET    /api/schedule/teacher/{teacherId}

GET    /api/schedule/classroom/{classroomId}

POST   /api/schedule/generate

GET    /api/schedule/export

```

  

#### Тикеты

  

```http

GET    /api/tickets

POST   /api/tickets

GET    /api/tickets/{id}

PUT    /api/tickets/{id}

POST   /api/tickets/{id}/comment

```

  

Полная документация доступна по адресу: `http://localhost:8000/docs`

  

### gRPC API

  

Все микросервисы используют gRPC для межсервисного взаимодействия. Спецификации находятся в папках `*/proto/*.proto`.

  

## 🔧 Разработка

  

### Структура проекта

  

```

max-miniapp/

├── bot/                    # Telegram/MAX бот

├── frontend/               # React фронтенд

│   ├── src/

│   │   ├── components/    # Компоненты

│   │   ├── pages/         # Страницы

│   │   ├── services/      # API клиенты

│   │   └── store/         # Zustand stores

│   └── package.json

├── gateway/                # API Gateway (FastAPI)

│   ├── routes/            # REST endpoints

│   ├── rpc_clients/       # gRPC клиенты

│   └── middleware/        # Middleware

├── ms-*/                   # Микросервисы

│   ├── proto/             # gRPC спецификации

│   ├── db/                # База данных

│   ├── rpc/               # gRPC серверы

│   ├── services/          # Бизнес-логика

│   └── utils/             # Утилиты

├── monitoring/             # Prometheus & Grafana

├── nginx/                  # Nginx конфигурация

├── scripts/                # Вспомогательные скрипты

└── compose.yaml            # Docker Compose

```

  
  
  

#### Frontend

  

```bash

cd frontend

  

# Установка зависимостей

npm install

  

# Сборка

npm run build

  

# Запуск dev сервера

npm run dev

  
  

```

  
  

### Миграции базы данных

  

```bash

# Применить все миграции

./scripts/run_migrations.sh

  

# Или вручную для конкретного сервиса

cd ms-core

python db/migrations/migrate.py

```

  

### Генерация gRPC кода

  

```bash

# Все сервисы

./scripts/generate_proto.sh

  

# Конкретный сервис

./scripts/generate_proto_auth.sh

```

  

## 📊 Мониторинг

  

### Prometheus

  

**URL**: http://localhost:9090

  

Собирает метрики со всех микросервисов:

- Количество запросов

- Время отклика

- Ошибки

- Использование ресурсов

  

### Grafana

  

**URL**: http://localhost:3000  

**Login**: `admin` / `admin`

  

Готовые дашборды для визуализации метрик:

- Обзор системы

- Метрики микросервисов

- Метрики базы данных

- Метрики Redis и RabbitMQ

  
  

### Логи

  

```bash

# Логи всех сервисов

docker-compose logs -f

  

# Логи конкретного сервиса

docker-compose logs -f gateway

docker-compose logs -f ms-core

```

  

## 🚢 Деплой

  

### Production настройки

  

1. **Измените все пароли** в `.env`

2. **Настройте JWT_SECRET_KEY** (используйте длинную случайную строку)

3. **Настройте CORS** в `gateway/config.py`

4. **Включите TLS/SSL** для gRPC (опционально)

5. **Настройте резервное копирование** PostgreSQL

  

### Docker Compose

  

```bash

# Production сборка

docker-compose -f compose.yaml up -d --build

  

# Проверка статуса

docker-compose ps

  

# Остановка

docker-compose down

```

  

### Отдельные сервисы

  

Каждый сервис может быть развернут независимо. См. `*/Dockerfile` для деталей.

  

## 🔒 Безопасность

  

- ✅ JWT аутентификация

- ✅ Хеширование паролей (bcrypt)

- ✅ Защита от брутфорса

- ✅ CORS настройки

- ✅ Валидация входных данных

- ✅ SQL injection защита (параметризованные запросы)