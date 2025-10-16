#!/bin/bash

# Скрипт для обновления API ключа cloud.ru
# Сохраняет ключ при всех обновлениях

SERVER="user1@176.108.243.54"
REMOTE_APP_DIR="/home/user1/prisoners-dilemma-bot"

if [ -z "$1" ]; then
    echo "Использование: $0 <NEW_CLOUD_RU_API_KEY>"
    echo "Пример: $0 ZTE0NjlhMzktYTFkOS00OGZjLWI3OGYtNzI0YjY4Mjc4MGRj.738e2f53ef86e0bec40be8e5262b9840"
    exit 1
fi

NEW_API_KEY="$1"

echo "🔧 Обновляем API ключ cloud.ru на сервере..."

# Обновляем API ключ в .env файле
ssh $SERVER "cd $REMOTE_APP_DIR && sed -i 's/^CLOUD_RU_API_KEY=.*/CLOUD_RU_API_KEY=$NEW_API_KEY/' .env"

# Проверяем, что ключ обновился
echo "✅ Проверяем обновление..."
ssh $SERVER "cd $REMOTE_APP_DIR && grep CLOUD_RU_API_KEY .env"

# Перезапускаем бота
echo "🔄 Перезапускаем бота..."
ssh $SERVER "cd $REMOTE_APP_DIR && docker-compose down && docker-compose up -d --build"

echo "✅ API ключ cloud.ru обновлен и бот перезапущен!"
echo "📋 Для проверки статуса LLM используйте: /admin llm_status"
