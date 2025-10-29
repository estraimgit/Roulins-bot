# Инструкция по безопасному обновлению бота на сервере

## 🚀 Автоматическое обновление (рекомендуется)

### Шаг 1: Подключитесь к серверу
```bash
ssh your_user@your_server
cd /path/to/Roulins_Bot
```

### Шаг 2: Запустите скрипт обновления
```bash
chmod +x safe_update.sh
./safe_update.sh
```

Скрипт автоматически:
- ✅ Создаст резервные копии .env и базы данных
- ✅ Остановит текущего бота
- ✅ Загрузит обновления из Git
- ✅ Восстановит ваши настройки
- ✅ Установит новые зависимости
- ✅ Запустит обновленного бота

---

## 🔧 Ручное обновление (если автоматическое не работает)

### Шаг 1: Подключение к серверу
```bash
ssh your_user@your_server
cd /path/to/Roulins_Bot
```

### Шаг 2: Создание резервных копий

#### Резервная копия .env файла
```bash
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Резервная копия .env создана"
```

#### Резервная копия базы данных
```bash
BACKUP_DIR="data_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r data/* "$BACKUP_DIR/"
echo "✅ Резервная копия базы данных создана в $BACKUP_DIR"
```

### Шаг 3: Остановка бота
```bash
# Найти процесс бота
ps aux | grep "python.*main.py"

# Остановить бота (замените PID на реальный)
kill <PID>

# Или остановить все процессы бота
pkill -f "python.*main.py"

# Проверить, что бот остановлен
ps aux | grep "python.*main.py"
```

### Шаг 4: Сохранение текущих настроек
```bash
# Сохранить .env во временный файл
cp .env .env.temp
```

### Шаг 5: Загрузка обновлений
```bash
# Сохранить локальные изменения (если есть)
git stash

# Загрузить обновления
git pull origin main

# Если были конфликты, разрешите их
```

### Шаг 6: Восстановление настроек
```bash
# Восстановить .env файл
mv .env.temp .env

# Проверить, что все настройки на месте
cat .env | grep -E "BOT_TOKEN|ENCRYPTION_KEY|ADMIN_USER_IDS"
```

### Шаг 7: Обновление зависимостей
```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Обновить pip
pip install --upgrade pip

# Установить/обновить зависимости
pip install -r requirements.txt
```

### Шаг 8: Проверка конфигурации
```bash
# Проверить валидность конфигурации
python -c "from config.settings import Config; Config.validate(); print('✅ Конфигурация валидна')"
```

Если увидите ошибки, проверьте файл .env:
```bash
nano .env
```

### Шаг 9: Создание необходимых директорий
```bash
mkdir -p data logs
```

### Шаг 10: Запуск бота
```bash
# Запуск в фоновом режиме
nohup python main.py > logs/bot_output.log 2>&1 &

# Сохранить PID процесса
echo $! > bot.pid

# Проверить, что бот запустился
tail -f logs/bot_output.log
```

### Шаг 11: Проверка работоспособности
```bash
# Проверить процесс
ps aux | grep "python.*main.py"

# Проверить логи
tail -f logs/bot.log

# Проверить логи вывода
tail -f logs/bot_output.log
```

---

## 📊 Полезные команды

### Просмотр логов
```bash
# Логи бота
tail -f logs/bot.log

# Логи вывода
tail -f logs/bot_output.log

# Последние 100 строк
tail -n 100 logs/bot.log
```

### Управление ботом
```bash
# Остановка бота
kill $(cat bot.pid)

# Перезапуск бота
kill $(cat bot.pid) && nohup python main.py > logs/bot_output.log 2>&1 & echo $! > bot.pid

# Проверка статуса
ps -p $(cat bot.pid)
```

### Проверка конфигурации
```bash
# Проверить .env
cat .env | grep -v "^#" | grep -v "^$"

# Проверить валидность
python -c "from config.settings import Config; Config.validate()"
```

---

## 🔄 Откат к предыдущей версии

Если что-то пошло не так:

### Шаг 1: Остановите бота
```bash
pkill -f "python.*main.py"
```

### Шаг 2: Откатите Git
```bash
git stash
git log  # Найдите нужный коммит
git checkout <commit_hash>
```

### Шаг 3: Восстановите резервные копии
```bash
# Восстановить .env
cp .env.backup.* .env

# Восстановить базу данных (если нужно)
cp data_backup_*/* data/
```

### Шаг 4: Запустите бота
```bash
source venv/bin/activate
nohup python main.py > logs/bot_output.log 2>&1 &
```

---

## ❓ Проблемы и решения

### Проблема: Бот не запускается
**Решение:**
1. Проверьте логи: `tail -f logs/bot_output.log`
2. Проверьте конфигурацию: `python -c "from config.settings import Config; Config.validate()"`
3. Проверьте зависимости: `pip install -r requirements.txt`

### Проблема: Ошибка валидации конфигурации
**Решение:**
1. Проверьте .env файл: `cat .env`
2. Убедитесь, что все обязательные параметры заданы:
   - `BOT_TOKEN`
   - `ENCRYPTION_KEY` (32+ символов)
3. Восстановите из резервной копии: `cp .env.backup.* .env`

### Проблема: База данных не работает
**Решение:**
1. Проверьте права доступа: `ls -la data/`
2. Восстановите из резервной копии: `cp data_backup_*/* data/`
3. Создайте новую базу (ВНИМАНИЕ: потеряете данные): `rm data/*.db`

### Проблема: Git конфликты
**Решение:**
```bash
git stash
git pull origin main
# Если нужно, восстановите изменения:
git stash pop
# Разрешите конфликты вручную
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в `logs/bot.log` и `logs/bot_output.log`
2. Убедитесь, что конфигурация валидна
3. Проверьте, что все зависимости установлены
4. Создайте issue в GitHub репозитории

---

## ✅ Чеклист обновления

- [ ] Создана резервная копия .env
- [ ] Создана резервная копия базы данных
- [ ] Бот остановлен
- [ ] Обновления загружены из Git
- [ ] .env файл восстановлен
- [ ] Зависимости установлены
- [ ] Конфигурация проверена
- [ ] Бот запущен
- [ ] Логи проверены
- [ ] Бот работает корректно

