# Инструкции по настройке бота

## ✅ Развертывание завершено!

Бот успешно развернут на сервере `user1@176.108.243.54` в Docker контейнере.

## 🔧 Настройка токена бота

### 1. Получите токен от @BotFather

1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте команду `/newbot`
4. Следуйте инструкциям:
   - Введите имя бота (например: "Prisoner's Dilemma Experiment Bot")
   - Введите username бота (например: "prisoners_dilemma_bot")
5. Скопируйте полученный токен (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Обновите конфигурацию на сервере

```bash
# Подключитесь к серверу
ssh user1@176.108.243.54

# Перейдите в директорию проекта
cd /home/user1/prisoners-dilemma-bot

# Отредактируйте .env файл
nano .env

# Замените строку:
# BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
# На ваш реальный токен:
# BOT_TOKEN=ваш_реальный_токен_здесь
```

### 3. Запустите бота

```bash
# Вернитесь на локальную машину и запустите:
./server-manage.sh start
```

## 🎯 Проверка работы

### Проверка статуса
```bash
./server-manage.sh status
```

### Просмотр логов
```bash
./server-manage.sh logs
```

### Тестирование бота
1. Найдите вашего бота в Telegram по username
2. Отправьте команду `/start`
3. Выберите язык
4. Участвуйте в эксперименте

## 📊 Управление ботом

### Основные команды
```bash
./server-manage.sh start    # Запустить
./server-manage.sh stop     # Остановить
./server-manage.sh restart  # Перезапустить
./server-manage.sh status   # Статус
./server-manage.sh logs     # Логи
./server-manage.sh backup   # Резервная копия
```

### Административные команды
- `/status` - статистика эксперимента (только для администраторов)
- `/help` - справка

## 🔒 Безопасность

- Все данные шифруются
- Участники анонимизированы
- Логи сохраняются в `/app/logs/`
- База данных в `/app/data/`

## 📈 Мониторинг

### Просмотр статистики
```bash
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose exec prisoners-dilemma-bot python -c \"
from utils.database import DatabaseManager
db = DatabaseManager()
stats = db.get_experiment_statistics()
print('Статистика:', stats)
\""
```

### Экспорт данных
```bash
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose exec prisoners-dilemma-bot python -c \"
from utils.data_analysis import DataAnalyzer
analyzer = DataAnalyzer()
analyzer.export_data('experiment_data.json')
print('Данные экспортированы')
\""
```

## 🆘 Устранение неполадок

### Бот не отвечает
1. Проверьте токен: `./server-manage.sh logs`
2. Убедитесь, что бот не заблокирован
3. Проверьте статус: `./server-manage.sh status`

### Проблемы с базой данных
```bash
# Проверка файлов
ssh user1@176.108.243.54 "ls -la /home/user1/prisoners-dilemma-bot/data/"

# Пересоздание базы данных
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose exec prisoners-dilemma-bot python -c \"
from utils.database import DatabaseManager
db = DatabaseManager()
print('База данных пересоздана')
\""
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `./server-manage.sh logs`
2. Проверьте статус: `./server-manage.sh status`
3. Создайте issue в репозитории GitHub

---

**🎉 Поздравляем! Ваш экспериментальный бот готов к работе!**
