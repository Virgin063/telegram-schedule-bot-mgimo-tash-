# ⚡ Быстрый старт за 5 минут

## Что нужно подготовить:

### 1. Получить токены Telegram ботов (5 мин)

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Создайте 2 бота:
   ```
   /newbot
   Название: Расписание МГИМО
   Username: mgimo_schedule_bot
   ```
   Сохраните токен!
   
   ```
   /newbot
   Название: Расписание МГИМО Admin
   Username: mgimo_admin_bot
   ```
   Сохраните токен!

3. Узнайте свой Telegram ID через [@userinfobot](https://t.me/userinfobot)

### 2. Получить OpenAI API ключ (10 мин)

1. Регистрация: [platform.openai.com](https://platform.openai.com)
2. Создать API ключ: Settings → API Keys → Create new key
3. Пополнить баланс на $5 минимум
4. Сохранить ключ!

### 3. Настройка Google Drive (опционально, 2 мин) ⭐

**НОВЫЙ ПРОСТОЙ СПОСОБ!** Без настройки API!

**Вариант A: Публичная ссылка (2 минуты)** ✅ Рекомендуется
1. Откройте файл на Google Drive
2. Правый клик → "Поделиться" → "Изменить доступ"
3. Выберите "Любой, у кого есть ссылка" → Читатель
4. Копировать ссылку
5. Вставьте в `.env`: `GOOGLE_DRIVE_PUBLIC_URL=ваша_ссылка`

**Вариант Б: Без автосинхронизации** ⚡ Еще проще
- Просто загружайте файлы вручную через админ-бота
- Полный контроль, ничего настраивать не нужно

**Вариант В: Google Drive API (15 мин)** 🔧 Для продвинутых
- Только если нужна синхронизация нескольких файлов
- См. [SETUP.md](SETUP.md) → Шаг 4

---

## Установка и запуск

### Вариант 1: Docker (рекомендуется) 🐳

```bash
# 1. Установите Docker (если нет)
# Mac: https://docs.docker.com/desktop/install/mac-install/
# Windows: https://docs.docker.com/desktop/install/windows-install/
# Linux: https://docs.docker.com/engine/install/

# 2. Клонируйте проект
cd "расписание бот для ташкента"

# 3. Создайте .env файл
cp .env.example .env

# 4. Отредактируйте .env
# Откройте в текстовом редакторе и добавьте:
# - STUDENT_BOT_TOKEN=<токен из BotFather>
# - ADMIN_BOT_TOKEN=<токен из BotFather>
# - ADMIN_IDS=<ваш Telegram ID>
# - OPENAI_API_KEY=<ключ OpenAI>
# - DB_PASSWORD=<придумайте пароль>

# 5. Запустите!
docker-compose up -d

# 6. Проверьте логи
docker-compose logs -f

# Готово! 🎉
```

### Вариант 2: Локально (для разработки) 💻

```bash
# 1. Установите зависимости системы

# Mac:
brew install postgresql redis

# Ubuntu/Debian:
sudo apt install postgresql redis-server python3-pip

# 2. Установите Python пакеты
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# 3. Настройте .env (см. выше)
cp .env.example .env
# Отредактируйте .env

# 4. Запустите PostgreSQL и Redis
# Mac:
brew services start postgresql
brew services start redis

# Ubuntu:
sudo systemctl start postgresql redis

# 5. Инициализируйте БД
python init_db.py

# 6. Запустите все компоненты
./run_all.sh

# Готово! 🎉
```

---

## Первые шаги

### 1. Тест студенческого бота

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Выберите группу (например, "БИ(б)-23/1")
4. Нажмите "📅 Сегодня"

**Если нет расписания:**
- Загрузите через админ-бота (см. ниже)

### 2. Тест админского бота

1. Найдите админского бота в Telegram
2. Отправьте `/start`
3. Нажмите "📤 Загрузить файл"
4. Отправьте файл "БИ 3 курс.xlsx"
5. Дождитесь обработки (~1-2 мин)

**Что делает AI:**
- Читает все 19 недель
- Исправляет ошибки
- Сохраняет в БД

### 3. Проверка расписания

1. Вернитесь в студенческого бота
2. Нажмите "📅 Сегодня"
3. Должно появиться расписание!

---

## Проверка работы системы

```bash
# Проверка Docker
docker-compose ps

# Должно быть:
# ✅ schedule_postgres    running
# ✅ schedule_redis       running
# ✅ schedule_student_bot running
# ✅ schedule_admin_bot   running

# Проверка логов
docker-compose logs -f student_bot

# Проверка БД
docker-compose exec postgres psql -U schedule_user -d schedule_bot -c "SELECT COUNT(*) FROM users;"
```

---

## Частые проблемы

### "Cannot connect to database"
```bash
# Проверьте PostgreSQL
docker-compose ps postgres

# Перезапустите
docker-compose restart postgres
```

### "OpenAI API error"
- Проверьте ключ в `.env`
- Проверьте баланс на OpenAI
- Проверьте интернет-соединение

### "Bot doesn't respond"
```bash
# Посмотрите логи
docker-compose logs student_bot

# Перезапустите бота
docker-compose restart student_bot
```

---

## Что дальше?

1. **Настройте уведомления**
   - Откройте студенческого бота
   - Нажмите "⚙️ Настройки"
   - Включите нужные уведомления

2. **Настройте автосинхронизацию** (если нужна)
   - **Простой способ:** [GOOGLE_DRIVE_SIMPLE.md](GOOGLE_DRIVE_SIMPLE.md) - 2 минуты!
   - Или оставьте ручную загрузку через админ-бота
   - Система будет автоматически проверять обновления каждые 15 мин

3. **Добавьте других админов**
   - Получите их Telegram ID
   - Добавьте в `.env`: `ADMIN_IDS=123456789,987654321`
   - Перезапустите: `docker-compose restart admin_bot`

4. **Пригласите студентов**
   - Отправьте ссылку на бота: `https://t.me/ваш_бот`
   - Они смогут выбрать свою группу и начать пользоваться

---

## Полезные команды

### Docker
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f student_bot

# Очистка (ОСТОРОЖНО!)
docker-compose down -v  # Удалит БД!
```

### Локальный запуск
```bash
# Запуск всех компонентов
./run_all.sh

# Остановка
./stop_all.sh

# Логи
tail -f logs/student_bot.out
tail -f logs/admin_bot.out
tail -f logs/scheduler.out
```

---

## Структура проекта

```
📁 Главные файлы для редактирования:
├── .env                    ← Настройки (токены, пароли)
├── docker-compose.yml      ← Docker конфигурация
├── БИ 3 курс.xlsx         ← Пример расписания

📁 Документация:
├── README.md              ← Полное описание
├── QUICKSTART.md          ← Этот файл
├── SETUP.md               ← Детальная установка
├── GUIDE.md               ← Руководство пользователя
└── PROJECT_OVERVIEW.md    ← Обзор архитектуры
```

---

## Поддержка

- 📖 Полная документация: [README.md](README.md)
- 🛠 Детальная установка: [SETUP.md](SETUP.md)
- 📚 Руководство: [GUIDE.md](GUIDE.md)
- 🏗 Архитектура: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

---

**Готово!** Теперь у вас работает полнофункциональный бот расписания с AI! 🎉

Если что-то не работает - проверьте логи и документацию выше.
