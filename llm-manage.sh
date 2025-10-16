#!/bin/bash

# Скрипт для управления LLM ботом

SERVER="user1@176.108.243.54"
PROJECT_DIR="/home/user1/prisoners-dilemma-bot"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_message() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_info() {
    echo -e "${BLUE}$1${NC}"
}

# Функция для проверки статуса
check_status() {
    print_info "📊 Проверяем статус LLM бота..."
    ssh $SERVER "cd $PROJECT_DIR && docker-compose ps"
}

# Функция для запуска LLM бота
start_llm_bot() {
    print_message "🚀 Запускаем LLM бота..."
    
    # Останавливаем обычный бот
    ssh $SERVER "cd $PROJECT_DIR && docker-compose down"
    
    # Заменяем main.py на main_llm.py
    ssh $SERVER "cd $PROJECT_DIR && cp main_llm.py main.py"
    
    # Запускаем LLM бота
    ssh $SERVER "cd $PROJECT_DIR && docker-compose up -d"
    
    print_message "✅ LLM бот запущен!"
    check_status
}

# Функция для остановки LLM бота
stop_llm_bot() {
    print_message "⏹️ Останавливаем LLM бота..."
    ssh $SERVER "cd $PROJECT_DIR && docker-compose down"
    print_message "✅ LLM бот остановлен!"
}

# Функция для перезапуска LLM бота
restart_llm_bot() {
    print_message "🔄 Перезапускаем LLM бота..."
    stop_llm_bot
    sleep 2
    start_llm_bot
}

# Функция для просмотра логов
view_logs() {
    print_info "📋 Логи LLM бота:"
    ssh $SERVER "cd $PROJECT_DIR && docker-compose logs --tail=50 -f"
}

# Функция для обновления токена LLM
update_llm_token() {
    if [ -z "$1" ]; then
        print_error "❌ Ошибка: Не указан токен"
        echo ""
        echo "Использование:"
        echo "  ./llm-manage.sh update-token YOUR_CLOUD_RU_TOKEN"
        echo ""
        echo "Пример:"
        echo "  ./llm-manage.sh update-token sk-1234567890abcdef"
        exit 1
    fi
    
    TOKEN="$1"
    
    print_message "🔧 Обновляем токен cloud.ru на сервере..."
    
    # Обновляем токен на сервере
    ssh $SERVER "cd $PROJECT_DIR && sed -i 's/CLOUD_RU_API_KEY=.*/CLOUD_RU_API_KEY='$TOKEN'/' .env"
    
    if [ $? -eq 0 ]; then
        print_message "✅ Токен обновлен успешно!"
        print_message "🔄 Перезапускаем бота..."
        restart_llm_bot
    else
        print_error "❌ Ошибка при обновлении токена"
    fi
}

# Функция для проверки LLM анализа
check_llm_analysis() {
    print_info "🧠 Проверяем LLM анализ..."
    ssh $SERVER "cd $PROJECT_DIR && docker-compose exec prisoners-dilemma-bot python -c \"
from utils.database import DatabaseManager
import json

db = DatabaseManager()
llm_data = db.get_llm_analysis_data()

print(f'Всего LLM анализов: {len(llm_data)}')

if llm_data:
    print('\\nПоследние 3 анализа:')
    for i, analysis in enumerate(llm_data[-3:]):
        print(f'\\n{i+1}. Участник: {analysis[\"participant_id\"]}')
        print(f'   Сообщение: {analysis[\"user_message\"][:50]}...')
        analysis_json = json.loads(analysis['analysis_json'])
        print(f'   Эмоция: {analysis_json.get(\"emotion\", \"неизвестно\")}')
        print(f'   Намерение: {analysis_json.get(\"intent\", \"неизвестно\")}')
        print(f'   Уверенность: {analysis_json.get(\"confidence\", \"неизвестно\")}')
else:
    print('LLM анализы не найдены')
\""
}

# Функция для экспорта LLM данных
export_llm_data() {
    print_message "📤 Экспортируем LLM данные..."
    
    ssh $SERVER "cd $PROJECT_DIR && docker-compose exec prisoners-dilemma-bot python -c \"
from utils.database import DatabaseManager
import json
from datetime import datetime

db = DatabaseManager()
llm_data = db.get_llm_analysis_data()

# Экспортируем в JSON
export_data = {
    'export_timestamp': datetime.now().isoformat(),
    'total_analyses': len(llm_data),
    'analyses': llm_data
}

with open('/app/data/llm_analysis_export.json', 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

print(f'Экспортировано {len(llm_data)} LLM анализов в llm_analysis_export.json')
\""
    
    # Копируем файл на локальную машину
    scp $SERVER:$PROJECT_DIR/data/llm_analysis_export.json ./llm_analysis_export.json
    print_message "✅ LLM данные экспортированы в llm_analysis_export.json"
}

# Функция для показа справки
show_help() {
    echo "🤖 LLM Bot Management Script"
    echo "=========================="
    echo ""
    echo "Использование:"
    echo "  ./llm-manage.sh [команда]"
    echo ""
    echo "Команды:"
    echo "  start           - Запустить LLM бота"
    echo "  stop            - Остановить LLM бота"
    echo "  restart         - Перезапустить LLM бота"
    echo "  status          - Показать статус"
    echo "  logs            - Показать логи"
    echo "  update-token    - Обновить токен cloud.ru"
    echo "  check-analysis  - Проверить LLM анализ"
    echo "  export-data     - Экспортировать LLM данные"
    echo "  help            - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  ./llm-manage.sh start"
    echo "  ./llm-manage.sh update-token sk-1234567890abcdef"
    echo "  ./llm-manage.sh check-analysis"
}

# Основная логика
case "$1" in
    start)
        start_llm_bot
        ;;
    stop)
        stop_llm_bot
        ;;
    restart)
        restart_llm_bot
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    update-token)
        update_llm_token "$2"
        ;;
    check-analysis)
        check_llm_analysis
        ;;
    export-data)
        export_llm_data
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "❌ Неизвестная команда: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
