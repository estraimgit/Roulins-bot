# Docker развертывание Prisoner's Dilemma Bot

## Предварительные требования

### На локальной машине:
- Docker и Docker Compose
- SSH доступ к серверу
- Git

### На сервере:
- Docker и Docker Compose
- SSH доступ
- Открытые порты 8443 (для webhook)

## Быстрое развертывание

### 1. Подготовка

```bash
# Клонируйте репозиторий
git clone git@github.com:estraimgit/Roulins-bot.git
cd Roulins-bot

# Создайте .env файл
cp production.env.example .env

# Отредактируйте .env файл
nano .env
```

### 2. Настройка .env файла

Обязательно настройте следующие переменные:

```bash
# Получите токен у @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Сгенерируйте сильный ключ шифрования (32+ символов)
ENCRYPTION_KEY=your_very_strong_32_character_key_here

# URL вашего сервера
WEBHOOK_URL=https://176.108.243.54:8443/webhook
```

### 3. Развертывание

```bash
# Запустите скрипт развертывания
./deploy.sh
```

## Ручное развертывание

### 1. Подготовка сервера

```bash
# Подключитесь к серверу
ssh user1@176.108.243.54

# Установите Docker (если не установлен)
sudo apt update
sudo apt install docker.io docker-compose

# Добавьте пользователя в группу docker
sudo usermod -aG docker user1

# Перелогиньтесь или выполните
newgrp docker
```

### 2. Копирование файлов

```bash
# Создайте директорию
mkdir -p /home/user1/prisoners-dilemma-bot
cd /home/user1/prisoners-dilemma-bot

# Скопируйте файлы проекта
scp -r /path/to/local/project/* user1@176.108.243.54:/home/user1/prisoners-dilemma-bot/
```

### 3. Настройка и запуск

```bash
# На сервере
cd /home/user1/prisoners-dilemma-bot

# Создайте .env файл
cp production.env.example .env
nano .env

# Создайте необходимые директории
mkdir -p data logs

# Соберите и запустите
docker-compose build
docker-compose up -d
```

## Управление ботом

### Использование скрипта управления

```bash
# Запуск
./server-manage.sh start

# Остановка
./server-manage.sh stop

# Перезапуск
./server-manage.sh restart

# Статус
./server-manage.sh status

# Логи
./server-manage.sh logs

# Обновление
./server-manage.sh update

# Подключение к контейнеру
./server-manage.sh shell

# Резервное копирование
./server-manage.sh backup
```

### Прямые команды Docker

```bash
# Подключение к серверу
ssh user1@176.108.243.54

# Переход в директорию
cd /home/user1/prisoners-dilemma-bot

# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка
docker-compose build --no-cache

# Перезапуск
docker-compose restart
```

## Мониторинг

### Проверка статуса

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f --tail=100
```

### Проверка работоспособности

```bash
# Проверка логов на ошибки
docker-compose logs | grep ERROR

# Проверка подключения к базе данных
docker-compose exec prisoners-dilemma-bot python -c "from utils.database import DatabaseManager; db = DatabaseManager(); print('DB OK')"

# Проверка статистики
docker-compose exec prisoners-dilemma-bot python -c "from utils.database import DatabaseManager; db = DatabaseManager(); print(db.get_experiment_statistics())"
```

## Резервное копирование

### Автоматическое резервное копирование

```bash
# Создание резервной копии
./server-manage.sh backup

# Или вручную
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && tar -czf backup-\$(date +%Y%m%d-%H%M%S).tar.gz data/ logs/"
```

### Восстановление из резервной копии

```bash
# Копирование резервной копии на сервер
scp backup-20241216-120000.tar.gz user1@176.108.243.54:/home/user1/prisoners-dilemma-bot/

# Восстановление
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && tar -xzf backup-20241216-120000.tar.gz"
```

## Обновление

### Обновление кода

```bash
# Обновление через скрипт
./deploy.sh

# Или вручную
git pull origin main
./deploy.sh
```

### Обновление зависимостей

```bash
# На сервере
ssh user1@176.108.243.54 "cd /home/user1/prisoners-dilemma-bot && docker-compose build --no-cache && docker-compose up -d"
```

## Безопасность

### Настройка файрвола

```bash
# На сервере
sudo ufw allow 22    # SSH
sudo ufw allow 8443  # Webhook
sudo ufw enable
```

### SSL сертификаты (для webhook)

```bash
# Установка certbot
sudo apt install certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Обновление .env
WEBHOOK_URL=https://your-domain.com:8443/webhook
```

## Устранение неполадок

### Проблемы с запуском

```bash
# Проверка логов
docker-compose logs

# Проверка конфигурации
docker-compose config

# Пересборка без кэша
docker-compose build --no-cache
```

### Проблемы с базой данных

```bash
# Проверка файлов базы данных
ls -la data/

# Проверка прав доступа
chmod 755 data/ logs/
```

### Проблемы с сетью

```bash
# Проверка портов
netstat -tlnp | grep 8443

# Проверка Docker сети
docker network ls
```

## Масштабирование

### Горизонтальное масштабирование

```yaml
# В docker-compose.yml
services:
  prisoners-dilemma-bot:
    deploy:
      replicas: 3
```

### Использование внешней базы данных

```yaml
# Добавить в docker-compose.yml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: prisoners_dilemma
      POSTGRES_USER: bot_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Мониторинг производительности

### Логирование

```bash
# Настройка ротации логов
sudo nano /etc/logrotate.d/prisoners-dilemma-bot
```

### Метрики

```bash
# Установка Prometheus (опционально)
docker run -d -p 9090:9090 prom/prometheus
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `./server-manage.sh logs`
2. Проверьте статус: `./server-manage.sh status`
3. Проверьте конфигурацию: `docker-compose config`
4. Создайте issue в репозитории GitHub
