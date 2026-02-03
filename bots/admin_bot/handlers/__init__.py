"""
Обработчики админского бота
"""
from bots.admin_bot.handlers.start import start_handler, help_handler, is_admin
from bots.admin_bot.handlers.upload import upload_handler, upload_button_handler
from bots.admin_bot.handlers.stats import status_handler, stats_handler, logs_handler
from bots.admin_bot.handlers.sync import sync_handler, broadcast_handler

__all__ = [
    "start_handler",
    "help_handler",
    "is_admin",
    "upload_handler",
    "upload_button_handler",
    "status_handler",
    "stats_handler",
    "logs_handler",
    "sync_handler",
    "broadcast_handler"
]
