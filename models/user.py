"""
Модель пользователя (студента)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.sql import func
from config.database import Base


class User(Base):
    """Модель студента"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, unique=True, nullable=False, index=True)
    group_name = Column(String(100), nullable=False, index=True)
    
    # Настройки уведомлений
    notifications_morning = Column(Boolean, default=True)
    notifications_before_class = Column(Boolean, default=True)
    notifications_changes = Column(Boolean, default=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Дополнительная информация (опционально)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100))
    
    def __repr__(self):
        return f"<User(chat_id={self.chat_id}, group={self.group_name})>"
    
    def to_dict(self):
        """Конвертация в словарь"""
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "group_name": self.group_name,
            "notifications_morning": self.notifications_morning,
            "notifications_before_class": self.notifications_before_class,
            "notifications_changes": self.notifications_changes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }
