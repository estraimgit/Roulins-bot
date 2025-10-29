#!/bin/bash

# Быстрое обновление бота (для опытных пользователей)
# Использовать только если уверены, что все настроено правильно

echo "🚀 Быстрое обновление Roulins_Bot"

# Остановка бота
pkill -f "python.*main.py" 2>/dev/null || true

# Резервное копирование
cp .env .env.backup 2>/dev/null || true
cp -r data data_backup 2>/dev/null || true

# Обновление кода
git stash
git pull origin main

# Восстановление настроек
mv .env.backup .env 2>/dev/null || true

# Обновление зависимостей
source venv/bin/activate
pip install -q -r requirements.txt

# Запуск бота
nohup python main.py > logs/bot_output.log 2>&1 &
echo $! > bot.pid

echo "✅ Обновление завершено! PID: $(cat bot.pid)"
echo "📊 Логи: tail -f logs/bot_output.log"

