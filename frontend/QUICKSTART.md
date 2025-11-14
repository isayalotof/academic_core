# Быстрый старт

## Локальная разработка

1. Установите зависимости:
```bash
cd frontend
npm install
```

2. Создайте файл `.env`:
```bash
cp env.example .env
```

3. Отредактируйте `.env` и укажите URL вашего API:
```env
VITE_API_URL=http://localhost:8000
VITE_MAX_BOT_TOKEN=your_bot_token_here
```

4. Запустите dev-сервер:
```bash
npm run dev
```

Приложение будет доступно по адресу http://localhost:3000

## Docker

### Сборка и запуск через Docker Compose

```bash
# Из корневой директории проекта
docker-compose -f compose-frontend.yaml up --build
```

### Только фронтенд

```bash
cd frontend
docker build -t university-frontend .
docker run -p 3000:80 university-frontend
```

## Структура

- **Студенты**: `/` - главная страница с расписанием, `/menu` - дополнительное меню
- **Преподаватели**: `/` - расписание, `/preferences` - временные предпочтения, `/report-issue/:id` - сообщение о проблеме
- **Администраторы**: `/` - панель управления, `/teachers/create` - создание преподавателя

## Примечания

- Приложение оптимизировано для мобильных устройств
- Использует MAX UI компоненты для соответствия дизайн-системе MAX
- Все API запросы идут через Gateway на `http://localhost:8000` (или указанный в `.env`)

