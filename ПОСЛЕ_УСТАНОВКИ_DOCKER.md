# 🚀 Запуск после установки Docker

## Когда Docker будет установлен, выполните:

### 1. Проверка Docker
```bash
docker --version
docker-compose --version
```

Должны увидеть версии!

### 2. Создание директории для логов
```bash
mkdir -p logs
```

### 3. Запуск базы данных и Redis
```bash
docker-compose up -d postgres redis
```

Подождите 10 секунд, пока они запустятся.

### 4. Проверка статуса
```bash
docker-compose ps
```

Должны увидеть:
- ✅ postgres running
- ✅ redis running

### 5. Создание виртуального окружения Python
```bash
python3 -m venv venv
source venv/bin/activate
```

### 6. Установка Python пакетов
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Это займет ~5 минут.

### 7. Инициализация базы данных
```bash
python init_db.py
```

Должны увидеть:
```
✅ База данных успешно инициализирована!
```

### 8. Тест парсера (опционально)
```bash
python parsers/test_parser.py
```

Это протестирует AI парсинг на примере файла.

### 9. Запуск ботов!

**Терминал 1 - Студенческий бот:**
```bash
python -m bots.student_bot.main
```

**Терминал 2 - Админский бот (откройте новое окно терминала):**
```bash
cd "Desktop/Моя жизнь/CodeZone/расписание бот для ташкента"
source venv/bin/activate
python -m bots.admin_bot.main
```

### 10. Проверка работы!

1. Найдите студенческого бота в Telegram
2. Отправьте `/start`
3. Найдите админского бота
4. Отправьте `/start`

---

## 🎉 Готово!

Система запущена!

**Что дальше:**
1. Скачайте ваш Excel файл из Google Sheets
2. Загрузите через админ-бота
3. Проверьте расписание в студенческом боте

---

## ⚠️ Возможные проблемы

### "Cannot connect to database"
```bash
# Проверьте, запущен ли PostgreSQL
docker-compose ps postgres

# Перезапустите если нужно
docker-compose restart postgres
```

### "ModuleNotFoundError"
```bash
# Убедитесь, что виртуальное окружение активно
source venv/bin/activate

# Переустановите пакеты
pip install -r requirements.txt
```

### "Bot token is invalid"
- Проверьте токены в `.env` файле
- Убедитесь, что нет лишних пробелов
