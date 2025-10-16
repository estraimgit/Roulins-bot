#!/bin/bash

# Скрипт для сброса всех активных сессий и данных эксперимента

echo "🔄 Сбрасываем все активные сессии..."

# Останавливаем бота
echo "⏹️ Останавливаем бота..."
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose down"

# Очищаем базу данных
echo "🗑️ Очищаем базу данных..."
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose up -d && sleep 3 && docker exec prisoners-dilemma-bot python3 -c \"
import sqlite3
conn = sqlite3.connect('/app/data/experiment.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM participants')
cursor.execute('DELETE FROM chat_messages')
cursor.execute('DELETE FROM survey_responses')
cursor.execute('DELETE FROM llm_analysis')
cursor.execute('DELETE FROM conversation_flow')
conn.commit()
print('✅ Все данные очищены')
conn.close()
\""

# Перезапускаем бота
echo "🚀 Перезапускаем бота..."
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose restart"

echo "✅ Готово! Все сессии сброшены, бот перезапущен в режиме polling."
