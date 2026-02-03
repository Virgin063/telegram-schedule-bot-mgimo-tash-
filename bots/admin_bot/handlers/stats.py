"""
Обработчики статистики и логов
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

from config.database import get_db
from models.user import User
from models.schedule import Schedule
from models.sync_log import SyncLog, SyncStatus
from bots.admin_bot.handlers.start import is_admin


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /status
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        with get_db() as db:
            # Последняя синхронизация
            last_sync = db.query(SyncLog).order_by(
                SyncLog.synced_at.desc()
            ).first()
            
            if last_sync:
                db.expunge(last_sync)
            
            # Количество пользователей
            total_users = db.query(User).count()
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            active_users = db.query(User).filter(
                User.last_active >= week_ago
            ).count()
            
            # Количество расписания
            total_schedule = db.query(Schedule).count()
            groups_count = db.query(func.count(func.distinct(Schedule.group_name))).scalar()
            
            # Последние ошибки
            recent_errors = db.query(SyncLog).filter(
                SyncLog.status == SyncStatus.ERROR
            ).order_by(SyncLog.synced_at.desc()).limit(3).all()
            
            for error in recent_errors:
                db.expunge(error)
        
        # Формируем сообщение
        status_message = f"""
📊 <b>Статус системы</b>

<b>🔄 Синхронизация:</b>
"""
        
        if last_sync:
            # Используем UTC для сравнения с timezone-aware datetime из БД
            now = datetime.now(timezone.utc)
            time_ago = now - last_sync.synced_at
            minutes_ago = int(time_ago.total_seconds() / 60)
            
            status_emoji = "✅" if last_sync.status.value == "успешно" else "❌"
            status_message += f"""
{status_emoji} Последняя: {minutes_ago} мин назад
Статус: {last_sync.status.value}
Изменений: {last_sync.changes_detected}
"""
        else:
            status_message += "Синхронизация еще не выполнялась\n"
        
        status_message += f"""
<b>👥 Пользователи:</b>
Всего: {total_users}
Активных (7 дней): {active_users}

<b>📅 Расписание:</b>
Всего занятий: {total_schedule}
Групп: {groups_count}
"""
    
        if recent_errors:
            status_message += f"\n<b>⚠️ Последние ошибки:</b>\n"
            for error in recent_errors:
                status_message += f"• {error.error_message[:50]}...\n"
        
        await update.message.reply_text(status_message, parse_mode="HTML")
        logger.info(f"Админ {user.id} запросил статус")
        
    except Exception as e:
        logger.error(f"Ошибка в status_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении статуса:\n{str(e)[:100]}"
        )


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /stats
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        with get_db() as db:
            # Распределение по группам
            groups_stats = db.query(
                User.group_name,
                func.count(User.id).label('count')
            ).group_by(User.group_name).all()
            
            # Настройки уведомлений
            morning_enabled = db.query(User).filter(
                User.notifications_morning == True
            ).count()
            
            before_class_enabled = db.query(User).filter(
                User.notifications_before_class == True
            ).count()
            
            changes_enabled = db.query(User).filter(
                User.notifications_changes == True
            ).count()
            
            total_users = db.query(User).count()
        
        stats_message = f"""
📈 <b>Статистика</b>

<b>👥 Всего пользователей: {total_users}</b>

<b>Распределение по группам:</b>
"""
        
        for group, count in groups_stats:
            if group:
                stats_message += f"• {group}: {count} студентов\n"
        
        stats_message += f"""
<b>📬 Уведомления:</b>
Утренние: {morning_enabled} ({morning_enabled*100//total_users if total_users > 0 else 0}%)
За 15 мин: {before_class_enabled} ({before_class_enabled*100//total_users if total_users > 0 else 0}%)
Об изменениях: {changes_enabled} ({changes_enabled*100//total_users if total_users > 0 else 0}%)
"""
        
        await update.message.reply_text(stats_message, parse_mode="HTML")
        logger.info(f"Админ {user.id} запросил статистику")
        
    except Exception as e:
        logger.error(f"Ошибка в stats_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении статистики:\n{str(e)[:100]}"
        )


async def logs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /logs
    
    Args:
        update: объект Update
        context: контекст
    """
    try:
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        with get_db() as db:
            # Последние 20 логов
            logs = db.query(SyncLog).order_by(
                SyncLog.synced_at.desc()
            ).limit(20).all()
        
            if not logs:
                await update.message.reply_text(
                    "📝 Логов пока нет"
                )
                return
            
            logs_message = "📝 <b>Последние логи синхронизации</b>\n\n"
            
            for log in logs:
                status_emoji = {
                    "успешно": "✅",
                    "ошибка": "❌",
                    "частично": "⚠️",
                    "пропущено": "⏭"
                }.get(log.status.value, "•")
                
                time_str = log.synced_at.strftime("%d.%m %H:%M")
                
                logs_message += f"{status_emoji} {time_str} | "
                
                if log.status.value == "успешно":
                    logs_message += f"OK ({log.changes_detected} изм.)\n"
                else:
                    error_short = log.error_message[:30] if log.error_message else "?"
                    logs_message += f"{error_short}...\n"
            
            await update.message.reply_text(logs_message, parse_mode="HTML")
            logger.info(f"Админ {user.id} запросил логи")
        
    except Exception as e:
        logger.error(f"Ошибка в logs_handler: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении логов:\n{str(e)[:100]}"
        )
