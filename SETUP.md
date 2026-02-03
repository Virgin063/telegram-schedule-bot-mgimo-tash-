# 🚀 Инструкция по установке и запуску

## Шаг 1: Установка зависимостей

### 1.1 Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # На Mac/Linux
# или
venv\Scripts\activate  # На Windows
```

### 1.2 Установка пакетов

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Шаг 2: Настройка Telegram ботов

### 2.1 Создание ботов

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)

2. **Студенческий бот:**
   ```
   /newbot
   Название: Расписание МГИМО Ташкент
   Username: mgimo_schedule_bot
   ```
   Сохраните токен!

3. **Админский бот:**
   ```
   /newbot
   Название: Расписание МГИМО Admin
   Username: mgimo_admin_bot
   ```
   Сохраните токен!

### 2.2 Узнайте ваш Telegram ID

1. Найдите бота [@userinfobot](https://t.me/userinfobot)
2. Отправьте команду `/start`
3. Сохраните ваш ID

## Шаг 3: Настройка OpenAI API

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Перейдите в API keys
3. Создайте новый API ключ
4. Сохраните ключ (он больше не будет показан!)

💡 **Важно:** Пополните баланс минимум на $5

## Шаг 4: Настройка Google Drive API (опционально)

### 4.1 Создание проекта в Google Cloud

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com)
2. Создайте новый проект
3. Включите Google Drive API
4. Создайте учетные данные (Service Account)
5. Скачайте JSON файл credentials
6. Переименуйте его в `credentials.json` и поместите в корень проекта

### 4.2 Настройка доступа

1. Откройте `credentials.json`
2. Найдите `client_email`
3. Откройте папку с расписанием на Google Drive
4. Нажмите "Поделиться"
5. Добавьте этот email с правами на чтение

### 4.3 Получение ID папки

1. Откройте папку в Google Drive
2. Скопируйте ID из URL:
   ```
   https://drive.google.com/drive/folders/XXXXXXXXXXXXXXX
                                          ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                          Это ID папки
   ```

## Шаг 5: Настройка базы данных

### 5.1 Вариант 1: Локально (для разработки)

```bash
# Установка PostgreSQL (Mac)
brew install postgresql
brew services start postgresql

# Создание базы данных
createdb schedule_bot
```

### 5.2 Вариант 2: Docker (рекомендуется)

```bash
# Запуск PostgreSQL и Redis
docker-compose up -d postgres redis

# Проверка
docker-compose ps
```

## Шаг 6: Конфигурация

### 6.1 Создание .env файла

```bash
cp .env.example .env
```

### 6.2 Редактирование .env

Откройте `.env` и заполните:

```bash
# Токены ботов (из BotFather)
STUDENT_BOT_TOKEN=1234567890:AAbbCCddEEffGGhhIIjjKKllMMnnOOpp
ADMIN_BOT_TOKEN=9876543210:ZZyyXXwwVVuuTTssRRqqPPooNNmmLLkk

# Ваш Telegram ID (из @userinfobot)
ADMIN_IDS=123456789

# База данных
DATABASE_URL=postgresql://schedule_user:password123@localhost:5432/schedule_bot
DB_PASSWORD=password123

# OpenAI API
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Drive (опционально)
GOOGLE_DRIVE_FOLDER_ID=xxxxxxxxxxxxxxxxxxxxxxxxx

# Остальные настройки можно оставить по умолчанию
```

## Шаг 7: Инициализация базы данных

```bash
python init_db.py
```

Вы должны увидеть:
```
✅ База данных успешно инициализирована!
```

## Шаг 8: Тестирование парсера

```bash
python parsers/test_parser.py
```

Это протестирует AI парсинг на файле "БИ 3 курс.xlsx"

## Шаг 9: Запуск ботов

### 9.1 Вариант 1: Вручную (для разработки)

**Терминал 1 - Студенческий бот:**
```bash
python -m bots.student_bot.main
```

**Терминал 2 - Админский бот:**
```bash
python -m bots.admin_bot.main
```

**Терминал 3 - Планировщик:**
```bash
python tasks/scheduler.py
```

### 9.2 Вариант 2: Скрипт запуска

```bash
./run_all.sh
```

Для остановки:
```bash
./stop_all.sh
```

### 9.3 Вариант 3: Docker (для продакшена)

```bash
docker-compose up -d
```

Просмотр логов:
```bash
docker-compose logs -f
```

Остановка:
```bash
docker-compose down
```

## Шаг 10: Проверка работы

### 10.1 Проверка студенческого бота

1. Найдите вашего студенческого бота в Telegram
2. Отправьте `/start`
3. Выберите группу
4. Попробуйте кнопки "Сегодня", "Завтра", "Неделя"

### 10.2 Проверка админского бота

1. Найдите вашего админского бота в Telegram
2. Отправьте `/start`
3. Попробуйте:
   - `/status` - статус системы
   - `/stats` - статистика
   - Загрузите Excel файл

## 🐛 Решение проблем

### Проблема: "Database connection failed"

**Решение:**
```bash
# Проверьте, запущен ли PostgreSQL
docker-compose ps

# Или для локальной установки
psql -U postgres -c "SELECT 1"
```

### Проблема: "OpenAI API key invalid"

**Решение:**
1. Проверьте ключ в `.env`
2. Убедитесь, что на балансе OpenAI есть деньги
3. Проверьте лимиты API

### Проблема: "Google Drive authentication failed"

**Решение:**
1. Проверьте наличие `credentials.json`
2. Проверьте права доступа к папке
3. Убедитесь, что Google Drive API включен

### Проблема: "Bot doesn't respond"

**Решение:**
```bash
# Проверьте логи
tail -f logs/bot.log

# Или для Docker
docker-compose logs -f student_bot
```

## 📊 Мониторинг

### Логи

```bash
# Просмотр логов в реальном времени
tail -f logs/bot.log

# Последние 100 строк
tail -n 100 logs/bot.log

# Поиск ошибок
grep ERROR logs/bot.log
```

### Статус системы

В админском боте:
```
/status
```

## 🔄 Обновление

```bash
# Остановить боты
./stop_all.sh  # или docker-compose down

# Получить обновления (если используете git)
git pull

# Обновить зависимости
pip install -r requirements.txt

# Применить миграции БД (если есть)
# alembic upgrade head

# Запустить снова
./run_all.sh  # или docker-compose up -d
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи
2. Проверьте статус через `/status`
3. Посмотрите README.md

## ✅ Чеклист готовности

- [ ] PostgreSQL установлен и запущен
- [ ] Redis установлен и запущен
- [ ] .env файл настроен
- [ ] База данных инициализирована
- [ ] Токены ботов получены
- [ ] OpenAI API ключ получен
- [ ] Google Drive настроен (опционально)
- [ ] Боты запущены
- [ ] Тестовое сообщение отправлено

Готово! 🎉
