# SSL Сертификаты

## Использование Let's Encrypt сертификатов

Проект настроен на использование Let's Encrypt сертификатов через certbot.

Сертификаты монтируются из `/etc/letsencrypt/live/max.isayalot.ru/`:
- `fullchain.pem` - полная цепочка сертификатов
- `privkey.pem` - приватный ключ

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

