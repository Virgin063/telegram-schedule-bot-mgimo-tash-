# 🚀 Загрузка проекта на GitHub

## 📋 Шаг 1: Создайте репозиторий на GitHub

1. Откройте [GitHub](https://github.com)
2. Нажмите "+" → "New repository"
3. Заполните:
   - **Repository name**: `telegram-schedule-bot` (или любое название)
   - **Description**: `Telegram bot для расписания студентов`
   - **Visibility**: Private (рекомендуется)
   - ❌ **НЕ** создавайте README, .gitignore или license (у нас они уже есть)
4. Нажмите "Create repository"
5. **Скопируйте URL репозитория** (будет вида `https://github.com/username/repo.git`)

---

## 💻 Шаг 2: Инициализируйте Git и загрузите код

Выполните эти команды **в терминале** (в папке проекта):

### 1. Инициализируйте Git репозиторий
```bash
git init
```

### 2. Настройте Git (если еще не настроено)
```bash
git config user.name "Ваше Имя"
git config user.email "your.email@example.com"
```

### 3. Добавьте все файлы
```bash
git add .
```

### 4. Создайте первый коммит
```bash
git commit -m "Initial commit: Telegram Schedule Bot

- Студенческий бот с расписанием
- Админ-бот для управления
- AI парсинг Excel файлов с GPT-4o
- PostgreSQL + Redis
- Docker-ready"
```

### 5. Подключите к GitHub репозиторию
```bash
git branch -M main
git remote add origin https://github.com/ВАШ_USERNAME/ВАШ_РЕПОЗИТОРИЙ.git
```

### 6. Загрузите на GitHub
```bash
git push -u origin main
```

---

## ⚠️ ВАЖНО: Проверьте что НЕ загружается

Убедитесь что эти файлы **НЕ попадут** на GitHub (они в .gitignore):

- ✅ `.env` (ваши секреты)
- ✅ `venv/` (виртуальное окружение)
- ✅ `logs/` (логи)
- ✅ `*.db` (база данных)
- ✅ `credentials.json` (Google API ключи)

Проверить можно командой:
```bash
git status
```

---

## 🔐 Шаг 3: Настройте секреты на сервере

Когда будете разворачивать на сервере:

1. **НЕ копируйте** файл `.env` из GitHub
2. Создайте новый `.env` на сервере вручную
3. Скопируйте настройки из `.env.example`
4. Заполните реальными значениями (токены ботов, API ключи, и т.д.)

---

## 📝 Полезные команды Git

### Проверить статус
```bash
git status
```

### Посмотреть историю
```bash
git log --oneline
```

### Добавить изменения
```bash
git add .
git commit -m "Описание изменений"
git push
```

### Обновить код с GitHub
```bash
git pull
```

---

## 🎯 Готово!

После загрузки ваш проект будет доступен на GitHub по адресу:
`https://github.com/ВАШ_USERNAME/ВАШ_РЕПОЗИТОРИЙ`

Теперь можно:
- ✅ Клонировать на сервер
- ✅ Работать в команде
- ✅ Отслеживать изменения
- ✅ Делать бэкапы
