"""
Модель логов синхронизации
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from config.database import Base
import enum


class SyncType(str, enum.Enum):
    """Тип синхронизации"""
    AUTO = "автоматическая"
    MANUAL = "ручная"
    FORCED = "принудительная"


class SyncStatus(str, enum.Enum):
    """Статус синхронизации"""
    SUCCESS = "успешно"
    ERROR = "ошибка"
    PARTIAL = "частично"
    SKIPPED = "пропущено"


class SyncLog(Base):
    """Модель лога синхронизации"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Тип и статус
    sync_type = Column(Enum(SyncType), nullable=False)
    status = Column(Enum(SyncStatus), nullable=False, index=True)
    
    # Информация о файле
    file_name = Column(String(255), nullable=True)
    file_id = Column(String(255), nullable=True)  # Google Drive file ID
    
    # Результаты
    changes_detected = Column(Integer, default=0)
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)
    
    # Ошибки
    error_message = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)  # JSON массив предупреждений
    
    # Время
    synced_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<SyncLog(type={self.sync_type}, status={self.status}, changes={self.changes_detected})>"
    
    def to_dict(self):
        """Конвертация в словарь"""
        return {
            "id": self.id,
            "sync_type": self.sync_type.value if self.sync_type else None,
            "status": self.status.value if self.status else None,
            "file_name": self.file_name,
            "changes_detected": self.changes_detected,
            "records_added": self.records_added,
            "records_updated": self.records_updated,
            "records_deleted": self.records_deleted,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "duration_seconds": self.duration_seconds,
        }
