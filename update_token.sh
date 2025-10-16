#!/bin/bash

# Скрипт для обновления токена бота

echo "🤖 Обновление токена бота"
echo "========================="
echo ""

# Проверяем, что токен передан
if [ -z "$1" ]; then
    echo "❌ Ошибка: Не указан токен"
    echo ""
    echo "Использование:"
    echo "  ./update_token.sh YOUR_BOT_TOKEN"
    echo ""
    echo "Пример:"
    echo "  ./update_token.sh 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890"
    echo ""
    echo "Чтобы получить токен:"
    echo "1. Откройте Telegram"
    echo "2. Найдите @BotFather"
    echo "3. Отправьте /newbot"
    echo "4. Следуйте инструкциям"
    echo "5. Скопируйте полученный токен"
    exit 1
fi

TOKEN="$1"
SERVER="user1@176.108.243.54"

echo "🔧 Обновляем токен на сервере..."

# Обновляем токен на сервере
ssh $SERVER "cd /home/user1/prisoners-dilemma-bot && sed -i 's/BOT_TOKEN=.*/BOT_TOKEN='$TOKEN'/' .env"

if [ $? -eq 0 ]; then
    echo "✅ Токен обновлен успешно!"
    echo ""
    echo "🚀 Запускаем бота..."
    
    # Запускаем бота
    ./server-manage.sh start
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Бот запущен!"
        echo ""
        echo "📋 Проверьте работу:"
        echo "1. Найдите вашего бота в Telegram"
        echo "2. Отправьте команду /start"
        echo "3. Бот должен ответить"
        echo ""
        echo "🔍 Для просмотра логов:"
        echo "  ./server-manage.sh logs"
        echo ""
        echo "📊 Для проверки статуса:"
        echo "  ./server-manage.sh status"
    else
        echo "❌ Ошибка при запуске бота"
        echo "Проверьте логи: ./server-manage.sh logs"
    fi
else
    echo "❌ Ошибка при обновлении токена"
    echo "Проверьте подключение к серверу"
fi
