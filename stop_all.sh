#!/bin/bash

# Скрипт для остановки всех компонентов

echo "================================"
echo "ОСТАНОВКА СИСТЕМЫ"
echo "================================"

# Функция для остановки процесса
stop_process() {
    local PID_FILE=$1
    local NAME=$2
    
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        
        if ps -p $PID > /dev/null 2>&1; then
            echo "Остановка $NAME (PID: $PID)..."
            kill $PID
            
            # Ждем завершения
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    echo "✅ $NAME остановлен"
                    rm $PID_FILE
                    return 0
                fi
                sleep 1
            done
            
            # Принудительная остановка
            echo "⚠️  Принудительная остановка $NAME"
            kill -9 $PID
            rm $PID_FILE
        else
            echo "❌ $NAME не запущен (PID: $PID)"
            rm $PID_FILE
        fi
    else
        echo "❌ PID файл $NAME не найден"
    fi
}

# Останавливаем все компоненты
stop_process ".student_bot.pid" "Студенческий бот"
stop_process ".admin_bot.pid" "Админский бот"
stop_process ".scheduler.pid" "Планировщик"

echo ""
echo "================================"
echo "✅ ВСЕ КОМПОНЕНТЫ ОСТАНОВЛЕНЫ"
echo "================================"
