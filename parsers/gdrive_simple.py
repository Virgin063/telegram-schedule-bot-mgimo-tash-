"""
Упрощенная синхронизация с Google Drive через публичную ссылку
БЕЗ настройки API!
"""
import os
import requests
from typing import Tuple, Optional
from datetime import datetime
from loguru import logger
import redis

from config.settings import settings
from parsers.ai_parser import AIScheduleParser
from services.schedule_service import ScheduleService
from models.sync_log import SyncLog, SyncType, SyncStatus
from config.database import get_db


class GoogleDriveSimpleSync:
    """
    Простая синхронизация с Google Drive через публичную ссылку
    
    Не требует настройки API!
    Просто нужна публичная ссылка на файл.
    """
    
    def __init__(self, public_url: str = None):
        """
        Инициализация
        
        Args:
            public_url: Публичная ссылка на файл Google Drive
                       (с доступом "Любой, у кого есть ссылка")
        """
        self.public_url = public_url or settings.google_drive_folder_id  # Используем как URL
        self.parser = AIScheduleParser()
        self.schedule_service = ScheduleService()
        
        # Redis для кеширования
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=False  # Для хранения бинарных данных
            )
        except Exception as e:
            logger.warning(f"Redis недоступен: {e}")
            self.redis_client = None
    
    def download_file_from_gdrive(self, url: str) -> Optional[bytes]:
        """
        Скачивает файл с Google Drive по публичной ссылке
        
        Args:
            url: Публичная ссылка на файл
            
        Returns:
            Optional[bytes]: содержимое файла или None
        """
        try:
            # Извлекаем file_id из разных форматов ссылок
            file_id = self._extract_file_id(url)
            
            if not file_id:
                logger.error(f"Не удалось извлечь file_id из ссылки: {url}")
                return None
            
            # Формируем ссылку для скачивания
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            logger.info(f"Скачивание файла: {file_id}")
            
            # Скачиваем
            session = requests.Session()
            response = session.get(download_url, stream=True)
            
            # Проверяем, нужно ли подтверждение (для больших файлов)
            if 'download_warning' in response.cookies:
                params = {'confirm': response.cookies['download_warning']}
                response = session.get(download_url, params=params, stream=True)
            
            if response.status_code == 200:
                logger.success(f"Файл успешно скачан ({len(response.content)} байт)")
                return response.content
            else:
                logger.error(f"Ошибка скачивания: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при скачивании файла: {e}")
            return None
    
    def _extract_file_id(self, url: str) -> Optional[str]:
        """
        Извлекает file_id из разных форматов ссылок Google Drive
        
        Поддерживаемые форматы:
        - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
        - https://drive.google.com/open?id=FILE_ID
        - https://drive.google.com/uc?id=FILE_ID
        
        Args:
            url: ссылка на файл
            
        Returns:
            Optional[str]: file_id или None
        """
        import re
        
        # Паттерны для разных форматов ссылок
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/d/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Возможно, это уже file_id
        if re.match(r'^[a-zA-Z0-9_-]+$', url):
            return url
        
        return None
    
    def check_if_changed(self) -> bool:
        """
        Проверяет, изменился ли файл
        
        Использует ETag или размер файла для определения
        
        Returns:
            bool: True если изменился
        """
        if not self.redis_client:
            return True  # Без Redis всегда считаем что изменился
        
        try:
            file_id = self._extract_file_id(self.public_url)
            if not file_id:
                return True
            
            # Делаем HEAD запрос для получения метаданных
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            response = requests.head(download_url)
            
            # Получаем ETag или Content-Length
            etag = response.headers.get('ETag')
            size = response.headers.get('Content-Length')
            
            current_signature = f"{etag}:{size}"
            
            # Проверяем кеш
            cached_signature = self.redis_client.get(f"gdrive_simple:signature:{file_id}")
            
            if cached_signature and cached_signature.decode() == current_signature:
                logger.info("Файл не изменился (по сигнатуре)")
                return False
            
            # Обновляем кеш
            self.redis_client.set(
                f"gdrive_simple:signature:{file_id}",
                current_signature,
                ex=86400  # 24 часа
            )
            
            return True
            
        except Exception as e:
            logger.warning(f"Ошибка проверки изменений: {e}")
            return True  # В случае ошибки считаем что изменился
    
    def sync(self) -> Tuple[bool, str, int]:
        """
        Синхронизирует файл
        
        Returns:
            Tuple[bool, str, int]: (успех, сообщение, количество изменений)
        """
        logger.info(f"Начинаем синхронизацию: {self.public_url}")
        
        start_time = datetime.now()
        
        try:
            # Проверяем, изменился ли файл
            if not self.check_if_changed():
                logger.info("Файл не изменился, пропускаем синхронизацию")
                return True, "Файл не изменился", 0
            
            # Скачиваем файл
            file_content = self.download_file_from_gdrive(self.public_url)
            
            if not file_content:
                return False, "Не удалось скачать файл", 0
            
            # Сохраняем во временный файл
            temp_path = "temp_gdrive_schedule.xlsx"
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Парсим файл
            logger.info("Парсинг файла с помощью AI...")
            schedule_data, warnings = self.parser.parse_excel_file(temp_path)
            
            if not schedule_data:
                return False, "Не удалось распарсить файл", 0
            
            # Сохраняем расписание
            saved_count = self.schedule_service.save_schedule(schedule_data)
            
            # Удаляем временный файл
            os.remove(temp_path)
            
            # Сохраняем лог
            duration = (datetime.now() - start_time).total_seconds()
            
            with get_db() as db:
                sync_log = SyncLog(
                    sync_type=SyncType.AUTO,
                    status=SyncStatus.SUCCESS,
                    file_name="Google Drive (публичная ссылка)",
                    changes_detected=len(schedule_data),
                    records_added=saved_count,
                    warnings=str(warnings) if warnings else None,
                    duration_seconds=int(duration)
                )
                db.add(sync_log)
                db.commit()
            
            logger.success(f"Синхронизация завершена: {saved_count} записей")
            
            return True, f"Успешно: {saved_count} записей", saved_count
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации: {e}")
            
            # Сохраняем лог об ошибке
            with get_db() as db:
                sync_log = SyncLog(
                    sync_type=SyncType.AUTO,
                    status=SyncStatus.ERROR,
                    file_name="Google Drive (публичная ссылка)",
                    error_message=str(e)
                )
                db.add(sync_log)
                db.commit()
            
            return False, str(e), 0


# Пример использования
if __name__ == "__main__":
    # Ваша публичная ссылка на файл
    PUBLIC_URL = "https://drive.google.com/file/d/ВАШ_FILE_ID/view?usp=sharing"
    
    sync = GoogleDriveSimpleSync(PUBLIC_URL)
    success, message, count = sync.sync()
    
    print(f"Результат: {message}")
