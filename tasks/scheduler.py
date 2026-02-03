#!/usr/bin/env python3
"""
Планировщик фоновых задач
"""
import sys
import asyncio
from datetime import datetime, time
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import settings
from config.database import init_db
from services.notification_service import NotificationService


# Настройка логирования
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>"
)
logger.add(
    "logs/scheduler.log",
    level=settings.log_level,
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)


# Глобальные сервисы
gdrive_sync = None
notification_service = None


def get_gdrive_sync():
    """Получает правильный sync в зависимости от режима"""
    if settings.google_drive_mode == "simple":
        # Простой режим - публичная ссылка
        from parsers.gdrive_simple import GoogleDriveSimpleSync
        return GoogleDriveSimpleSync(settings.google_drive_public_url)
    else:
        # API режим
        from parsers.gdrive_sync import GoogleDriveSync
        return GoogleDriveSync()


async def sync_task():
    """Задача синхронизации с Google Drive"""
    global gdrive_sync
    
    if settings.sync_mode != "auto":
        logger.info("Автоматическая синхронизация отключена")
        return
    
    # Проверяем, настроен ли Google Drive
    if settings.google_drive_mode == "simple" and not settings.google_drive_public_url:
        logger.warning("Google Drive публичная ссылка не настроена. Пропускаем синхронизацию.")
        return
    
    if settings.google_drive_mode == "api" and not settings.google_drive_folder_id:
        logger.warning("Google Drive API не настроен. Пропускаем синхронизацию.")
        return
    
    logger.info(f"Запуск задачи синхронизации (режим: {settings.google_drive_mode})")
    
    try:
        if not gdrive_sync:
            gdrive_sync = get_gdrive_sync()
        
        if settings.google_drive_mode == "simple":
            # Простой режим - один файл
            success, message, count = gdrive_sync.sync()
            
            if success:
                logger.success(f"Синхронизация успешна: {message}")
            else:
                logger.error(f"Ошибка синхронизации: {message}")
        else:
            # API режим - несколько файлов
            success, errors, messages = gdrive_sync.sync_all()
            
            if errors > 0:
                logger.warning(f"Синхронизация завершена с ошибками: {errors}")
            else:
                logger.success(f"Синхронизация успешна: {success} файлов")
            
    except Exception as e:
        logger.error(f"Ошибка в задаче синхронизации: {e}")
        import traceback
        traceback.print_exc()


async def morning_notifications_task():
    """Задача отправки утренних уведомлений"""
    global notification_service
    
    logger.info("Запуск задачи утренних уведомлений")
    
    try:
        if not notification_service:
            notification_service = NotificationService()
        
        await notification_service.send_morning_notifications()
        
    except Exception as e:
        logger.error(f"Ошибка в задаче утренних уведомлений: {e}")
        import traceback
        traceback.print_exc()


async def before_class_notifications_task():
    """Задача уведомлений за 15 минут до пары"""
    # TODO: Реализовать логику поиска пар, которые начнутся через 15 минут
    # и отправку уведомлений студентам
    pass


def main():
    """Главная функция"""
    logger.info("=" * 80)
    logger.info("ЗАПУСК ПЛАНИРОВЩИКА ЗАДАЧ")
    logger.info("=" * 80)
    
    # Инициализация БД
    try:
        init_db()
        logger.success("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        sys.exit(1)
    
    # Создаем планировщик
    scheduler = AsyncIOScheduler()
    
    # Задача синхронизации (каждые N минут)
    if settings.sync_mode == "auto":
        scheduler.add_job(
            sync_task,
            'interval',
            minutes=settings.sync_interval_minutes,
            id='sync_task',
            name='Синхронизация с Google Drive'
        )
        logger.info(f"Задача синхронизации: каждые {settings.sync_interval_minutes} минут")
    
    # Утренние уведомления (в указанное время)
    morning_time = settings.morning_notification_time.split(':')
    scheduler.add_job(
        morning_notifications_task,
        CronTrigger(hour=int(morning_time[0]), minute=int(morning_time[1])),
        id='morning_notifications',
        name='Утренние уведомления'
    )
    logger.info(f"Задача утренних уведомлений: {settings.morning_notification_time}")
    
    # Запускаем планировщик
    scheduler.start()
    logger.success("Планировщик запущен!")
    
    # Держим процесс запущенным
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка планировщика...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
