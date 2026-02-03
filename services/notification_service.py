"""
Сервис уведомлений
"""
from typing import List
from datetime import datetime, date, time, timedelta
from telegram import Bot
from loguru import logger

from config.settings import settings
from services.user_service import UserService
from services.schedule_service import ScheduleService
from utils.formatters import ScheduleFormatter
from models.schedule_change import ScheduleChange


class NotificationService:
    """Сервис для отправки уведомлений"""
    
    def __init__(self, bot_token: str = None):
        """
        Инициализация сервиса
        
        Args:
            bot_token: токен бота (по умолчанию - студенческий)
        """
        self.bot = Bot(token=bot_token or settings.student_bot_token)
        self.user_service = UserService()
        self.schedule_service = ScheduleService()
        self.formatter = ScheduleFormatter()
    
    async def send_morning_notifications(self):
        """Отправляет утренние уведомления всем пользователям"""
        logger.info("Начинаем отправку утренних уведомлений")
        
        # Получаем пользователей с включенными утренними уведомлениями
        users = self.user_service.get_users_with_morning_notifications()
        
        today = date.today()
        sent_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Получаем расписание на сегодня
                schedule = self.schedule_service.get_schedule_for_day(
                    user.group_name,
                    today
                )
                
                # Форматируем сообщение
                message = "🌅 <b>Доброе утро!</b>\n\n"
                message += self.formatter.format_schedule_for_day(schedule, today)
                
                # Отправляем
                await self.bot.send_message(
                    chat_id=user.chat_id,
                    text=message,
                    parse_mode="HTML"
                )
                
                sent_count += 1
                
                # Небольшая задержка для избежания лимитов
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Ошибка отправки утреннего уведомления пользователю {user.chat_id}: {e}")
                error_count += 1
        
        logger.success(f"Утренние уведомления отправлены: {sent_count} успешно, {error_count} ошибок")
    
    async def send_before_class_notification(
        self,
        user_chat_id: int,
        class_item
    ):
        """
        Отправляет уведомление за 15 минут до пары
        
        Args:
            user_chat_id: chat_id пользователя
            class_item: занятие
        """
        try:
            message = f"""
🔔 <b>Напоминание о паре</b>

Через 15 минут начинается:
{self.formatter._format_class(class_item)}
"""
            
            await self.bot.send_message(
                chat_id=user_chat_id,
                text=message,
                parse_mode="HTML"
            )
            
            logger.info(f"Уведомление о паре отправлено пользователю {user_chat_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о паре: {e}")
    
    async def send_change_notification(
        self,
        group_name: str,
        change: dict
    ):
        """
        Отправляет уведомление об изменении расписания
        
        Args:
            group_name: название группы
            change: изменение
        """
        logger.info(f"Отправка уведомления об изменении для группы {group_name}")
        
        # Получаем пользователей группы с включенными уведомлениями
        users = self.user_service.get_users_by_group(group_name)
        users = [u for u in users if u.notifications_changes]
        
        sent_count = 0
        error_count = 0
        
        # Форматируем сообщение
        message = "⚠️ <b>Изменение в расписании!</b>\n\n"
        message += self.formatter.format_class_change(change)
        
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.chat_id,
                    text=message,
                    parse_mode="HTML"
                )
                
                sent_count += 1
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления об изменении: {e}")
                error_count += 1
        
        logger.success(f"Уведомления об изменении отправлены: {sent_count} успешно, {error_count} ошибок")
    
    async def broadcast_message(
        self,
        message: str,
        group_name: str = None
    ):
        """
        Рассылка сообщения всем пользователям или конкретной группе
        
        Args:
            message: текст сообщения
            group_name: название группы (если None - всем)
        """
        logger.info(f"Начинаем рассылку сообщения (группа: {group_name or 'все'})")
        
        if group_name:
            users = self.user_service.get_users_by_group(group_name)
        else:
            users = self.user_service.get_all_users()
        
        sent_count = 0
        error_count = 0
        
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.chat_id,
                    text=message,
                    parse_mode="HTML"
                )
                
                sent_count += 1
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Ошибка рассылки пользователю {user.chat_id}: {e}")
                error_count += 1
        
        logger.success(f"Рассылка завершена: {sent_count} успешно, {error_count} ошибок")
        
        return sent_count, error_count


# Для совместимости с asyncio
import asyncio
