# 📅 Бот расписания для университета

> Telegram бот для автоматического управления расписанием студентов МГИМО Ташкент с AI-парсингом Excel файлов

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green.svg)](https://openai.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Возможности

### Студенческий бот
- 📅 Просмотр расписания (на сегодня, завтра, неделю)
- 🔔 Настраиваемые уведомления:
  - Утренние уведомления с расписанием на день
  - Напоминание за 15 минут до пары
  - Мгновенные уведомления об изменениях расписания
- 👥 Выбор группы при регистрации
- ⚙️ Управление настройками уведомлений

### Админский бот
- 📤 Ручная загрузка Excel файлов
- 📊 Статус системы и логи
- 🔄 Принудительная синхронизация
- 📈 Статистика пользователей
- 📢 Рассылка сообщений

### Система
- 🤖 **AI-парсинг** расписания через GPT-4o
- ☁️ Автоматическая синхронизация с Google Drive
- 🔍 Обнаружение изменений в расписании
- 📦 Кеширование для быстрой работы
- 🐳 Docker-контейнеризация

## 🏗️ Архитектура

```
расписание-бот/
├── config/              # Конфигурация
├── models/              # Модели базы данных
├── parsers/             # AI парсинг Excel
├── bots/                # Telegram боты
│   ├── student_bot/     # Бот для студентов
│   └── admin_bot/       # Бот для админов
├── services/            # Бизнес-логика
├── tasks/               # Фоновые задачи
└── utils/               # Утилиты
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить пакеты
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
# Копировать пример конфигурации
cp .env.example .env

# Отредактировать .env и добавить:
# - Токены Telegram ботов
# - OpenAI API ключ
# - Настройки базы данных
# - Google Drive credentials
```

### 3. Настройка базы данных

```bash
# Запустить PostgreSQL (через Docker)
docker-compose up -d postgres redis

# Применить миграции
alembic upgrade head
```

### 4. Запуск ботов

```bash
# Студенческий бот
python -m bots.student_bot.main

# Админский бот (в отдельном терминале)
python -m bots.admin_bot.main

# Планировщик задач (в отдельном терминале)
python -m tasks.scheduler
```

## 🔧 Конфигурация

### Telegram боты

Получить токены через [@BotFather](https://t.me/BotFather):

1. Создать студенческого бота: `/newbot`
2. Создать админского бота: `/newbot`
3. Сохранить токены в `.env`

### OpenAI API

1. Зарегистрироваться на [platform.openai.com](https://platform.openai.com)
2. Создать API ключ
3. Добавить в `.env`: `OPENAI_API_KEY=sk-...`

### Google Drive API

1. Создать проект в [Google Cloud Console](https://console.cloud.google.com)
2. Включить Google Drive API
3. Создать credentials (Service Account)
4. Скачать `credentials.json`
5. Добавить Service Account email в папку с расписанием (доступ на чтение)

## 📊 База данных

### Таблицы

- `users` - Студенты и их настройки
- `schedule` - Расписание занятий
- `schedule_changes` - История изменений
- `sync_logs` - Логи синхронизации
- `notifications` - Очередь уведомлений

### Миграции

```bash
# Создать миграцию
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Откатить
alembic downgrade -1
```

## 🐳 Docker

```bash
# Запустить все сервисы
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановить
docker-compose down
```

## 📝 Использование

### Студенческий бот

1. Старт: `/start`
2. Выбрать группу
3. Команды:
   - `📅 Сегодня` - расписание на сегодня
   - `➡️ Завтра` - расписание на завтра
   - `📆 Неделя` - расписание на неделю
   - `⚙️ Настройки` - управление уведомлениями

### Админский бот

1. Старт: `/start`
2. Команды:
   - `/upload` - загрузить Excel файл
   - `/status` - статус системы
   - `/force_sync` - принудительная синхронизация
   - `/logs` - просмотр логов
   - `/stats` - статистика
   - `/broadcast` - рассылка

## 🔍 AI Парсинг

Система использует GPT-4o для интеллектуального парсинга Excel файлов:

- ✅ Определяет структуру таблицы
- ✅ Исправляет опечатки
- ✅ Распознает ФИО в неправильных графах
- ✅ Стандартизирует форматы
- ✅ Выявляет аномалии

## 📈 Мониторинг

### Логи

```bash
# Просмотр логов
tail -f logs/bot.log

# Логи через Docker
docker-compose logs -f student_bot
```

### Статистика

Доступна через админского бота: `/stats`

## 🛠️ Разработка

### Структура кода

- Используем **async/await** для асинхронности
- **SQLAlchemy ORM** для базы данных
- **Pydantic** для валидации данных
- **Loguru** для логирования

### Тестирование

```bash
# Запустить тесты
pytest

# С покрытием
pytest --cov=.

# Конкретный тест
pytest tests/test_parser.py
```

### Code style

```bash
# Форматирование
black .

# Линтер
flake8 .

# Type checking
mypy .
```

## 📦 Деплой

### На VPS

1. Клонировать репозиторий
2. Настроить `.env`
3. Запустить через Docker Compose
4. Настроить Nginx (опционально)
5. Настроить SSL (Let's Encrypt)

### Бэкап

```bash
# Бэкап БД
docker-compose exec postgres pg_dump -U schedule_user schedule_bot > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U schedule_user schedule_bot < backup.sql
```

## 📞 Поддержка

При возникновении проблем:

1. Проверить логи: `logs/bot.log`
2. Проверить статус: `/status` в админ боте
3. Проверить синхронизацию: `/force_sync`

## 📄 Лицензия

MIT License

## 👥 Авторы

Разработано для университета в Ташкенте 🇺🇿
