#!/bin/bash

# Скрипт для запуска в режиме разработки
# Использует tmux для управления несколькими терминалами

SESSION="mdm-dev"

# Проверка наличия tmux
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux не установлен. Установите его: sudo dnf install tmux"
    exit 1
fi

# Убиваем существующую сессию если она есть
tmux kill-session -t $SESSION 2>/dev/null

echo "🚀 Запуск MDM Bot в режиме разработки..."

# Создаем новую сессию
tmux new-session -d -s $SESSION -n "services"

# Окно 1: Docker сервисы (postgres, meilisearch)
tmux send-keys -t $SESSION:0 "docker-compose up postgres meilisearch" C-m

# Окно 2: API Server
tmux new-window -t $SESSION -n "api"
tmux send-keys -t $SESSION:1 "sleep 5 && python api_server.py" C-m

# Окно 3: Telegram Bot
tmux new-window -t $SESSION -n "bot"
tmux send-keys -t $SESSION:2 "sleep 7 && python main.py" C-m

# Окно 4: Frontend Dev Server
tmux new-window -t $SESSION -n "webapp"
tmux send-keys -t $SESSION:3 "cd webapp && npm run dev" C-m

# Окно 5: Логи/терминал
tmux new-window -t $SESSION -n "logs"
tmux send-keys -t $SESSION:4 "echo '📊 Окно для логов и команд'" C-m

# Выбираем первое окно
tmux select-window -t $SESSION:0

echo "✅ Сервисы запущены в tmux сессии: $SESSION"
echo ""
echo "Команды управления:"
echo "  tmux attach -t $SESSION    - Подключиться к сессии"
echo "  Ctrl+B, D                  - Отключиться от сессии (не останавливая)"
echo "  Ctrl+B, [0-4]              - Переключиться между окнами"
echo "  tmux kill-session -t $SESSION - Остановить все сервисы"
echo ""
echo "Окна:"
echo "  0: Docker (postgres, meilisearch)"
echo "  1: API Server (port 8000)"
echo "  2: Telegram Bot"
echo "  3: Web App (port 5173)"
echo "  4: Логи/терминал"
echo ""

# Автоматически подключаемся к сессии
tmux attach -t $SESSION
