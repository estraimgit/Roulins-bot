# 🧠 LLM Интеграция для Анализа Сообщений

## Обзор

Добавлена интеграция с LLM (Large Language Model) для анализа сообщений пользователей в реальном времени. Это позволяет боту:

- **Анализировать эмоции** пользователей
- **Определять намерения** в сообщениях
- **Генерировать персонализированные ответы**
- **Оценивать эффективность нуджинга**
- **Предсказывать риск выхода из эксперимента**

## 🚀 Возможности

### 1. Анализ Сообщений
- **Эмоциональное состояние**: positive, negative, neutral, anxious, frustrated, cooperative, defensive
- **Намерения**: cooperate, defect, question, complaint, confusion, agreement, disagreement
- **Уверенность**: high, medium, low
- **Сопротивление убеждению**: high, medium, low
- **Основные темы**: автоматическое выделение ключевых тем

### 2. Персонализированные Ответы
- Генерация ответов на основе анализа эмоций
- Адаптация к группе эксперимента (confess/silent)
- Учет контекста разговора
- Поддержка многоязычности

### 3. Анализ Потока Разговора
- **Уровень вовлеченности**: high, medium, low
- **Качество разговора**: good, average, poor
- **Удовлетворенность пользователя**: high, medium, low
- **Прогресс эксперимента**: on_track, struggling, off_track

### 4. Мониторинг и Аналитика
- Оценка эффективности нуджинга
- Предсказание риска выхода из эксперимента
- Рекомендации для улучшения взаимодействия

## 🔧 Настройка

### 1. Получение API Ключа

1. Зарегистрируйтесь на [cloud.ru](https://cloud.ru)
2. Создайте проект
3. Получите API ключ
4. Скопируйте ключ

### 2. Конфигурация

```bash
# Обновите .env файл
CLOUD_RU_API_KEY=your_cloud_ru_token_here
LLM_MODEL=gpt-3.5-turbo
LLM_ENABLED=true
LLM_ANALYSIS_ENABLED=true
```

### 3. Запуск LLM Бота

```bash
# Запустить LLM бота
./llm-manage.sh start

# Обновить токен
./llm-manage.sh update-token your_cloud_ru_token

# Проверить статус
./llm-manage.sh status
```

## 📊 Структура Данных

### LLM Анализ
```json
{
  "emotion": "anxious",
  "intent": "question",
  "confidence": "medium",
  "persuasion_resistance": "high",
  "key_themes": ["uncertainty", "decision"],
  "suggested_response": "Понимаю ваши сомнения...",
  "nudging_effectiveness": "medium",
  "risk_of_dropout": "low"
}
```

### Анализ Потока Разговора
```json
{
  "engagement_level": "high",
  "conversation_quality": "good",
  "user_satisfaction": "high",
  "experiment_progress": "on_track",
  "recommendations": ["Продолжать текущий подход"]
}
```

## 🗄️ База Данных

### Новые Таблицы

#### `llm_analysis`
- `participant_id` - ID участника
- `user_message` - Сообщение пользователя
- `analysis_json` - JSON с результатами анализа
- `bot_response` - Ответ бота
- `timestamp` - Время анализа

#### `conversation_flow`
- `participant_id` - ID участника
- `flow_analysis_json` - JSON с анализом потока
- `timestamp` - Время анализа

## 🎯 Использование

### Команды Бота

- `/start` - Начать эксперимент с LLM анализом
- `/status` - Статус эксперимента
- `/llm_status` - Статус LLM анализа
- `/help` - Справка

### Управление

```bash
# Основные команды
./llm-manage.sh start          # Запуск
./llm-manage.sh stop           # Остановка
./llm-manage.sh restart        # Перезапуск
./llm-manage.sh status         # Статус
./llm-manage.sh logs           # Логи

# Анализ и данные
./llm-manage.sh check-analysis # Проверить анализ
./llm-manage.sh export-data    # Экспорт данных
./llm-manage.sh update-token   # Обновить токен
```

## 📈 Аналитика

### Метрики LLM Анализа

1. **Эмоциональная динамика** - изменение эмоций в ходе эксперимента
2. **Эффективность нуджинга** - оценка влияния на решения
3. **Качество взаимодействия** - удовлетворенность пользователей
4. **Риск выхода** - предсказание досрочного завершения

### Экспорт Данных

```bash
# Экспорт всех LLM данных
./llm-manage.sh export-data

# Файл: llm_analysis_export.json
{
  "export_timestamp": "2025-10-16T15:00:00",
  "total_analyses": 150,
  "analyses": [...]
}
```

## 🔒 Безопасность

- Все сообщения анонимизированы
- API ключи хранятся в переменных окружения
- Данные шифруются в базе данных
- Логирование без персональных данных

## 🚨 Устранение Неполадок

### Проблемы с API

```bash
# Проверить токен
./llm-manage.sh check-analysis

# Обновить токен
./llm-manage.sh update-token new_token

# Проверить логи
./llm-manage.sh logs
```

### Отключение LLM

```bash
# В .env файле
LLM_ENABLED=false
LLM_ANALYSIS_ENABLED=false

# Перезапуск
./llm-manage.sh restart
```

## 📚 Примеры Анализа

### Пример 1: Тревожный Пользователь
```
Сообщение: "Я не знаю, что делать... Это сложно"
Анализ: {
  "emotion": "anxious",
  "intent": "confusion",
  "confidence": "low",
  "risk_of_dropout": "high"
}
Ответ: "Понимаю ваши сомнения. Давайте разберем это пошагово..."
```

### Пример 2: Уверенный Пользователь
```
Сообщение: "Я готов к сотрудничеству!"
Анализ: {
  "emotion": "positive",
  "intent": "cooperate",
  "confidence": "high",
  "nudging_effectiveness": "high"
}
Ответ: "Отлично! Честность действительно важна в любых отношениях."
```

## 🔄 Интеграция с Существующим Ботом

LLM интеграция полностью совместима с существующим функционалом:

- ✅ Многоязычная поддержка
- ✅ Случайное распределение по группам
- ✅ Система нуджинга
- ✅ Пост-интерактивный опрос
- ✅ Безопасный сбор данных

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `./llm-manage.sh logs`
2. Проверьте статус: `./llm-manage.sh status`
3. Проверьте анализ: `./llm-manage.sh check-analysis`
4. Обновите токен: `./llm-manage.sh update-token`

---

**🎉 LLM интеграция готова к использованию!**
