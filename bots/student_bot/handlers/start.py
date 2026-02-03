"""
Обработчик команды /start
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from services.user_service import UserService
from bots.student_bot.keyboards import get_main_keyboard, get_group_selection_keyboard


user_service = UserService()

# Доступные группы (можно загрузить из БД)
AVAILABLE_GROUPS = [
    "БИ(б)-23/1",
    "БИ(б)-23/2",
    "БИ(б)-24/1",
    "БИ(б)-24/2",
]


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    
    Args:
        update: объект Update
        context: контекст
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"Команда /start от пользователя {chat_id}")
    
    # Проверяем, есть ли пользователь в БД
    db_user = user_service.get_user_by_chat_id(chat_id)
    
    if db_user and db_user.group_name:
        # Пользователь уже зарегистрирован
        await update.message.reply_text(
            f"👋 С возвращением, {user.first_name}!\n\n"
            f"Ваша группа: <b>{db_user.group_name}</b>\n\n"
            f"Используйте кнопки ниже для просмотра расписания.",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        # Новый пользователь - просим выбрать группу
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"Я помогу тебе с расписанием занятий.\n\n"
            f"Сначала выбери свою группу:",
            reply_markup=get_group_selection_keyboard(AVAILABLE_GROUPS)
        )


async def group_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора группы
    
    Args:
        update: объект Update
        context: контекст
    """
    query = update.callback_query
    await query.answer()
    
    # Извлекаем название группы из callback_data
    group_name = query.data.replace("select_group_", "")
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Создаем или обновляем пользователя
    user_service.get_or_create_user(
        chat_id=chat_id,
        group_name=group_name,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )
    
    logger.info(f"Пользователь {chat_id} выбрал группу {group_name}")
    
    # Отправляем подтверждение
    await query.edit_message_text(
        f"✅ Отлично! Ты выбрал группу <b>{group_name}</b>\n\n"
        f"Теперь ты можешь просматривать расписание и настроить уведомления.",
        parse_mode="HTML"
    )
    
    # Отправляем главное меню
    await context.bot.send_message(
        chat_id=chat_id,
        text="Используй кнопки ниже:",
        reply_markup=get_main_keyboard()
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /help
    
    Args:
        update: объект Update
        context: контекст
    """
    help_text = """
<b>📚 Помощь по боту</b>

<b>Основные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку

<b>Кнопки:</b>
📅 <b>Сегодня</b> - Расписание на сегодня
➡️ <b>Завтра</b> - Расписание на завтра
📆 <b>Неделя</b> - Расписание на неделю
⚙️ <b>Настройки</b> - Настройки уведомлений

<b>Уведомления:</b>
Ты можешь настроить:
• Утренние уведомления (каждое утро в 7:00)
• Напоминания за 15 минут до пары
• Уведомления об изменениях расписания

<b>Вопросы?</b>
Обратитесь в деканат или к администратору бота.
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
