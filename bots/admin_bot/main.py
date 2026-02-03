#!/usr/bin/env python3
"""
Админский бот
"""
import sys
from loguru import logger
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from config.settings import settings
from config.database import init_db
from bots.admin_bot.handlers import (
    start_handler,
    help_handler,
    upload_handler,
    upload_button_handler,
    status_handler,
    stats_handler,
    logs_handler,
    sync_handler,
    broadcast_handler
)


# Настройка логирования
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>"
)
logger.add(
    "logs/admin_bot.log",
    level=settings.log_level,
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)


def main():
    """Главная функция"""
    logger.info("=" * 80)
    logger.info("ЗАПУСК АДМИНСКОГО БОТА")
    logger.info("=" * 80)
    
    # Инициализация БД
    try:
        init_db()
        logger.success("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        sys.exit(1)
    
    # Создаем приложение
    application = Application.builder().token(settings.admin_bot_token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("status", status_handler))
    application.add_handler(CommandHandler("stats", stats_handler))
    application.add_handler(CommandHandler("logs", logs_handler))
    application.add_handler(CommandHandler("upload", upload_button_handler))
    application.add_handler(CommandHandler("sync", sync_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    
    # Регистрируем обработчики кнопок
    application.add_handler(MessageHandler(
        filters.Regex("^📊 Статус$"),
        status_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📈 Статистика$"),
        stats_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📝 Логи$"),
        logs_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📤 Загрузить файл$"),
        upload_button_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^🔄 Синхронизация$"),
        sync_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📢 Рассылка$"),
        broadcast_handler
    ))
    
    # Обработчик документов (загрузка файлов)
    application.add_handler(MessageHandler(
        filters.Document.FileExtension("xlsx") | filters.Document.FileExtension("xls"),
        upload_handler
    ))
    
    # Запускаем бота
    logger.success("Админский бот запущен!")
    logger.info(f"Админы: {settings.admin_ids}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
