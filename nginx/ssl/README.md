# SSL Сертификаты

## Текущая конфигурация

По умолчанию nginx настроен для работы **без SSL** (HTTP только). Это позволяет запустить проект без необходимости получения сертификатов.

## Включение SSL

Для включения SSL необходимо:

1. **Получить сертификаты Let's Encrypt** (см. раздел ниже)
2. **Раскомментировать HTTPS блок** в `nginx/nginx.conf`
3. **Раскомментировать редирект на HTTPS** в HTTP блоке
4. **Перезапустить nginx**

## Использование Let's Encrypt сертификатов

Проект настроен на использование Let's Encrypt сертификатов через certbot.

Сертификаты монтируются из `/etc/letsencrypt/live/max.isayalot.ru/`:
- `fullchain.pem` - полная цепочка сертификатов
- `privkey.pem` - приватный ключ

### Получение сертификатов

Для получения сертификатов через certbot:

```bash
# Установите certbot (если еще не установлен)
sudo apt-get update
sudo apt-get install certbot

# Получите сертификат (замените email на ваш)
sudo certbot certonly --standalone -d max.isayalot.ru --email your-email@example.com --agree-tos --non-interactive
```

**Важно:** Для получения сертификатов через standalone режим nginx должен быть остановлен, так как certbot использует порт 80.

## Обновление сертификатов

Let's Encrypt сертификаты действительны 90 дней. Для автоматического обновления:

1. Установите cron задачу для обновления:
```bash
sudo crontab -e
# Добавьте строку:
0 0 * * * certbot renew --quiet && docker-compose restart nginx
```

2. Или используйте systemd timer (если доступен):
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Проверка сертификатов

Проверить статус сертификатов:
```bash
sudo certbot certificates
```

## Если нужно использовать другие сертификаты

Если у вас другие сертификаты, обновите `nginx.conf` и `compose.yaml`:

1. В `nginx.conf` измените пути к сертификатам
2. В `compose.yaml` измените volume монтирование

## Перезапуск nginx

После изменений перезапустите nginx:

```bash
docker-compose restart nginx
```

Или пересоберите:

```bash
docker-compose up -d --build nginx
```

