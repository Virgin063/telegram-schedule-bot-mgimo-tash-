"""
Обработчики расписания
"""
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta, date
from loguru import logger

from services.user_service import UserService
from services.schedule_service import ScheduleService
from utils.formatters import ScheduleFormatter
from bots.student_bot.keyboards import get_main_keyboard


user_service = UserService()
schedule_service = ScheduleService()
formatter = ScheduleFormatter()


async def today_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "Сегодня"
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        chat_id = update.effective_chat.id
        
        # Получаем пользователя
        user = user_service.get_user_by_chat_id(chat_id)
        
        if not user or not user.group_name:
            await update.message.reply_text(
                "❌ Сначала выбери группу с помощью команды /start"
            )
            return
        
        # Получаем расписание на сегодня
        today = date.today()
        schedule = schedule_service.get_schedule_for_day(user.group_name, today)
        
        # Форматируем и отправляем
        message = formatter.format_schedule_for_day(schedule, today)
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"Пользователь {chat_id} запросил расписание на сегодня")
        
    except Exception as e:
        logger.error(f"Ошибка в today_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении расписания:\n{str(e)[:100]}"
        )


async def tomorrow_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "Завтра"
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        chat_id = update.effective_chat.id
        
        # Получаем пользователя
        user = user_service.get_user_by_chat_id(chat_id)
        
        if not user or not user.group_name:
            await update.message.reply_text(
                "❌ Сначала выбери группу с помощью команды /start"
            )
            return
        
        # Получаем расписание на завтра
        tomorrow = date.today() + timedelta(days=1)
        schedule = schedule_service.get_schedule_for_day(user.group_name, tomorrow)
        
        # Форматируем и отправляем
        message = formatter.format_schedule_for_day(schedule, tomorrow)
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"Пользователь {chat_id} запросил расписание на завтра")
        
    except Exception as e:
        logger.error(f"Ошибка в tomorrow_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении расписания:\n{str(e)[:100]}"
        )


async def week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "Неделя"
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        chat_id = update.effective_chat.id
        
        # Получаем пользователя
        user = user_service.get_user_by_chat_id(chat_id)
        
        if not user or not user.group_name:
            await update.message.reply_text(
                "❌ Сначала выбери группу с помощью команды /start"
            )
            return
        
        # Получаем начало текущей недели (понедельник)
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        
        # Получаем расписание на неделю
        schedule_by_days = schedule_service.get_schedule_for_week(user.group_name, monday)
        
        # Форматируем и отправляем
        message = formatter.format_schedule_for_week(schedule_by_days, monday)
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"Пользователь {chat_id} запросил расписание на неделю")
        
    except Exception as e:
        logger.error(f"Ошибка в week_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении расписания:\n{str(e)[:100]}"
        )
