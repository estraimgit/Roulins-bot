#!/bin/bash

# Скрипт управления ботом на сервере
# Использование: ./server-manage.sh [start|stop|restart|status|logs|update]

SERVER="user1@176.108.243.54"
APP_DIR="/home/user1/prisoners-dilemma-bot"

case "$1" in
    start)
        echo "🚀 Запускаем бота..."
        ssh $SERVER "cd $APP_DIR && docker-compose up -d"
        ;;
    stop)
        echo "⏹️ Останавливаем бота..."
        ssh $SERVER "cd $APP_DIR && docker-compose down"
        ;;
    restart)
        echo "🔄 Перезапускаем бота..."
        ssh $SERVER "cd $APP_DIR && docker-compose restart"
        ;;
    status)
        echo "📊 Статус бота:"
        ssh $SERVER "cd $APP_DIR && docker-compose ps"
        ;;
    logs)
        echo "📋 Логи бота:"
        ssh $SERVER "cd $APP_DIR && docker-compose logs -f --tail=100"
        ;;
    update)
        echo "🔄 Обновляем бота..."
        ssh $SERVER "cd $APP_DIR && docker-compose pull && docker-compose up -d --build"
        ;;
    shell)
        echo "🐚 Подключаемся к контейнеру..."
        ssh $SERVER "cd $APP_DIR && docker-compose exec prisoners-dilemma-bot /bin/bash"
        ;;
    backup)
        echo "💾 Создаем резервную копию данных..."
        ssh $SERVER "cd $APP_DIR && tar -czf backup-\$(date +%Y%m%d-%H%M%S).tar.gz data/ logs/"
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs|update|shell|backup}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить бота"
        echo "  stop    - Остановить бота"
        echo "  restart - Перезапустить бота"
        echo "  status  - Показать статус"
        echo "  logs    - Показать логи"
        echo "  update  - Обновить и перезапустить"
        echo "  shell   - Подключиться к контейнеру"
        echo "  backup  - Создать резервную копию"
        exit 1
        ;;
esac
