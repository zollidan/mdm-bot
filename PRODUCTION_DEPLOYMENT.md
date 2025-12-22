# 🚀 Production Deployment Guide - MDM Bot Mini App

## Предварительные требования

### Обязательно

- ✅ Зарегистрированный домен (например, `mdm-store.com`)
- ✅ VPS/сервер с установленным Docker и Docker Compose
- ✅ SSL сертификат (Let's Encrypt рекомендуется)
- ✅ Telegram Bot Token
- ✅ Минимум 4GB RAM, 2 CPU cores

### Рекомендуется

- 📧 Email для уведомлений
- 🔐 SSH ключ для доступа к серверу
- 📊 Мониторинг (Prometheus/Grafana)
- 💾 Настроенные бэкапы

---

## 🔧 Шаг 1: Подготовка сервера

### 1.1 Обновление системы

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# Fedora/RHEL
sudo dnf update -y
```

### 1.2 Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Fedora
sudo dnf install docker docker-compose -y
sudo systemctl enable --now docker
```

### 1.3 Установка Docker Compose V2

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 1.4 Настройка файрвола

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Firewalld (Fedora)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

---

## 📦 Шаг 2: Развертывание приложения

### 2.1 Клонирование репозитория

```bash
cd /opt
sudo git clone https://github.com/your-username/mdm-bot.git
cd mdm-bot
sudo chown -R $USER:$USER .
```

### 2.2 Конфигурация .env файла

```bash
# Скопировать production шаблон
cp .env.production .env

# Редактировать .env
nano .env
```

**Обязательные настройки:**

```env
# Bot Token от @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# PostgreSQL (используйте СИЛЬНЫЕ пароли!)
POSTGRES_USER=postgres_prod
POSTGRES_PASSWORD=СГЕНЕРИРУЙТЕ_СЛУЧАЙНЫЙ_ПАРОЛЬ_32_СИМВОЛА
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mdm_bot_db

# MeiliSearch (минимум 16 символов)
MEILI_HOST=meilisearch
MEILI_PORT=7700
MEILI_MASTER_KEY=СГЕНЕРИРУЙТЕ_СЛУЧАЙНЫЙ_КЛЮЧ_32_СИМВОЛА
MEILI_ENV=production

# Mini App (ВАШ домен с HTTPS!)
WEBAPP_URL=https://mdm-store.com
ALLOWED_ORIGINS=https://mdm-store.com,https://web.telegram.org
```

**Генерация безопасных паролей:**

```bash
# PostgreSQL пароль
openssl rand -base64 32

# MeiliSearch ключ
openssl rand -base64 32
```

### 2.3 Установка SSL сертификата (Let's Encrypt)

```bash
# Установка certbot
sudo apt install certbot -y  # Ubuntu
sudo dnf install certbot -y  # Fedora

# Получение сертификата (перед запуском контейнеров)
sudo certbot certonly --standalone -d mdm-store.com -d www.mdm-store.com

# Сертификаты будут в:
# /etc/letsencrypt/live/mdm-store.com/fullchain.pem
# /etc/letsencrypt/live/mdm-store.com/privkey.pem
```

### 2.4 Настройка Nginx для SSL

```bash
# Скопировать SSL шаблон
cp webapp/nginx-ssl.conf.template webapp/nginx-ssl.conf

# Отредактировать конфигурацию
nano webapp/nginx-ssl.conf

# Заменить:
# - your-domain.com -> mdm-store.com
# - Пути к сертификатам
```

### 2.5 Обновление Dockerfile для SSL

Создайте `webapp/Dockerfile.prod`:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine

# Копируем SSL конфигурацию
COPY nginx-ssl.conf /etc/nginx/conf.d/default.conf

# Копируем приложение
COPY --from=builder /app/dist /usr/share/nginx/html

# Создаем директорию для SSL
RUN mkdir -p /etc/nginx/ssl

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

### 2.6 Монтирование SSL сертификатов

Обновите `docker-compose.prod.yaml`:

```yaml
webapp:
  build:
    context: ./webapp
    dockerfile: Dockerfile.prod  # Используем prod Dockerfile
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - /etc/letsencrypt/live/mdm-store.com/fullchain.pem:/etc/nginx/ssl/cert.pem:ro
    - /etc/letsencrypt/live/mdm-store.com/privkey.pem:/etc/nginx/ssl/key.pem:ro
  # ... остальная конфигурация
```

---

## 🚀 Шаг 3: Запуск приложения

### 3.1 Сборка образов

```bash
docker-compose -f docker-compose.prod.yaml build
```

### 3.2 Первый запуск

```bash
# Запуск всех сервисов
docker-compose -f docker-compose.prod.yaml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yaml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yaml logs -f
```

### 3.3 Импорт данных (если есть CSV)

```bash
# Скопировать CSV в контейнер
docker-compose -f docker-compose.prod.yaml exec bot bash

# Внутри контейнера
uv run convert.py
exit
```

### 3.4 Проверка работоспособности

```bash
# 1. API Health Check
curl https://mdm-store.com/api/health
# Ожидаемый ответ: {"status":"ok","service":"mdm-bot-api"}

# 2. Получение товаров
curl https://mdm-store.com/api/products?page=1&limit=5

# 3. Проверка Mini App
# Откройте бот в Telegram и нажмите "🛍️ Открыть каталог"
```

---

## 🔒 Шаг 4: Безопасность

### 4.1 Ограничение доступа к портам

```bash
# Проверьте, что эти порты НЕ доступны извне:
# - 5432 (PostgreSQL)
# - 7700 (MeiliSearch)
# - 8000 (API - только через Nginx)

# Проверка открытых портов
sudo netstat -tulpn | grep LISTEN
```

### 4.2 Настройка автоматического обновления SSL

```bash
# Автообновление сертификата
sudo crontab -e

# Добавить:
0 0 1 * * certbot renew --quiet && docker-compose -f /opt/mdm-bot/docker-compose.prod.yaml restart webapp
```

### 4.3 Rate Limiting (опционально)

Добавьте в `webapp/nginx-ssl.conf` в блок `http`:

```nginx
http {
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    # ... остальная конфигурация
}
```

---

## 📊 Шаг 5: Мониторинг и логи

### 5.1 Просмотр логов

```bash
# Все логи
docker-compose -f docker-compose.prod.yaml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yaml logs -f bot
docker-compose -f docker-compose.prod.yaml logs -f api
docker-compose -f docker-compose.prod.yaml logs -f webapp

# Последние N строк
docker-compose -f docker-compose.prod.yaml logs --tail=100 api
```

### 5.2 Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Дисковое пространство
docker system df
```

### 5.3 Настройка Healthchecks (опционально)

Зарегистрируйтесь на [healthchecks.io](https://healthchecks.io) и добавьте cron:

```bash
# Проверка каждые 5 минут
*/5 * * * * curl -fsS --retry 3 https://hc-ping.com/YOUR-UUID-HERE > /dev/null || echo "Health check failed"
```

---

## 💾 Шаг 6: Резервное копирование

### 6.1 Скрипт бэкапа PostgreSQL

Создайте `scripts/backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/mdm-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mdm_bot_$DATE.sql.gz"

# Создать директорию если не существует
mkdir -p $BACKUP_DIR

# Бэкап базы данных
docker-compose -f /opt/mdm-bot/docker-compose.prod.yaml exec -T postgres \
    pg_dump -U postgres_prod mdm_bot_db | gzip > $BACKUP_FILE

# Удалить старые бэкапы (старше 7 дней)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE"
```

### 6.2 Автоматический бэкап

```bash
chmod +x scripts/backup-db.sh

# Добавить в cron (каждый день в 2:00)
0 2 * * * /opt/mdm-bot/scripts/backup-db.sh
```

### 6.3 Восстановление из бэкапа

```bash
# Распаковать и восстановить
gunzip < backups/mdm_bot_YYYYMMDD_HHMMSS.sql.gz | \
    docker-compose -f docker-compose.prod.yaml exec -T postgres \
    psql -U postgres_prod mdm_bot_db
```

---

## 🔄 Шаг 7: Обновление приложения

### 7.1 Обновление кода

```bash
cd /opt/mdm-bot

# Создать бэкап перед обновлением
./scripts/backup-db.sh

# Обновить код
git pull origin master

# Пересобрать и перезапустить
docker-compose -f docker-compose.prod.yaml build
docker-compose -f docker-compose.prod.yaml up -d
```

### 7.2 Откат к предыдущей версии

```bash
# Просмотр коммитов
git log --oneline

# Откат к конкретному коммиту
git checkout COMMIT_HASH

# Пересборка
docker-compose -f docker-compose.prod.yaml build
docker-compose -f docker-compose.prod.yaml up -d
```

---

## ✅ Production Checklist

Перед запуском убедитесь:

- [ ] ✅ SSL сертификат установлен и работает
- [ ] ✅ `.env` файл с production настройками
- [ ] ✅ WEBAPP_URL использует HTTPS
- [ ] ✅ ALLOWED_ORIGINS настроен правильно
- [ ] ✅ Сильные пароли для PostgreSQL и MeiliSearch
- [ ] ✅ Файрвол настроен (только 80, 443, 22)
- [ ] ✅ PostgreSQL порт НЕ доступен извне
- [ ] ✅ MeiliSearch порт НЕ доступен извне
- [ ] ✅ API документация отключена в production (`/api/docs`)
- [ ] ✅ Логирование настроено (rotation, max size)
- [ ] ✅ Healthcheck эндпоинты работают
- [ ] ✅ Автоматический бэкап настроен
- [ ] ✅ SSL автообновление настроено
- [ ] ✅ Мониторинг настроен
- [ ] ✅ Telegram Mini App открывается через бота
- [ ] ✅ Товары загружаются корректно
- [ ] ✅ Пагинация работает

---

## 🆘 Troubleshooting

### Проблема: Mini App не открывается

**Решение:**
1. Проверьте WEBAPP_URL в `.env` (должен быть HTTPS)
2. Убедитесь, что SSL сертификат валидный
3. Проверьте логи: `docker-compose -f docker-compose.prod.yaml logs webapp`

### Проблема: Ошибка CORS

**Решение:**
1. Проверьте ALLOWED_ORIGINS в `.env`
2. Убедитесь, что домен указан с https://
3. Перезапустите API: `docker-compose -f docker-compose.prod.yaml restart api`

### Проблема: База данных не подключается

**Решение:**
1. Проверьте логи postgres: `docker-compose logs postgres`
2. Убедитесь, что POSTGRES_PASSWORD правильный
3. Проверьте healthcheck: `docker-compose ps`

### Проблема: Out of Memory

**Решение:**
1. Увеличьте лимиты в `docker-compose.prod.yaml`
2. Добавьте swap: `sudo fallocate -l 4G /swapfile`
3. Мониторьте: `docker stats`

---

## 📞 Поддержка

- 📚 Документация: `MINIAPP_GUIDE.md`
- 🐛 Issues: GitHub Issues
- 💬 Telegram: @your_support_bot

---

## 🎉 Готово!

Ваш Telegram Mini App запущен в production! 🚀

**Важные URL:**
- Web App: https://mdm-store.com
- API Health: https://mdm-store.com/api/health
- Telegram Bot: https://t.me/your_bot_username
