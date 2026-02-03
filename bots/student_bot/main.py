#!/usr/bin/env python3
"""
Студенческий бот
"""
import sys
from loguru import logger
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config.settings import settings
from config.database import init_db
from bots.student_bot.handlers import (
    start_handler,
    help_handler,
    group_selection_handler,
    today_handler,
    tomorrow_handler,
    week_handler,
    settings_handler,
    toggle_notification_handler
)


# Настройка логирования
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>"
)
logger.add(
    settings.log_file,
    level=settings.log_level,
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)


def main():
    """Главная функция"""
    logger.info("=" * 80)
    logger.info("ЗАПУСК СТУДЕНЧЕСКОГО БОТА")
    logger.info("=" * 80)
    
    # Инициализация БД
    try:
        init_db()
        logger.success("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        sys.exit(1)
    
    # Создаем приложение
    application = Application.builder().token(settings.student_bot_token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    
    # Регистрируем обработчики кнопок
    application.add_handler(MessageHandler(
        filters.Regex("^📅 Сегодня$"),
        today_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^➡️ Завтра$"),
        tomorrow_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📆 Неделя$"),
        week_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^⚙️ Настройки$"),
        settings_handler
    ))
    
    # Регистрируем обработчики callback
    application.add_handler(CallbackQueryHandler(
        group_selection_handler,
        pattern="^select_group_"
    ))
    application.add_handler(CallbackQueryHandler(
        toggle_notification_handler,
        pattern="^toggle_"
    ))
    application.add_handler(CallbackQueryHandler(
        toggle_notification_handler,
        pattern="^back_to_main$"
    ))
    
    # Запускаем бота
    logger.success("Студенческий бот запущен!")
    logger.info(f"Режим: {settings.sync_mode}")
    logger.info(f"Интервал синхронизации: {settings.sync_interval_minutes} мин")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
