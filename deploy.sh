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
    
    echo "Копируем .env файл с сохранением важных настроек..."
    # Сохраняем важные настройки из старого .env
    if [ -f .env ]; then
        OLD_BOT_TOKEN=$(grep "^BOT_TOKEN=" .env | cut -d'=' -f2- || echo "")
        OLD_CLOUD_API_KEY=$(grep "^CLOUD_RU_API_KEY=" .env | cut -d'=' -f2- || echo "")
        OLD_ADMIN_IDS=$(grep "^ADMIN_USER_IDS=" .env | cut -d'=' -f2- || echo "")
        OLD_TESTING_MODE=$(grep "^TESTING_MODE=" .env | cut -d'=' -f2- || echo "")
        OLD_MULTIPLE_SESSIONS=$(grep "^ALLOW_MULTIPLE_SESSIONS=" .env | cut -d'=' -f2- || echo "")
        OLD_LLM_MODEL=$(grep "^LLM_MODEL=" .env | cut -d'=' -f2- || echo "")
        OLD_LLM_ENABLED=$(grep "^LLM_ENABLED=" .env | cut -d'=' -f2- || echo "")
        OLD_LLM_ANALYSIS_ENABLED=$(grep "^LLM_ANALYSIS_ENABLED=" .env | cut -d'=' -f2- || echo "")
    fi
    
    # Копируем новый .env
    cp /tmp/.env .
    
    # Восстанавливаем важные настройки, если они были
    if [ ! -z "$OLD_BOT_TOKEN" ]; then
        sed -i "s|^BOT_TOKEN=.*|BOT_TOKEN=$OLD_BOT_TOKEN|" .env
    fi
    if [ ! -z "$OLD_CLOUD_API_KEY" ]; then
        sed -i "s|^CLOUD_RU_API_KEY=.*|CLOUD_RU_API_KEY=$OLD_CLOUD_API_KEY|" .env
    fi
    if [ ! -z "$OLD_ADMIN_IDS" ]; then
        sed -i "s|^ADMIN_USER_IDS=.*|ADMIN_USER_IDS=$OLD_ADMIN_IDS|" .env
    fi
    if [ ! -z "$OLD_TESTING_MODE" ]; then
        sed -i "s|^TESTING_MODE=.*|TESTING_MODE=$OLD_TESTING_MODE|" .env
    fi
    if [ ! -z "$OLD_MULTIPLE_SESSIONS" ]; then
        sed -i "s|^ALLOW_MULTIPLE_SESSIONS=.*|ALLOW_MULTIPLE_SESSIONS=$OLD_MULTIPLE_SESSIONS|" .env
    fi
    if [ ! -z "$OLD_LLM_MODEL" ]; then
        sed -i "s|^LLM_MODEL=.*|LLM_MODEL=$OLD_LLM_MODEL|" .env
    fi
    if [ ! -z "$OLD_LLM_ENABLED" ]; then
        sed -i "s|^LLM_ENABLED=.*|LLM_ENABLED=$OLD_LLM_ENABLED|" .env
    fi
    if [ ! -z "$OLD_LLM_ANALYSIS_ENABLED" ]; then
        sed -i "s|^LLM_ANALYSIS_ENABLED=.*|LLM_ANALYSIS_ENABLED=$OLD_LLM_ANALYSIS_ENABLED|" .env
    fi
    
    echo "Создаем необходимые директории..."
    mkdir -p data logs
    
    echo "Восстанавливаем важные настройки из backup..."
    if [ -f settings_backup.env ]; then
        # Сначала восстанавливаем API ключ cloud.ru (критически важно!)
        CLOUD_API_KEY=$(grep "^CLOUD_RU_API_KEY=" settings_backup.env | cut -d'=' -f2-)
        if [ ! -z "$CLOUD_API_KEY" ]; then
            sed -i "s|^CLOUD_RU_API_KEY=.*|CLOUD_RU_API_KEY=$CLOUD_API_KEY|" .env || echo "CLOUD_RU_API_KEY=$CLOUD_API_KEY" >> .env
            echo "🔑 API ключ cloud.ru восстановлен"
        fi
        
        # Затем остальные настройки
        while IFS='=' read -r key value; do
            if [[ ! -z "$key" && ! "$key" =~ ^# && "$key" != "CLOUD_RU_API_KEY" ]]; then
                sed -i "s|^$key=.*|$key=$value|" .env || echo "$key=$value" >> .env
            fi
        done < settings_backup.env
        echo "✅ Настройки восстановлены из backup"
    else
        echo "⚠️ Backup файл не найден, используем сохраненные настройки"
    fi
    
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
