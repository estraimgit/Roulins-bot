#!/bin/bash

# Автоматическое восстановление настроек
# Этот скрипт гарантирует, что важные настройки никогда не потеряются

SERVER="user1@176.108.243.54"
REMOTE_APP_DIR="/home/user1/prisoners-dilemma-bot"

echo "🔧 Автоматическое восстановление настроек..."

# Проверяем, есть ли backup файл
ssh $SERVER "cd $REMOTE_APP_DIR && if [ -f settings_backup.env ]; then
    echo '📋 Найден backup файл, восстанавливаем настройки...'
    
    # Проверяем, есть ли настройки в .env
    if ! grep -q 'ADMIN_USER_IDS=' .env; then
        echo '⚠️ Настройки админа отсутствуют, восстанавливаем...'
        cat settings_backup.env >> .env
        echo '✅ Настройки восстановлены'
    else
        echo '✅ Настройки админа уже присутствуют'
    fi
    
    # Проверяем API ключ cloud.ru
    if ! grep -q 'CLOUD_RU_API_KEY=' .env; then
        echo '⚠️ API ключ cloud.ru отсутствует, восстанавливаем...'
        cat settings_backup.env >> .env
        echo '✅ API ключ восстановлен'
    else
        echo '✅ API ключ cloud.ru уже присутствует'
    fi
    
    echo '🔄 Перезапускаем бота...'
    docker-compose down
    docker-compose up -d
    
    echo '✅ Восстановление завершено!'
else
    echo '❌ Backup файл не найден!'
    echo 'Создаем новый backup файл...'
    
    cat > settings_backup.env << 'EOF'
# Важные настройки - НЕ УДАЛЯТЬ И НЕ ОБНОВЛЯТЬ!
ADMIN_USER_IDS=177657170
TESTING_MODE=true
ALLOW_MULTIPLE_SESSIONS=true
LLM_ENABLED=true
LLM_ANALYSIS_ENABLED=true
LLM_MODEL=GigaChat/GigaChat-2-Max
# API ключ cloud.ru - КРИТИЧЕСКИ ВАЖНО! НИКОГДА НЕ СТИРАТЬ!
CLOUD_RU_API_KEY=ZTE0NjlhMzktYTFkOS00OGZjLWI3OGYtNzI0YjY4Mjc4MGRj.738e2f53ef86e0bec40be8e5262b9840
EOF
    
    echo '✅ Backup файл создан'
fi"

echo "🎯 Проверяем финальный статус..."
ssh $SERVER "cd $REMOTE_APP_DIR && echo '📋 Текущие настройки:' && cat .env | grep -E 'ADMIN|CLOUD|LLM'"
