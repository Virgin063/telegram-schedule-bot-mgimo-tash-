"""
Синхронизация с Google Drive
"""
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from loguru import logger
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import redis

from config.settings import settings
from parsers.ai_parser import AIScheduleParser
from parsers.schedule_differ import ScheduleDiffer
from services.schedule_service import ScheduleService
from models.sync_log import SyncLog, SyncType, SyncStatus
from config.database import get_db


class GoogleDriveSync:
    """Синхронизация расписания с Google Drive"""
    
    def __init__(self):
        """Инициализация"""
        self.folder_id = settings.google_drive_folder_id
        self.parser = AIScheduleParser()
        self.differ = ScheduleDiffer()
        self.schedule_service = ScheduleService()
        
        # Redis для кеширования
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis недоступен: {e}")
            self.redis_client = None
        
        # Инициализация Google Drive
        self.drive = self._init_drive()
    
    def _init_drive(self) -> Optional[GoogleDrive]:
        """
        Инициализирует Google Drive API
        
        Returns:
            Optional[GoogleDrive]: объект Drive или None
        """
        try:
            # Проверяем наличие credentials файла
            if not os.path.exists(settings.google_credentials_file):
                logger.warning(f"Credentials файл не найден: {settings.google_credentials_file}")
                return None
            
            gauth = GoogleAuth()
            
            # Пытаемся загрузить сохраненные credentials
            gauth.LoadCredentialsFile("mycreds.txt")
            
            if gauth.credentials is None:
                # Authenticate if they're not there
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                # Refresh them if expired
                gauth.Refresh()
            else:
                # Initialize the saved creds
                gauth.Authorize()
            
            # Save the current credentials to a file
            gauth.SaveCredentialsFile("mycreds.txt")
            
            drive = GoogleDrive(gauth)
            logger.success("Google Drive API инициализирован")
            
            return drive
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Google Drive: {e}")
            return None
    
    def check_for_updates(self) -> List[Dict]:
        """
        Проверяет наличие обновлений файлов
        
        Returns:
            List[Dict]: список измененных файлов
        """
        if not self.drive:
            logger.warning("Google Drive не инициализирован")
            return []
        
        try:
            # Получаем список файлов в папке
            file_list = self.drive.ListFile({
                'q': f"'{self.folder_id}' in parents and trashed=false and mimeType contains 'spreadsheet'"
            }).GetList()
            
            changed_files = []
            
            for file in file_list:
                file_id = file['id']
                file_name = file['title']
                modified_time = file['modifiedDate']
                
                # Проверяем в кеше
                cached_time = self._get_cached_modified_time(file_id)
                
                if cached_time != modified_time:
                    logger.info(f"Обнаружено изменение файла: {file_name}")
                    changed_files.append({
                        'id': file_id,
                        'name': file_name,
                        'modified': modified_time,
                        'file_obj': file
                    })
            
            return changed_files
            
        except Exception as e:
            logger.error(f"Ошибка проверки обновлений: {e}")
            return []
    
    def sync_file(self, file_info: Dict) -> Tuple[bool, str, int]:
        """
        Синхронизирует один файл
        
        Args:
            file_info: информация о файле
            
        Returns:
            Tuple[bool, str, int]: (успех, сообщение, количество изменений)
        """
        file_id = file_info['id']
        file_name = file_info['name']
        file_obj = file_info['file_obj']
        
        try:
            # Скачиваем файл
            logger.info(f"Скачивание файла: {file_name}")
            temp_path = f"temp_{file_name}"
            file_obj.GetContentFile(temp_path)
            
            # Парсим файл
            logger.info(f"Парсинг файла: {file_name}")
            schedule_data, warnings = self.parser.parse_excel_file(temp_path)
            
            if not schedule_data:
                return False, "Не удалось распарсить файл", 0
            
            # Получаем текущее расписание для сравнения
            # (упрощенная версия - можно улучшить)
            
            # Сохраняем расписание
            saved_count = self.schedule_service.save_schedule(schedule_data)
            
            # Обновляем кеш
            self._update_cached_modified_time(file_id, file_info['modified'])
            
            # Удаляем временный файл
            os.remove(temp_path)
            
            logger.success(f"Файл {file_name} синхронизирован: {saved_count} записей")
            
            return True, f"Успешно: {saved_count} записей", saved_count
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации файла {file_name}: {e}")
            return False, str(e), 0
    
    def sync_all(self) -> Tuple[int, int, List[str]]:
        """
        Синхронизирует все измененные файлы
        
        Returns:
            Tuple[int, int, List[str]]: (успешно, ошибок, список сообщений)
        """
        logger.info("Начинаем синхронизацию с Google Drive")
        
        start_time = datetime.now()
        changed_files = self.check_for_updates()
        
        if not changed_files:
            logger.info("Нет изменений для синхронизации")
            return 0, 0, ["Нет изменений"]
        
        success_count = 0
        error_count = 0
        messages = []
        total_changes = 0
        
        for file_info in changed_files:
            success, message, changes = self.sync_file(file_info)
            
            if success:
                success_count += 1
                total_changes += changes
            else:
                error_count += 1
            
            messages.append(f"{file_info['name']}: {message}")
        
        # Сохраняем лог
        duration = (datetime.now() - start_time).total_seconds()
        
        with get_db() as db:
            sync_log = SyncLog(
                sync_type=SyncType.AUTO,
                status=SyncStatus.SUCCESS if error_count == 0 else SyncStatus.PARTIAL,
                file_name=f"{success_count} файлов",
                changes_detected=total_changes,
                records_added=total_changes,
                error_message="; ".join(messages) if error_count > 0 else None,
                duration_seconds=int(duration)
            )
            db.add(sync_log)
            db.commit()
        
        logger.success(
            f"Синхронизация завершена: {success_count} успешно, "
            f"{error_count} ошибок, {total_changes} изменений"
        )
        
        return success_count, error_count, messages
    
    def _get_cached_modified_time(self, file_id: str) -> Optional[str]:
        """
        Получает время изменения файла из кеша
        
        Args:
            file_id: ID файла
            
        Returns:
            Optional[str]: время изменения или None
        """
        if not self.redis_client:
            return None
        
        try:
            return self.redis_client.get(f"gdrive:modified:{file_id}")
        except Exception as e:
            logger.warning(f"Ошибка чтения из Redis: {e}")
            return None
    
    def _update_cached_modified_time(self, file_id: str, modified_time: str):
        """
        Обновляет время изменения файла в кеше
        
        Args:
            file_id: ID файла
            modified_time: время изменения
        """
        if not self.redis_client:
            return
        
        try:
            self.redis_client.set(
                f"gdrive:modified:{file_id}",
                modified_time,
                ex=86400 * 7  # 7 дней
            )
        except Exception as e:
            logger.warning(f"Ошибка записи в Redis: {e}")
