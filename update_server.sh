#!/bin/bash

# Скрипт для безопасного обновления бота на сервере user1@176.108.243.54
# Сохраняет все ключи, токены и базу данных

set -e  # Останавливаем выполнение при ошибке

echo "🔄 Безопасное обновление Roulins_Bot на сервере"
echo "================================================"

# Параметры сервера
SERVER="user1@176.108.243.54"
APP_DIR="/home/user1/prisoners-dilemma-bot"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Создаем резервную копию .env файла
echo -e "\n${YELLOW}📦 Шаг 1: Создание резервной копии .env файла...${NC}"
ssh $SERVER "cd $APP_DIR && cp .env .env.backup.\$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo 'Файл .env не найден'"
echo -e "${GREEN}✅ Резервная копия .env создана${NC}"

# 2. Создаем резервную копию базы данных
echo -e "\n${YELLOW}📦 Шаг 2: Создание резервной копии базы данных...${NC}"
ssh $SERVER "cd $APP_DIR && mkdir -p data_backup_\$(date +%Y%m%d_%H%M%S) && cp -r data/* data_backup_\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'Директория data не найдена'"
echo -e "${GREEN}✅ Резервная копия базы данных создана${NC}"

# 3. Останавливаем бота
echo -e "\n${YELLOW}🛑 Шаг 3: Остановка бота...${NC}"
ssh $SERVER "cd $APP_DIR && docker-compose down"
echo -e "${GREEN}✅ Бот остановлен${NC}"

# 4. Сохраняем текущий .env во временный файл
echo -e "\n${YELLOW}💾 Шаг 4: Сохранение конфигурации...${NC}"
ssh $SERVER "cd $APP_DIR && cp .env .env.temp 2>/dev/null || echo 'Файл .env не найден'"
echo -e "${GREEN}✅ Конфигурация сохранена${NC}"

# 5. Загружаем изменения из Git
echo -e "\n${YELLOW}📥 Шаг 5: Загрузка обновлений из Git...${NC}"
ssh $SERVER "cd $APP_DIR && git stash && git pull origin main"
echo -e "${GREEN}✅ Обновления загружены${NC}"

# 6. Восстанавливаем .env файл
echo -e "\n${YELLOW}🔧 Шаг 6: Восстановление конфигурации...${NC}"
ssh $SERVER "cd $APP_DIR && mv .env.temp .env 2>/dev/null || echo 'Файл .env.temp не найден'"
echo -e "${GREEN}✅ Конфигурация восстановлена${NC}"

# 7. Пересобираем Docker образ
echo -e "\n${YELLOW}🔨 Шаг 7: Пересборка Docker образа...${NC}"
ssh $SERVER "cd $APP_DIR && docker-compose build --no-cache"
echo -e "${GREEN}✅ Docker образ пересобран${NC}"

# 8. Проверяем конфигурацию
echo -e "\n${YELLOW}🔍 Шаг 8: Проверка конфигурации...${NC}"
if ssh $SERVER "cd $APP_DIR && docker-compose run --rm prisoners-dilemma-bot python -c 'from config.settings import Config; Config.validate(); print(\"OK\")'" 2>/dev/null; then
    echo -e "${GREEN}✅ Конфигурация валидна${NC}"
else
    echo -e "${RED}❌ Ошибка: Конфигурация невалидна${NC}"
    echo -e "${YELLOW}Проверьте файл .env на сервере${NC}"
    exit 1
fi

# 9. Запускаем бота
echo -e "\n${YELLOW}🚀 Шаг 9: Запуск обновленного бота...${NC}"
ssh $SERVER "cd $APP_DIR && docker-compose up -d"
echo -e "${GREEN}✅ Бот запущен${NC}"

# 10. Проверяем статус
echo -e "\n${YELLOW}📊 Шаг 10: Проверка статуса...${NC}"
sleep 5
ssh $SERVER "cd $APP_DIR && docker-compose ps"

# Выводим финальную информацию
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📊 Информация о сервере:"
echo "  Сервер: $SERVER"
echo "  Директория: $APP_DIR"
echo "  Статус: docker-compose ps"
echo ""
echo "🔧 Полезные команды:"
echo "  Просмотр логов: ./server-manage.sh logs"
echo "  Статус бота: ./server-manage.sh status"
echo "  Остановка: ./server-manage.sh stop"
echo "  Перезапуск: ./server-manage.sh restart"
echo ""
echo "💾 Резервные копии созданы на сервере"
echo ""

