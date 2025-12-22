# ⚡ Quick Production Guide

## 🚀 Запуск за 5 минут

### Предварительно:
- Сервер с Docker
- Домен с SSL сертификатом
- Telegram Bot Token

### Команды:

```bash
# 1. Клонировать
git clone https://github.com/your/mdm-bot.git && cd mdm-bot

# 2. Настроить .env
cp .env.production .env
nano .env  # Заполнить: BOT_TOKEN, пароли, WEBAPP_URL, ALLOWED_ORIGINS

# 3. Сгенерировать пароли
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)"
echo "MEILI_MASTER_KEY=$(openssl rand -base64 32)"

# 4. Настроить SSL в docker-compose.prod.yaml
nano docker-compose.prod.yaml
# Добавить в секцию webapp > volumes:
#   - /etc/letsencrypt/live/ДОМЕН/fullchain.pem:/etc/nginx/ssl/cert.pem:ro
#   - /etc/letsencrypt/live/ДОМЕН/privkey.pem:/etc/nginx/ssl/key.pem:ro

# 5. Настроить Nginx
cp webapp/nginx-ssl.conf.template webapp/nginx-ssl.conf
sed -i 's/your-domain.com/ваш-домен.com/g' webapp/nginx-ssl.conf

# 6. Запустить!
docker-compose -f docker-compose.prod.yaml up -d

# 7. Проверить
docker-compose -f docker-compose.prod.yaml ps
curl https://ваш-домен.com/api/health
```

## ✅ Checklist

Минимум для запуска:
- [ ] `.env` с HTTPS WEBAPP_URL
- [ ] SSL сертификат
- [ ] ALLOWED_ORIGINS настроен
- [ ] Сильные пароли (32+ символов)

## 📖 Документация

- **Полный гайд**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Чеклист**: [PRODUCTION_CHECKLIST.txt](PRODUCTION_CHECKLIST.txt)
- **Summary**: [PRODUCTION_READY_SUMMARY.md](PRODUCTION_READY_SUMMARY.md)

## 🆘 Проблемы?

1. Mini App не открывается → Проверьте WEBAPP_URL (должен быть HTTPS!)
2. CORS ошибки → Проверьте ALLOWED_ORIGINS
3. База не подключается → Проверьте POSTGRES_PASSWORD

## 🎯 Готово!

После запуска:
1. Откройте бота в Telegram
2. /start
3. Нажмите "🛍️ Открыть каталог"
4. Готово! 🎉
