.PHONY: help dev prod stop restart logs clean backup restore health test

# Detect compose command (docker-compose or podman-compose)
COMPOSE := $(shell command -v podman-compose 2> /dev/null || command -v docker-compose 2> /dev/null)
ifeq ($(COMPOSE),)
    $(error "Neither podman-compose nor docker-compose found. Please install one of them.")
endif

help: ## Показать справку
	@echo "MDM Bot - Команды управления"
	@echo "Using: $(COMPOSE)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# === Development ===

dev: ## Запустить в режиме разработки
	@echo "🚀 Запуск в режиме разработки..."
	@if [ ! -f .env ]; then echo "⚠️  .env не найден! Копирую .env.example..."; cp .env.example .env; fi
	$(COMPOSE) up -d
	@echo "✅ Сервисы запущены"
	@make logs-bot

dev-build: ## Пересобрать и запустить в dev режиме
	$(COMPOSE) up -d --build

local: ## Запустить бота локально (только БД и MeiliSearch в Docker)
	@echo "🚀 Запуск БД и MeiliSearch..."
	$(COMPOSE) up -d postgres meilisearch
	@echo "✅ Запустите бота: python main.py"

# === Production ===

prod: ## Развернуть в production режиме
	@echo "🚀 Развертывание в production..."
	@if [ ! -f .env ]; then echo "❌ .env не найден! Создайте из .env.production"; exit 1; fi
	$(COMPOSE) up -d
	@echo "✅ Production сервисы запущены"
	@make health

prod-setup: ## Подготовить production окружение
	@echo "📝 Настройка production окружения..."
	@if [ ! -f .env ]; then cp .env.production .env; echo "✅ .env создан из .env.production - заполните переменные!"; else echo "⚠️  .env уже существует"; fi
	@mkdir -p backups
	@echo "✅ Директория backups создана"

# === Service Control ===

stop: ## Остановить все сервисы
	@echo "⏸️  Остановка сервисов..."
	$(COMPOSE) stop

down: ## Остановить и удалить контейнеры
	@echo "🔻 Остановка и удаление контейнеров..."
	$(COMPOSE) down

down-volumes: ## Остановить и удалить контейнеры с volumes (УДАЛЯЕТ ДАННЫЕ!)
	@echo "⚠️  ВНИМАНИЕ: Будут удалены все данные!"
	@read -p "Вы уверены? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) down -v; \
		echo "✅ Контейнеры и данные удалены"; \
	else \
		echo "❌ Отменено"; \
	fi

restart: ## Перезапустить все сервисы
	@echo "🔄 Перезапуск сервисов..."
	$(COMPOSE) restart

restart-bot: ## Перезапустить только бота
	@echo "🔄 Перезапуск бота..."
	$(COMPOSE) restart bot

# === Logs ===

logs: ## Показать логи всех сервисов
	$(COMPOSE) logs -f

logs-bot: ## Показать логи бота
	$(COMPOSE) logs -f bot

logs-db: ## Показать логи PostgreSQL
	$(COMPOSE) logs -f postgres

logs-search: ## Показать логи MeiliSearch
	$(COMPOSE) logs -f meilisearch

# === Database ===

db-shell: ## Открыть psql shell в PostgreSQL
	$(COMPOSE) exec postgres psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2)

db-import: ## Импортировать товары из CSV
	@echo "📦 Импорт товаров из CSV..."
	$(COMPOSE) exec bot uv run convert.py

backup: ## Создать бэкап базы данных
	@echo "💾 Создание бэкапа..."
	@mkdir -p backups
	@$(COMPOSE) exec -T postgres pg_dump -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) $$(grep POSTGRES_DB .env | cut -d '=' -f2) | gzip > backups/backup-$$(date +%Y%m%d-%H%M%S).sql.gz
	@echo "✅ Бэкап создан: backups/backup-$$(date +%Y%m%d-%H%M%S).sql.gz"

restore: ## Восстановить из бэкапа (использование: make restore FILE=backups/backup.sql.gz)
	@if [ -z "$(FILE)" ]; then echo "❌ Укажите файл: make restore FILE=backups/backup.sql.gz"; exit 1; fi
	@echo "♻️  Восстановление из $(FILE)..."
	@$(COMPOSE) stop bot
	@gunzip < $(FILE) | $(COMPOSE) exec -T postgres psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) $$(grep POSTGRES_DB .env | cut -d '=' -f2)
	@$(COMPOSE) start bot
	@echo "✅ База данных восстановлена"

# === Health & Monitoring ===

health: ## Проверить здоровье всех сервисов
	@echo "🏥 Проверка здоровья сервисов..."
	@echo "\n📊 Статус контейнеров:"
	@$(COMPOSE) ps
	@echo "\n🔍 PostgreSQL:"
	@$(COMPOSE) exec postgres pg_isready -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) || echo "❌ PostgreSQL недоступен"
	@echo "\n🔍 MeiliSearch:"
	@curl -s http://localhost:7700/health | grep -q "available" && echo "✅ MeiliSearch работает" || echo "❌ MeiliSearch недоступен"

status: ## Показать статус контейнеров
	$(COMPOSE) ps

stats: ## Показать использование ресурсов
	docker stats --no-stream

# === Maintenance ===

update: ## Обновить образы и перезапустить
	@echo "🔄 Обновление образов..."
	$(COMPOSE) pull
	$(COMPOSE) up -d --build
	@echo "✅ Обновление завершено"

clean: ## Очистить неиспользуемые Docker ресурсы
	@echo "🧹 Очистка Docker..."
	docker system prune -f
	@echo "✅ Очистка завершена"

clean-all: ## Глубокая очистка Docker (включая образы)
	@echo "⚠️  Глубокая очистка Docker..."
	docker system prune -a -f
	@echo "✅ Глубокая очистка завершена"

# === Testing ===

test: ## Проверить конфигурацию
	@echo "🧪 Проверка конфигурации..."
	@if [ ! -f .env ]; then echo "❌ .env не найден"; exit 1; else echo "✅ .env найден"; fi
	@grep -q "BOT_TOKEN=" .env && echo "✅ BOT_TOKEN настроен" || echo "❌ BOT_TOKEN не настроен"
	@grep -q "POSTGRES_PASSWORD=" .env && echo "✅ POSTGRES_PASSWORD настроен" || echo "❌ POSTGRES_PASSWORD не настроен"
	@grep -q "MEILI_MASTER_KEY=" .env && echo "✅ MEILI_MASTER_KEY настроен" || echo "❌ MEILI_MASTER_KEY не настроен"
	@$(COMPOSE) config > /dev/null && echo "✅ docker-compose.yaml валиден" || echo "❌ Ошибка в docker-compose.yaml"

# === Info ===

env: ## Показать переменные окружения (без секретов)
	@echo "🔐 Переменные окружения:"
	@grep -v "PASSWORD\|TOKEN\|KEY" .env 2>/dev/null || echo "❌ .env не найден"

ports: ## Показать открытые порты
	@echo "🔌 Открытые порты:"
	@$(COMPOSE) ps --format json | jq -r '.[].Publishers[] | select(.PublishedPort != null) | "\(.PublishedPort) -> \(.TargetPort) (\(.Name))"' 2>/dev/null || $(COMPOSE) ps
