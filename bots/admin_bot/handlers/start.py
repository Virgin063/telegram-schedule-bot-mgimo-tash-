"""
Обработчик команды /start для админского бота
"""
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from config.settings import settings


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    return user_id in settings.admin_ids


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    
    Args:
        update: объект Update
        context: контекст
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Проверяем, является ли пользователь админом
    if not is_admin(user.id):
        await update.message.reply_text(
            "❌ У вас нет доступа к этому боту."
        )
        logger.warning(f"Попытка доступа не-админа: {chat_id}")
        return
    
    keyboard = [
        ["📊 Статус", "📤 Загрузить файл"],
        ["🔄 Синхронизация", "📝 Логи"],
        ["📈 Статистика", "📢 Рассылка"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"🔐 <b>Панель администратора</b>\n\n"
        f"Доступные команды:\n"
        f"📊 Статус - статус системы\n"
        f"📤 Загрузить файл - загрузить Excel\n"
        f"🔄 Синхронизация - принудительная синхронизация\n"
        f"📝 Логи - просмотр логов\n"
        f"📈 Статистика - статистика пользователей\n"
        f"📢 Рассылка - отправить сообщение всем",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    logger.info(f"Админ {chat_id} запустил бота")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /help
    
    Args:
        update: объект Update
        context: контекст
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        return
    
    help_text = """
<b>🔐 Справка для администратора</b>

<b>Команды:</b>
/start - Начать работу
/help - Эта справка
/status - Статус системы
/upload - Загрузить Excel файл
/sync - Принудительная синхронизация
/logs - Показать последние логи
/stats - Статистика пользователей
/broadcast - Рассылка сообщений

<b>Загрузка файла:</b>
1. Нажмите "📤 Загрузить файл"
2. Отправьте Excel файл с расписанием
3. Бот автоматически распарсит и сохранит

<b>Синхронизация:</b>
- Автоматическая: каждые {sync_interval} минут
- Ручная: через команду /sync

<b>Логи:</b>
Показывают последние 20 записей логов
- ✅ Успешные операции
- ⚠️ Предупреждения
- ❌ Ошибки

<b>Статистика:</b>
- Количество пользователей
- Активные пользователи
- Распределение по группам
""".format(sync_interval=settings.sync_interval_minutes)
    
    await update.message.reply_text(
        help_text,
        parse_mode="HTML"
    )
