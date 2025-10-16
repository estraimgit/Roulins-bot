#!/bin/bash

# Скрипт развертывания на сервер
# Использование: ./deploy.sh

set -e

# Конфигурация
SERVER="user1@176.108.243.54"
APP_DIR="/home/user1/prisoners-dilemma-bot"
DOCKER_IMAGE="prisoners-dilemma-bot"

echo "🚀 Начинаем развертывание Prisoner's Dilemma Bot на сервер..."

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте config.env.example в .env и настройте переменные:"
    echo "cp config.env.example .env"
    echo "nano .env"
    exit 1
fi

# Проверяем наличие BOT_TOKEN
if ! grep -q "BOT_TOKEN=" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo "❌ BOT_TOKEN не настроен в .env файле!"
    echo "Получите токен у @BotFather и добавьте в .env файл"
    exit 1
fi

echo "✅ Конфигурация проверена"

# Создаем архив проекта
echo "📦 Создаем архив проекта..."
tar --exclude='.git' \
    --exclude='data' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='prisoners-dilemma-bot.tar.gz' \
    -czf prisoners-dilemma-bot.tar.gz .

echo "✅ Архив создан"

# Копируем файлы на сервер
echo "📤 Копируем файлы на сервер..."
scp prisoners-dilemma-bot.tar.gz $SERVER:/tmp/
scp .env $SERVER:/tmp/

echo "✅ Файлы скопированы"

# Подключаемся к серверу и разворачиваем
echo "🔧 Разворачиваем на сервере..."
ssh $SERVER << 'EOF'
    set -e
    
    echo "Создаем директорию приложения..."
    mkdir -p /home/user1/prisoners-dilemma-bot
    cd /home/user1/prisoners-dilemma-bot
    
    echo "Распаковываем архив..."
    tar -xzf /tmp/prisoners-dilemma-bot.tar.gz
    
    echo "Копируем .env файл..."
    cp /tmp/.env .
    
    echo "Создаем необходимые директории..."
    mkdir -p data logs
    
    echo "Останавливаем старые контейнеры..."
    docker-compose down || true
    
    echo "Собираем новый образ..."
    docker-compose build --no-cache
    
    echo "Запускаем контейнер..."
    docker-compose up -d
    
    echo "Проверяем статус..."
    docker-compose ps
    
    echo "Показываем логи..."
    docker-compose logs --tail=50
EOF

# Очищаем временные файлы
echo "🧹 Очищаем временные файлы..."
rm prisoners-dilemma-bot.tar.gz

echo "✅ Развертывание завершено!"
echo ""
echo "Для проверки статуса выполните:"
echo "ssh $SERVER 'cd $APP_DIR && docker-compose ps'"
echo ""
echo "Для просмотра логов выполните:"
echo "ssh $SERVER 'cd $APP_DIR && docker-compose logs -f'"
echo ""
echo "Для остановки бота выполните:"
echo "ssh $SERVER 'cd $APP_DIR && docker-compose down'"
