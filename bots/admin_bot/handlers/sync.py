"""
Обработчики синхронизации
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from bots.admin_bot.handlers.start import is_admin


async def sync_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик принудительной синхронизации
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        await update.message.reply_text(
            "🔄 <b>Принудительная синхронизация</b>\n\n"
            "⚠️ Эта функция пока в разработке.\n\n"
            "Автоматическая синхронизация работает по расписанию.\n"
            "Для обновления расписания используйте:\n"
            "📤 <b>Загрузить файл</b>",
            parse_mode="HTML"
        )
        
        logger.info(f"Админ {user.id} запросил синхронизацию")
        
    except Exception as e:
        logger.error(f"Ошибка в sync_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при запуске синхронизации:\n{str(e)[:100]}"
        )


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик рассылки
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        await update.message.reply_text(
            "📢 <b>Рассылка сообщений</b>\n\n"
            "⚠️ Эта функция пока в разработке.\n\n"
            "Запланировано:\n"
            "• Рассылка всем пользователям\n"
            "• Рассылка по группам\n"
            "• Отложенная рассылка\n"
            "• Предпросмотр сообщения",
            parse_mode="HTML"
        )
        
        logger.info(f"Админ {user.id} открыл рассылку")
        
    except Exception as e:
        logger.error(f"Ошибка в broadcast_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при открытии рассылки:\n{str(e)[:100]}"
        )
