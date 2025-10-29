#!/bin/bash

# Скрипт для безопасного обновления бота на сервере
# Сохраняет все ключи, токены и базу данных

set -e  # Останавливаем выполнение при ошибке

echo "🔄 Начало безопасного обновления Roulins_Bot"
echo "============================================"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Ошибка: Запустите скрипт из корневой директории проекта${NC}"
    exit 1
fi

# 1. Создаем резервную копию .env файла
echo -e "\n${YELLOW}📦 Шаг 1: Создание резервной копии .env файла...${NC}"
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Резервная копия .env создана${NC}"
else
    echo -e "${RED}⚠️  Внимание: Файл .env не найден${NC}"
fi

# 2. Создаем резервную копию базы данных
echo -e "\n${YELLOW}📦 Шаг 2: Создание резервной копии базы данных...${NC}"
if [ -d "data" ]; then
    BACKUP_DIR="data_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r data/* "$BACKUP_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✅ Резервная копия базы данных создана в $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  Директория data не найдена${NC}"
fi

# 3. Останавливаем бота (если запущен)
echo -e "\n${YELLOW}🛑 Шаг 3: Остановка бота...${NC}"
if pgrep -f "python.*main.py" > /dev/null; then
    pkill -f "python.*main.py" || true
    sleep 2
    echo -e "${GREEN}✅ Бот остановлен${NC}"
else
    echo -e "${YELLOW}ℹ️  Бот не был запущен${NC}"
fi

# 4. Сохраняем текущий .env во временный файл
echo -e "\n${YELLOW}💾 Шаг 4: Сохранение конфигурации...${NC}"
if [ -f ".env" ]; then
    cp .env .env.temp
    echo -e "${GREEN}✅ Конфигурация сохранена${NC}"
fi

# 5. Загружаем изменения из Git
echo -e "\n${YELLOW}📥 Шаг 5: Загрузка обновлений из Git...${NC}"
git stash || true
git pull origin main
echo -e "${GREEN}✅ Обновления загружены${NC}"

# 6. Восстанавливаем .env файл
echo -e "\n${YELLOW}🔧 Шаг 6: Восстановление конфигурации...${NC}"
if [ -f ".env.temp" ]; then
    mv .env.temp .env
    echo -e "${GREEN}✅ Конфигурация восстановлена${NC}"
else
    echo -e "${RED}❌ Ошибка: .env.temp не найден${NC}"
    exit 1
fi

# 7. Активируем виртуальное окружение
echo -e "\n${YELLOW}🔌 Шаг 7: Активация виртуального окружения...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Виртуальное окружение активировано${NC}"
else
    echo -e "${YELLOW}⚠️  Виртуальное окружение не найдено, создаем новое...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Виртуальное окружение создано и активировано${NC}"
fi

# 8. Обновляем зависимости
echo -e "\n${YELLOW}📦 Шаг 8: Установка/обновление зависимостей...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Зависимости установлены${NC}"

# 9. Проверяем конфигурацию
echo -e "\n${YELLOW}🔍 Шаг 9: Проверка конфигурации...${NC}"
if python -c "from config.settings import Config; Config.validate(); print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✅ Конфигурация валидна${NC}"
else
    echo -e "${RED}❌ Ошибка: Конфигурация невалидна${NC}"
    echo -e "${YELLOW}Проверьте файл .env и исправьте ошибки${NC}"
    exit 1
fi

# 10. Создаем необходимые директории
echo -e "\n${YELLOW}📁 Шаг 10: Создание необходимых директорий...${NC}"
mkdir -p data logs
echo -e "${GREEN}✅ Директории созданы${NC}"

# 11. Запускаем бота
echo -e "\n${YELLOW}🚀 Шаг 11: Запуск обновленного бота...${NC}"
nohup python main.py > logs/bot_output.log 2>&1 &
BOT_PID=$!
echo $BOT_PID > bot.pid
sleep 3

# Проверяем, что бот запустился
if ps -p $BOT_PID > /dev/null; then
    echo -e "${GREEN}✅ Бот успешно запущен (PID: $BOT_PID)${NC}"
else
    echo -e "${RED}❌ Ошибка: Бот не запустился${NC}"
    echo -e "${YELLOW}Проверьте логи: tail -f logs/bot_output.log${NC}"
    exit 1
fi

# Выводим финальную информацию
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📊 Информация о боте:"
echo "  PID: $BOT_PID"
echo "  Логи: logs/bot_output.log"
echo "  Конфигурация: .env"
echo ""
echo "🔧 Полезные команды:"
echo "  Просмотр логов: tail -f logs/bot_output.log"
echo "  Остановка бота: kill $BOT_PID"
echo "  Проверка статуса: ps -p $BOT_PID"
echo ""
echo "💾 Резервные копии:"
echo "  База данных: $BACKUP_DIR"
echo "  Конфигурация: .env.backup.*"
echo ""

