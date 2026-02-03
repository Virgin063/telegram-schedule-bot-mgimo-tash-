"""
Обработчик загрузки файлов
"""
import os
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime

from parsers.ai_parser import AIScheduleParser
from services.schedule_service import ScheduleService
from models.sync_log import SyncLog, SyncType, SyncStatus
from config.database import get_db
from bots.admin_bot.handlers.start import is_admin


schedule_service = ScheduleService()


async def upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик загрузки Excel файла
    
    Args:
        update: объект Update
        context: контекст
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        return
    
    # Проверяем, что есть документ
    if not update.message.document:
        await update.message.reply_text(
            "📤 <b>Загрузка расписания</b>\n\n"
            "Отправьте Excel файл с расписанием (.xlsx)",
            parse_mode="HTML"
        )
        return
    
    document = update.message.document
    
    # Проверяем расширение
    if not document.file_name.endswith(('.xlsx', '.xls')):
        await update.message.reply_text(
            "❌ Неверный формат файла. Отправьте .xlsx файл."
        )
        return
    
    # Отправляем уведомление о начале обработки
    status_message = await update.message.reply_text(
        "⏳ Загрузка файла...",
        parse_mode="HTML"
    )
    
    try:
        # Скачиваем файл
        file = await document.get_file()
        file_path = f"temp_{document.file_name}"
        await file.download_to_drive(file_path)
        
        logger.info(f"Файл {document.file_name} загружен админом {user.id}")
        
        # Обновляем статус
        await status_message.edit_text(
            "🤖 Парсинг файла с помощью AI...\n"
            "⏱ Это займет 5-10 минут (19 недель).\n"
            "Не отправляйте другие файлы пока идет обработка!"
        )
        
        start_time = datetime.now()
        
        # Парсим файл
        import asyncio
        parser = AIScheduleParser()
        
        # Запускаем парсинг в отдельном потоке
        loop = asyncio.get_event_loop()
        schedule_data, warnings = await loop.run_in_executor(
            None, 
            parser.parse_excel_file, 
            file_path
        )
        
        # Обновляем статус
        await status_message.edit_text(
            f"💾 Сохранение в базу данных...\n"
            f"Найдено {len(schedule_data)} занятий"
        )
        
        # Удаляем старое расписание (опционально - можно сделать по группам)
        # schedule_service.delete_schedule_for_group(...)
        
        # Сохраняем новое расписание
        saved_count = schedule_service.save_schedule(schedule_data)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Сохраняем лог
        with get_db() as db:
            sync_log = SyncLog(
                sync_type=SyncType.MANUAL,
                status=SyncStatus.SUCCESS if saved_count > 0 else SyncStatus.ERROR,
                file_name=document.file_name,
                changes_detected=len(schedule_data),
                records_added=saved_count,
                warnings=str(warnings) if warnings else None,
                duration_seconds=int(duration)
            )
            db.add(sync_log)
            db.commit()
        
        # Удаляем временный файл
        os.remove(file_path)
        
        # Формируем итоговое сообщение
        result_message = f"""
✅ <b>Файл успешно обработан!</b>

📊 <b>Статистика:</b>
• Файл: {document.file_name}
• Найдено занятий: {len(schedule_data)}
• Сохранено в БД: {saved_count}
• Время обработки: {duration:.1f} сек
"""
        
        if warnings:
            result_message += f"\n⚠️ <b>Предупреждения ({len(warnings)}):</b>\n"
            for warning in warnings[:5]:  # Показываем первые 5
                result_message += f"• {warning}\n"
            
            if len(warnings) > 5:
                result_message += f"• ... и еще {len(warnings) - 5}\n"
        
        await status_message.edit_text(result_message, parse_mode="HTML")
        
        logger.success(f"Файл {document.file_name} успешно обработан: {saved_count} записей")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        
        # Сохраняем лог об ошибке
        with get_db() as db:
            sync_log = SyncLog(
                sync_type=SyncType.MANUAL,
                status=SyncStatus.ERROR,
                file_name=document.file_name,
                error_message=str(e)
            )
            db.add(sync_log)
            db.commit()
        
        await status_message.edit_text(
            f"❌ <b>Ошибка при обработке файла</b>\n\n"
            f"Ошибка: {str(e)}\n\n"
            f"Проверьте формат файла и попробуйте снова.",
            parse_mode="HTML"
        )
        
        # Удаляем временный файл если он есть
        if os.path.exists(file_path):
            os.remove(file_path)


async def upload_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "Загрузить файл"
    
    Args:
        update: объект Update
        context: контекст
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        return
    
    await update.message.reply_text(
        "📤 <b>Загрузка расписания</b>\n\n"
        "Отправьте Excel файл с расписанием (.xlsx)\n\n"
        "Бот автоматически:\n"
        "• Распарсит файл с помощью AI\n"
        "• Исправит ошибки\n"
        "• Сохранит в базу данных\n"
        "• Покажет статистику и предупреждения",
        parse_mode="HTML"
    )
