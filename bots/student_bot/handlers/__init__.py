"""
Обработчики студенческого бота
"""
from bots.student_bot.handlers.start import (
    start_handler,
    help_handler,
    group_selection_handler
)
from bots.student_bot.handlers.schedule import (
    today_handler,
    tomorrow_handler,
    week_handler
)
from bots.student_bot.handlers.settings import (
    settings_handler,
    toggle_notification_handler
)

__all__ = [
    "start_handler",
    "help_handler",
    "group_selection_handler",
    "today_handler",
    "tomorrow_handler",
    "week_handler",
    "settings_handler",
    "toggle_notification_handler",
]
