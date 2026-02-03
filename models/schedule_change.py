"""
Модель изменений расписания
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from config.database import Base
import enum


class ChangeType(str, enum.Enum):
    """Типы изменений"""
    CANCELLED = "отменено"
    TIME_CHANGED = "время_изменено"
    ROOM_CHANGED = "аудитория_изменена"
    TEACHER_CHANGED = "преподаватель_изменен"
    NEW_CLASS = "новое_занятие"
    DELETED = "удалено"
    OTHER = "другое"


class ScheduleChange(Base):
    """Модель изменений расписания"""
    __tablename__ = "schedule_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Что изменилось
    group_name = Column(String(100), nullable=False, index=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    
    # Старое и новое значение
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Детали изменения
    subject_name = Column(String(200), nullable=True)
    day_of_week = Column(String(50), nullable=True)
    start_time = Column(String(10), nullable=True)
    
    # Уведомления
    notified = Column(Boolean, default=False, index=True)
    notification_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метаданные
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ScheduleChange(group={self.group_name}, type={self.change_type}, notified={self.notified})>"
    
    def to_dict(self):
        """Конвертация в словарь"""
        return {
            "id": self.id,
            "group_name": self.group_name,
            "change_type": self.change_type.value if self.change_type else None,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "subject_name": self.subject_name,
            "day_of_week": self.day_of_week,
            "start_time": self.start_time,
            "notified": self.notified,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
