# Production Deployment Checklist

Используйте этот чеклист для развертывания MDM Bot в production.

## Перед развертыванием

### 1. Подготовка окружения

- [ ] Установлен Docker и Docker Compose
- [ ] Настроен доступ к серверу (SSH, sudo права)
- [ ] Открыты необходимые порты в файерволе (опционально: 5432, 7700)
- [ ] Есть домен и SSL сертификат (если требуется внешний доступ)

### 2. Конфигурация

```bash
# Клонировать репозиторий
git clone <repository-url>
cd mdm-bot

# Создать production .env
cp .env.production .env
```

- [ ] `BOT_TOKEN` - Получен от @BotFather в Telegram
- [ ] `POSTGRES_USER` - Установлен пользователь БД (default: postgres_prod)
- [ ] `POSTGRES_PASSWORD` - **КРИТИЧНО**: Сгенерирован надежный пароль
- [ ] `POSTGRES_DB` - Имя базы данных (default: mdm_bot_db)
- [ ] `MEILI_MASTER_KEY` - **КРИТИЧНО**: Сгенерирован ключ (минимум 16 символов)
- [ ] `MEILI_ENV` - Установлен в `production`

**Генерация надежных паролей:**
```bash
# Для POSTGRES_PASSWORD
openssl rand -base64 32

# Для MEILI_MASTER_KEY
openssl rand -base64 24
```

### 3. Безопасность

- [ ] `.env` файл не коммитится в git (проверить .gitignore)
- [ ] Пароли не содержат специальных символов, которые нужно экранировать
- [ ] Файрвол настроен (закрыты порты 5432 и 7700 от внешнего доступа)
- [ ] SSH ключ настроен для безопасного доступа к серверу
- [ ] Регулярные бэкапы запланированы (cron)

### 4. Проверка docker-compose.yaml

- [ ] Проверены resource limits для сервисов (CPU, RAM)
- [ ] Порты 5432 и 7700 закомментированы если не нужен внешний доступ
- [ ] Restart policy установлен в `unless-stopped`
- [ ] Health checks настроены для всех сервисов

## Развертывание

### 1. Первый запуск

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps
```

**Ожидаемый результат:**
```
NAME                IMAGE                              STATUS
mdm-bot-bot-1       mdm-bot-bot                       Up (healthy)
mdm-bot-postgres-1  postgres:16-alpine                 Up (healthy)
mdm-bot-meilisearch-1  getmeili/meilisearch:v1.10     Up (healthy)
```

- [ ] Все контейнеры в статусе `Up`
- [ ] Health checks проходят успешно

### 2. Проверка логов

```bash
# Логи бота
docker-compose logs -f bot

# Логи базы данных
docker-compose logs postgres

# Логи MeiliSearch
docker-compose logs meilisearch
```

- [ ] Бот успешно подключился к БД
- [ ] Бот успешно подключился к MeiliSearch
- [ ] Нет критических ошибок в логах
- [ ] Бот запустился и polling активен

### 3. Инициализация данных

```bash
# Импортировать товары из CSV (если есть)
docker-compose exec bot uv run convert.py
```

- [ ] CSV файл загружен (если применимо)
- [ ] Товары успешно импортированы в БД
- [ ] Товары проиндексированы в MeiliSearch

### 4. Тестирование бота

- [ ] Отправлен `/start` в Telegram - бот отвечает
- [ ] Поиск товаров работает
- [ ] Добавление в корзину работает
- [ ] Оформление заказа работает
- [ ] Профиль пользователя редактируется

## После развертывания

### 1. Мониторинг

```bash
# Проверить использование ресурсов
docker stats

# Проверить здоровье сервисов
curl http://localhost:7700/health  # MeiliSearch
docker-compose exec postgres pg_isready -U postgres_prod  # PostgreSQL
```

- [ ] CPU usage в пределах нормы (<80%)
- [ ] Memory usage в пределах нормы (<80%)
- [ ] Disk space достаточно

### 2. Настройка бэкапов

```bash
# Создать директорию для бэкапов
mkdir -p backups

# Добавить в crontab
crontab -e
```

**Добавить строку:**
```cron
0 2 * * * cd /path/to/mdm-bot && docker-compose exec -T postgres pg_dump -U postgres_prod mdm_bot_db | gzip > backups/backup-$(date +\%Y\%m\%d).sql.gz
```

- [ ] Cron job создан для ежедневных бэкапов
- [ ] Тестовый бэкап создан и проверен
- [ ] Процедура восстановления протестирована

### 3. Логирование

- [ ] Логи бота пишутся в файл `mdm.log`
- [ ] Настроена ротация логов (logrotate)
- [ ] Определены критические алерты для мониторинга

### 4. Документация

- [ ] Записаны учетные данные в безопасное место (password manager)
- [ ] Документированы custom изменения конфигурации
- [ ] Создан runbook для типичных проблем
- [ ] Команда ознакомлена с процедурами обслуживания

## Обслуживание

### Регулярные задачи

**Еженедельно:**
- [ ] Проверить логи на ошибки
- [ ] Проверить использование дискового пространства
- [ ] Проверить статус всех контейнеров

**Ежемесячно:**
- [ ] Обновить Docker образы
- [ ] Проверить и удалить старые бэкапы
- [ ] Проверить security updates

**Команды обслуживания:**

```bash
# Обновить образы и перезапустить
docker-compose pull
docker-compose up -d --build

# Очистить неиспользуемые образы
docker system prune -a

# Проверить размер volumes
docker system df
```

## Troubleshooting

### Бот не запускается

```bash
# Проверить логи
docker-compose logs bot

# Проверить .env
docker-compose exec bot env | grep -E 'BOT_TOKEN|POSTGRES|MEILI'

# Перезапустить контейнер
docker-compose restart bot
```

### Ошибки подключения к БД

```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Проверить логи
docker-compose logs postgres

# Протестировать подключение
docker-compose exec postgres psql -U postgres_prod -d mdm_bot_db -c '\dt'
```

### Проблемы с MeiliSearch

```bash
# Проверить health
curl http://localhost:7700/health

# Проверить логи
docker-compose logs meilisearch

# Проверить индексы
curl -H "Authorization: Bearer ${MEILI_MASTER_KEY}" \
  http://localhost:7700/indexes
```

### Восстановление из бэкапа

```bash
# Остановить бота
docker-compose stop bot

# Восстановить БД
docker-compose exec -T postgres psql -U postgres_prod mdm_bot_db < backups/backup-YYYYMMDD.sql

# Запустить бота
docker-compose start bot
```

## Контакты для поддержки

- Repository: [GitHub URL]
- Документация: [DEPLOYMENT.md](DEPLOYMENT.md)
- Telegram: @your_support_username

## Статус развертывания

**Дата развертывания:** _______________
**Версия:** _______________
**Развернул:** _______________
**Статус:** [ ] Dev [ ] Staging [ ] Production

---

✅ **Production Ready** - Все пункты чеклиста выполнены
