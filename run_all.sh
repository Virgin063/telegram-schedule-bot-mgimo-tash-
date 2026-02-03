#!/bin/bash

# Скрипт для запуска всех компонентов системы

echo "================================"
echo "ЗАПУСК СИСТЕМЫ РАСПИСАНИЯ"
echo "================================"

# Проверяем .env файл
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте .env.example в .env и настройте:"
    echo "  cp .env.example .env"
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Активируем виртуальное окружение (если есть)
if [ -d "venv" ]; then
    echo "Активация виртуального окружения..."
    source venv/bin/activate
fi

# Инициализация БД
echo ""
echo "Инициализация базы данных..."
python init_db.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка инициализации БД"
    exit 1
fi

echo ""
echo "Запуск компонентов..."
echo ""

# Запускаем студенческого бота
echo "🤖 Запуск студенческого бота..."
python -m bots.student_bot.main > logs/student_bot.out 2>&1 &
STUDENT_BOT_PID=$!
echo "  PID: $STUDENT_BOT_PID"

# Небольшая задержка
sleep 2

# Запускаем админского бота
echo "🔐 Запуск админского бота..."
python -m bots.admin_bot.main > logs/admin_bot.out 2>&1 &
ADMIN_BOT_PID=$!
echo "  PID: $ADMIN_BOT_PID"

sleep 2

# Запускаем планировщик
echo "⏰ Запуск планировщика..."
python tasks/scheduler.py > logs/scheduler.out 2>&1 &
SCHEDULER_PID=$!
echo "  PID: $SCHEDULER_PID"

echo ""
echo "================================"
echo "✅ ВСЕ КОМПОНЕНТЫ ЗАПУЩЕНЫ"
echo "================================"
echo ""
echo "PIDs:"
echo "  Студенческий бот: $STUDENT_BOT_PID"
echo "  Админский бот:    $ADMIN_BOT_PID"
echo "  Планировщик:      $SCHEDULER_PID"
echo ""
echo "Логи:"
echo "  logs/student_bot.out"
echo "  logs/admin_bot.out"
echo "  logs/scheduler.out"
echo ""
echo "Для остановки используйте: ./stop_all.sh"
echo ""

# Сохраняем PIDs
echo $STUDENT_BOT_PID > .student_bot.pid
echo $ADMIN_BOT_PID > .admin_bot.pid
echo $SCHEDULER_PID > .scheduler.pid
