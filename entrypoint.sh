#!/bin/bash

# Скрипт запуска для Docker контейнера

echo "Starting Prisoner's Dilemma Bot..."

# Проверяем наличие необходимых переменных окружения
if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: BOT_TOKEN environment variable is not set"
    exit 1
fi

if [ -z "$ENCRYPTION_KEY" ]; then
    echo "ERROR: ENCRYPTION_KEY environment variable is not set"
    exit 1
fi

# Создаем директории если они не существуют
mkdir -p /app/data /app/logs

# Устанавливаем права доступа
chmod 755 /app/data /app/logs

# Запускаем бота
echo "Starting bot with Python..."
exec python main.py
