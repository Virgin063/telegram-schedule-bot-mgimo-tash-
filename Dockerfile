FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Устанавливаем переменную окружения для Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# По умолчанию запускаем студенческого бота
CMD ["python", "-m", "bots.student_bot.main"]
