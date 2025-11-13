# 📊 Мониторинг системы University Schedule

Настройка мониторинга через **Prometheus** и **Grafana**.

---

## 🚀 Быстрый старт

### 1. Запуск мониторинга

```bash
# Запустить все сервисы включая мониторинг
docker-compose up -d

# Или только мониторинг
docker-compose up -d prometheus grafana
```

### 2. Доступ к интерфейсам

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - **Логин**: `admin`
  - **Пароль**: `admin` (или значение из `.env`: `GRAFANA_ADMIN_PASSWORD`)

---

## 📈 Prometheus

### Конфигурация

Конфигурационный файл: `monitoring/prometheus.yml`

### Что мониторится:

#### **Microservices** (каждые 10 секунд)
- ✅ **gateway** - API Gateway (`:8000/metrics`)
- ✅ **ms-auth** - Authentication (`:8001/metrics`)
- ✅ **ms-audit** - Classroom Management (`:8001/metrics`)
- ✅ **ms-agent** - LLM Schedule Generator (`:8001/metrics`)
- ✅ **ms-core** - Core Entities (`:8001/metrics`)
- ✅ **ms-schedule** - Schedule Management (`:8001/metrics`)

#### **Infrastructure** (каждые 15-30 секунд)
- 🐘 **postgres** - PostgreSQL Database
- 🐰 **rabbitmq** - Message Broker (`:15692/metrics`)
- 📦 **redis** - Cache
- 📊 **prometheus** - Self-monitoring

### Проверка целей

Откройте Prometheus UI: http://localhost:9090/targets

Все targets должны быть в состоянии **UP** (зеленые).

---

## 📊 Grafana

### Автоматическая настройка

При запуске Grafana автоматически:
1. ✅ Подключается к Prometheus как data source
2. ✅ Загружает готовые дашборды
3. ✅ Применяет конфигурацию

### Готовые Dashboard'ы

#### **University Schedule System - Overview**

**Панели:**

1. **Total Gateway Requests** - общее количество запросов к Gateway
2. **Gateway Uptime** - время работы Gateway
3. **Gateway Request Rate** - частота запросов (req/s)
4. **Services Health Status** - статус всех микросервисов
5. **RabbitMQ Message Rate** - скорость обработки сообщений
6. **Scrape Duration** - время сбора метрик

**Доступ**: http://localhost:3000/d/university-schedule-overview

---

## 🔧 Доступные метрики

### Gateway

```promql
# Общее количество запросов
gateway_requests_total

# Время работы Gateway (секунды)
gateway_uptime_seconds

# Информация о версии
gateway_info{version="1.0.0",environment="production"}
```

### MS-Audit (Classroom Management)

```promql
# HTTP запросы
http_requests_total{service="ms-audit"}

# Время обработки запросов
http_request_duration_seconds{service="ms-audit"}

# Подключения к БД
db_connections_active{service="ms-audit"}
```

### RabbitMQ

```promql
# Опубликованные сообщения
rabbitmq_messages_published_total

# Доставленные сообщения
rabbitmq_messages_delivered_total

# Сообщения в очереди
rabbitmq_queue_messages
```

---

## 📝 Создание собственных Dashboard'ов

### 1. Через UI

1. Зайдите в Grafana: http://localhost:3000
2. Нажмите **+** → **Dashboard** → **Add new panel**
3. Выберите **Prometheus** как data source
4. Введите PromQL запрос
5. Настройте визуализацию
6. Сохраните dashboard

### 2. Экспорт/Импорт

```bash
# Экспортировать dashboard
curl http://admin:admin@localhost:3000/api/dashboards/uid/university-schedule-overview \
  > my-dashboard.json

# Импортировать dashboard
# Settings → Dashboards → Import → Upload JSON file
```

---

## 🎯 Полезные PromQL запросы

### Частота запросов к Gateway

```promql
rate(gateway_requests_total[1m])
```

### Время работы всех сервисов

```promql
up{job=~"gateway|ms-.*"}
```

### Количество активных подключений к PostgreSQL

```promql
pg_stat_activity_count
```

### Средняя задержка запросов к ms-audit

```promql
rate(http_request_duration_seconds_sum{service="ms-audit"}[5m]) 
/ 
rate(http_request_duration_seconds_count{service="ms-audit"}[5m])
```

---

## 🚨 Алертинг (опционально)

### Настройка Alertmanager

1. Создайте конфигурацию `monitoring/alertmanager.yml`
2. Добавьте правила в `monitoring/alert_rules.yml`
3. Обновите `compose.yaml` для запуска Alertmanager

### Пример правила

```yaml
# monitoring/alert_rules.yml
groups:
  - name: gateway_alerts
    interval: 30s
    rules:
      - alert: GatewayDown
        expr: up{job="gateway"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Gateway is down"
          description: "Gateway has been down for more than 1 minute"
```

---

## 🔍 Troubleshooting

### Prometheus не видит targets

1. Проверьте, что сервисы запущены: `docker-compose ps`
2. Проверьте логи: `docker-compose logs prometheus`
3. Проверьте конфигурацию: http://localhost:9090/config

### Grafana не показывает данные

1. Проверьте data source: **Configuration** → **Data Sources** → **Prometheus**
2. Проверьте, что Prometheus работает: http://localhost:9090
3. Проверьте Time Range в dashboard (правый верхний угол)

### Метрики не обновляются

1. Проверьте scrape interval в `prometheus.yml`
2. Проверьте эндпоинты метрик:
   ```bash
   curl http://localhost:8000/metrics  # Gateway
   curl http://localhost:15692/metrics # RabbitMQ
   ```

---

## 📚 Дополнительная информация

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **PromQL Tutorial**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Dashboard Best Practices**: https://grafana.com/docs/grafana/latest/dashboards/

---

## 🎨 Кастомизация

### Изменить интервал сбора метрик

Отредактируйте `monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'gateway'
    scrape_interval: 5s  # Было: 10s
```

### Добавить новый dashboard

1. Создайте JSON файл в `monitoring/grafana/dashboards/`
2. Перезапустите Grafana: `docker-compose restart grafana`

### Изменить retention period

Добавьте в `compose.yaml`:

```yaml
prometheus:
  command:
    - '--storage.tsdb.retention.time=30d'  # Хранить 30 дней
```

---

## 📊 Структура каталогов

```
monitoring/
├── prometheus.yml                          # Prometheus конфигурация
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml             # Автоконфигурация источника данных
│   │   └── dashboards/
│   │       └── default.yml                 # Автозагрузка дашбордов
│   └── dashboards/
│       └── university-schedule-overview.json  # Главный дашборд
└── README.md                               # Эта документация
```

---

✅ **Готово!** Мониторинг настроен и работает. Откройте http://localhost:3000 для просмотра метрик!

