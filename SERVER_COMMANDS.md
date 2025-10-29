# Шпаргалка команд для сервера

## 🚀 Обновление бота

### Полное безопасное обновление
```bash
./safe_update.sh
```

### Быстрое обновление
```bash
./quick_update.sh
```

---

## 📊 Мониторинг

### Просмотр логов
```bash
# Основные логи бота
tail -f logs/bot.log

# Логи вывода
tail -f logs/bot_output.log

# Последние 50 строк
tail -n 50 logs/bot.log
```

### Проверка статуса бота
```bash
# Проверить, работает ли бот
ps aux | grep "python.*main.py"

# Проверить по PID файлу
ps -p $(cat bot.pid)
```

---

## ⚙️ Управление ботом

### Запуск
```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Запустить бота
nohup python main.py > logs/bot_output.log 2>&1 &
echo $! > bot.pid
```

### Остановка
```bash
# По PID файлу
kill $(cat bot.pid)

# Принудительная остановка
pkill -f "python.*main.py"
```

### Перезапуск
```bash
# Остановка и запуск
kill $(cat bot.pid) && sleep 2 && nohup python main.py > logs/bot_output.log 2>&1 & echo $! > bot.pid
```

---

## 🔧 Проверка конфигурации

### Просмотр настроек
```bash
# Показать все настройки (без комментариев)
cat .env | grep -v "^#" | grep -v "^$"

# Проверить конкретные параметры
grep -E "BOT_TOKEN|ENCRYPTION_KEY|ADMIN_USER_IDS" .env
```

### Валидация конфигурации
```bash
python -c "from config.settings import Config; Config.validate(); print('✅ OK')"
```

---

## 💾 Резервное копирование

### Создать резервную копию
```bash
# .env файл
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# База данных
cp -r data data_backup_$(date +%Y%m%d_%H%M%S)

# Все вместе
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .env data/
```

### Восстановить из резервной копии
```bash
# .env файл
cp .env.backup.YYYYMMDD_HHMMSS .env

# База данных
cp -r data_backup_YYYYMMDD_HHMMSS/* data/
```

---

## 🔍 Диагностика проблем

### Проверить системные ресурсы
```bash
# Использование CPU и памяти
top -p $(cat bot.pid)

# Дисковое пространство
df -h

# Использование памяти
free -h
```

### Проверить сетевое подключение
```bash
# Проверить доступность Telegram API
curl -I https://api.telegram.org

# Проверить доступность Cloud.ru API
curl -I https://foundation-models.api.cloud.ru
```

### Проверить права доступа
```bash
# Проверить права на директории
ls -la data/ logs/

# Исправить права (если нужно)
chmod 755 data/ logs/
chmod 644 data/*.db
```

---

## 📦 Управление зависимостями

### Обновить зависимости
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Показать установленные пакеты
```bash
pip list
```

### Проверить устаревшие пакеты
```bash
pip list --outdated
```

---

## 🔄 Git операции

### Обновить код
```bash
# Сохранить локальные изменения
git stash

# Загрузить обновления
git pull origin main

# Восстановить локальные изменения
git stash pop
```

### Проверить статус
```bash
git status
git log --oneline -5
```

### Откатить к предыдущей версии
```bash
git log  # Найти нужный коммит
git checkout <commit_hash>
```

---

## 🧪 Тестирование

### Проверить импорты
```bash
python -c "import telegram; import config.settings; print('✅ Imports OK')"
```

### Проверить базу данных
```bash
python -c "from utils.database import DatabaseManager; db = DatabaseManager(); print('✅ DB OK')"
```

### Тестовый запуск (foreground)
```bash
python main.py
# Ctrl+C для остановки
```

---

## 📱 Telegram команды

После запуска бота в Telegram:
- `/start` - Начать эксперимент
- `/help` - Помощь
- `/status` - Статус эксперимента
- `/admin help` - Админские команды (только для админов)

---

## ❓ Частые проблемы

### Бот не запускается
```bash
# 1. Проверить логи
tail -f logs/bot_output.log

# 2. Проверить конфигурацию
python -c "from config.settings import Config; Config.validate()"

# 3. Проверить зависимости
pip install -r requirements.txt

# 4. Проверить токен
grep BOT_TOKEN .env
```

### Ошибка "Module not found"
```bash
# Переустановить зависимости
pip install --force-reinstall -r requirements.txt
```

### База данных заблокирована
```bash
# Остановить все процессы бота
pkill -f "python.*main.py"

# Подождать несколько секунд
sleep 5

# Запустить снова
nohup python main.py > logs/bot_output.log 2>&1 & echo $! > bot.pid
```

---

## 🔐 Безопасность

### Проверить .gitignore
```bash
cat .gitignore | grep .env
```

### Проверить, что .env не в Git
```bash
git status | grep .env
# Не должно ничего выводить
```

### Изменить ключ шифрования (ОСТОРОЖНО!)
```bash
# 1. Сгенерировать новый ключ
python generate_key.py

# 2. Обновить .env файл
nano .env

# 3. ВАЖНО: Старые данные нельзя будет расшифровать!
```

---

## 📧 Контакты для поддержки

При критических проблемах:
1. Создайте резервную копию
2. Сохраните логи
3. Создайте issue на GitHub
4. Опишите проблему и приложите логи (без токенов!)

