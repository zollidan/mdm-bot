#!/bin/bash

echo "🔍 Проверка Telegram Mini App..."
echo ""

# Проверка наличия необходимых файлов
echo "📁 Проверка структуры файлов..."

FILES=(
    "api_server.py"
    "webapp/package.json"
    "webapp/vite.config.js"
    "webapp/src/App.vue"
    "webapp/src/components/ProductList.vue"
    "webapp/src/api/products.js"
    "webapp/Dockerfile"
    "webapp/nginx.conf"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - НЕ НАЙДЕН"
    fi
done

echo ""
echo "🔌 Проверка доступности сервисов..."

# Проверка API
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API Server (http://localhost:8000)"
else
    echo "❌ API Server - не доступен (запустите: python api_server.py)"
fi

# Проверка Webapp
if curl -s http://localhost/ > /dev/null 2>&1; then
    echo "✅ Web App (http://localhost)"
else
    echo "⚠️  Web App - не доступен (запустите: docker-compose up webapp)"
fi

# Проверка PostgreSQL
if docker-compose ps postgres | grep -q "Up"; then
    echo "✅ PostgreSQL"
else
    echo "❌ PostgreSQL - не запущен (запустите: docker-compose up postgres)"
fi

echo ""
echo "📦 Проверка зависимостей..."

# Проверка Python зависимостей
if python -c "import fastapi" 2>/dev/null; then
    echo "✅ FastAPI установлен"
else
    echo "❌ FastAPI не установлен (выполните: uv sync)"
fi

# Проверка Node модулей
if [ -d "webapp/node_modules" ]; then
    echo "✅ Node.js зависимости установлены"
else
    echo "❌ Node.js зависимости не установлены (выполните: cd webapp && npm install)"
fi

echo ""
echo "🎯 Следующие шаги:"
echo "1. Запустите сервисы: docker-compose up --build"
echo "2. Откройте Telegram бота"
echo "3. Нажмите на кнопку '🛍️ Открыть каталог'"
echo ""
echo "📖 Документация: MINIAPP_QUICKSTART.md"
