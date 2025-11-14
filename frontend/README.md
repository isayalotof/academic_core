# University Schedule Frontend

Фронтенд для мини-приложения расписания университета в мессенджере MAX.

## Технологии

- React 18
- TypeScript
- Vite
- MAX UI (@maxhub/max-ui)
- React Router
- Zustand (state management)
- Axios (HTTP client)
- date-fns (работа с датами)

## Установка

```bash
npm install
```

## Разработка

```bash
npm run dev
```

Приложение будет доступно по адресу http://localhost:3000

## Сборка

```bash
npm run build
```

## Структура проекта

```
frontend/
├── src/
│   ├── components/      # Переиспользуемые компоненты
│   ├── pages/          # Страницы приложения
│   ├── services/       # API сервисы
│   ├── store/          # Zustand stores
│   ├── hooks/          # React hooks
│   ├── App.tsx         # Главный компонент
│   └── main.tsx        # Точка входа
├── public/             # Статические файлы
├── index.html          # HTML шаблон
└── vite.config.ts      # Конфигурация Vite
```

## Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```env
VITE_API_URL=http://localhost:8000
VITE_MAX_BOT_TOKEN=your_bot_token_here
```

## Роли пользователей

### Студент
- Просмотр расписания группы
- Навигация по дням (вчера/сегодня/завтра)
- Доступ к меню с дополнительными услугами

### Преподаватель
- Просмотр своего расписания
- Установка временных предпочтений
- Сообщение о неисправностях в аудиториях

### Администратор
- Просмотр статистики
- Создание преподавателей
- Управление расписанием

## Интеграция с MAX

Приложение использует MAX Bridge SDK для взаимодействия с платформой MAX:

- `window.WebApp` - основной объект для работы с MAX API
- `window.WebApp.ready()` - уведомление о готовности приложения
- `window.WebApp.initDataUnsafe` - данные пользователя из MAX

## Деплой

Приложение собирается в статические файлы и может быть размещено на любом хостинге:

- Vercel
- GitHub Pages
- Nginx
- Docker (см. Dockerfile)

## Docker

```bash
# Сборка образа
docker build -t university-frontend ./frontend

# Запуск
docker run -p 3000:80 university-frontend
```

Или используйте `compose-frontend.yaml`:

```bash
docker-compose -f compose-frontend.yaml up --build
```

