#!/bin/bash

# Скрипт для сохранения важных настроек при обновлениях
# Этот скрипт гарантирует, что настройки админа и тестирования не будут потеряны

SERVER="user1@176.108.243.54"
REMOTE_APP_DIR="/home/user1/prisoners-dilemma-bot"

echo "🔒 Сохраняем важные настройки..."

# Сохраняем текущие настройки
ssh $SERVER "cd $REMOTE_APP_DIR && cat > settings_backup.env << 'EOF'
# Важные настройки - НЕ УДАЛЯТЬ!
ADMIN_USER_IDS=177657170
TESTING_MODE=true
ALLOW_MULTIPLE_SESSIONS=true
LLM_ENABLED=true
LLM_ANALYSIS_ENABLED=true
LLM_MODEL=GigaChat/GigaChat-2-Max
CLOUD_RU_API_KEY=ZTE0NjlhMzktYTFkOS00OGZjLWI3OGYtNzI0YjY4Mjc4MGRj.738e2f53ef86e0bec40be8e5262b9840
EOF"

echo "✅ Настройки сохранены в settings_backup.env"

# Функция для восстановления настроек
restore_settings() {
    echo "🔄 Восстанавливаем настройки..."
    ssh $SERVER "cd $REMOTE_APP_DIR && if [ -f settings_backup.env ]; then
        # Восстанавливаем настройки из backup
        while IFS='=' read -r key value; do
            if [[ ! -z \"\$key\" && ! \"\$key\" =~ ^# ]]; then
                sed -i \"s|^\$key=.*|\$key=\$value|\" .env || echo \"\$key=\$value\" >> .env
            fi
        done < settings_backup.env
        echo '✅ Настройки восстановлены'
    else
        echo '❌ Файл backup не найден'
    fi"
}

# Проверяем, есть ли аргумент для восстановления
if [ "$1" = "restore" ]; then
    restore_settings
    exit 0
fi

echo "📋 Доступные команды:"
echo "  $0          - сохранить настройки"
echo "  $0 restore  - восстановить настройки"
echo "  $0 check    - проверить текущие настройки"

if [ "$1" = "check" ]; then
    echo "🔍 Проверяем текущие настройки..."
    ssh $SERVER "cd $REMOTE_APP_DIR && echo '=== Текущие настройки ===' && cat .env | grep -E '(ADMIN_USER_IDS|TESTING_MODE|ALLOW_MULTIPLE_SESSIONS|LLM_)'"
fi
