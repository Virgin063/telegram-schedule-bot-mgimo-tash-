"""
Обработчики настроек
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from services.user_service import UserService
from bots.student_bot.keyboards import get_settings_keyboard, get_main_keyboard


user_service = UserService()


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "Настройки"
    
    Args:
        update: объект Update
        context: контекст
    """
    chat_id = update.effective_chat.id
    
    # Получаем пользователя
    user = user_service.get_user_by_chat_id(chat_id)
    
    if not user:
        await update.message.reply_text(
            "❌ Сначала выбери группу с помощью команды /start"
        )
        return
    
    # Формируем сообщение с настройками
    message = f"""
⚙️ <b>Настройки уведомлений</b>

Управляй своими уведомлениями:

<b>Утренние уведомления</b> (7:00)
Получай расписание на день каждое утро

<b>За 15 минут до пары</b>
Напоминание перед каждым занятием

<b>Об изменениях расписания</b>
Мгновенные уведомления при любых изменениях
"""
    
    # Отправляем с клавиатурой
    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            morning=user.notifications_morning,
            before_class=user.notifications_before_class,
            changes=user.notifications_changes
        )
    )
    
    logger.info(f"Пользователь {chat_id} открыл настройки")


async def toggle_notification_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик переключения настроек
    
    Args:
        update: объект Update
        context: контекст
    """
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    user = user_service.get_user_by_chat_id(chat_id)
    
    if not user:
        return
    
    # Определяем, какую настройку переключаем
    if query.data == "toggle_morning":
        user_service.update_notification_settings(
            chat_id=chat_id,
            morning=not user.notifications_morning
        )
        setting_name = "Утренние уведомления"
        new_state = not user.notifications_morning
        
    elif query.data == "toggle_before_class":
        user_service.update_notification_settings(
            chat_id=chat_id,
            before_class=not user.notifications_before_class
        )
        setting_name = "Уведомления за 15 минут"
        new_state = not user.notifications_before_class
        
    elif query.data == "toggle_changes":
        user_service.update_notification_settings(
            chat_id=chat_id,
            changes=not user.notifications_changes
        )
        setting_name = "Уведомления об изменениях"
        new_state = not user.notifications_changes
    
    elif query.data == "back_to_main":
        await query.edit_message_text(
            "👌 Настройки сохранены!",
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="Используй кнопки ниже:",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Обновляем пользователя
    user = user_service.get_user_by_chat_id(chat_id)
    
    # Обновляем клавиатуру
    message = f"""
⚙️ <b>Настройки уведомлений</b>

{setting_name}: {"✅ Включены" if new_state else "❌ Выключены"}

Управляй своими уведомлениями:

<b>Утренние уведомления</b> (7:00)
Получай расписание на день каждое утро

<b>За 15 минут до пары</b>
Напоминание перед каждым занятием

<b>Об изменениях расписания</b>
Мгновенные уведомления при любых изменениях
"""
    
    await query.edit_message_text(
        message,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            morning=user.notifications_morning,
            before_class=user.notifications_before_class,
            changes=user.notifications_changes
        )
    )
    
    logger.info(f"Пользователь {chat_id} изменил настройку: {query.data}")
