"""
Сервис для работы с пользователями
"""
from typing import Optional, List
from datetime import datetime
from loguru import logger

from config.database import get_db
from models.user import User


class UserService:
    """Сервис для работы с пользователями"""
    
    def get_or_create_user(self, chat_id: int, **kwargs) -> User:
        """
        Получает или создает пользователя
        
        Args:
            chat_id: Telegram chat_id
            **kwargs: дополнительные параметры
            
        Returns:
            User: пользователь
        """
        with get_db() as db:
            user = db.query(User).filter(User.chat_id == chat_id).first()
            
            if not user:
                user = User(chat_id=chat_id, **kwargs)
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Создан новый пользователь: {chat_id}")
            else:
                # Обновляем last_active
                user.last_active = datetime.now()
                db.commit()
                db.refresh(user)
            
            # Делаем объект независимым от сессии
            db.expunge(user)
            return user
    
    def get_user_by_chat_id(self, chat_id: int) -> Optional[User]:
        """
        Получает пользователя по chat_id
        
        Args:
            chat_id: Telegram chat_id
            
        Returns:
            Optional[User]: пользователь или None
        """
        with get_db() as db:
            user = db.query(User).filter(User.chat_id == chat_id).first()
            if user:
                # Делаем объект независимым от сессии
                db.expunge(user)
            return user
    
    def update_user_group(self, chat_id: int, group_name: str) -> User:
        """
        Обновляет группу пользователя
        
        Args:
            chat_id: Telegram chat_id
            group_name: название группы
            
        Returns:
            User: обновленный пользователь
        """
        with get_db() as db:
            user = db.query(User).filter(User.chat_id == chat_id).first()
            if user:
                user.group_name = group_name
                db.commit()
                db.refresh(user)
                logger.info(f"Группа пользователя {chat_id} обновлена на {group_name}")
            return user
    
    def update_notification_settings(
        self,
        chat_id: int,
        morning: Optional[bool] = None,
        before_class: Optional[bool] = None,
        changes: Optional[bool] = None
    ) -> User:
        """
        Обновляет настройки уведомлений
        
        Args:
            chat_id: Telegram chat_id
            morning: утренние уведомления
            before_class: уведомления за 15 мин
            changes: уведомления об изменениях
            
        Returns:
            User: обновленный пользователь
        """
        with get_db() as db:
            user = db.query(User).filter(User.chat_id == chat_id).first()
            if user:
                if morning is not None:
                    user.notifications_morning = morning
                if before_class is not None:
                    user.notifications_before_class = before_class
                if changes is not None:
                    user.notifications_changes = changes
                
                db.commit()
                db.refresh(user)
                logger.info(f"Настройки уведомлений пользователя {chat_id} обновлены")
            return user
    
    def get_users_by_group(self, group_name: str) -> List[User]:
        """
        Получает всех пользователей группы
        
        Args:
            group_name: название группы
            
        Returns:
            List[User]: список пользователей
        """
        with get_db() as db:
            return db.query(User).filter(User.group_name == group_name).all()
    
    def get_all_users(self) -> List[User]:
        """
        Получает всех пользователей
        
        Returns:
            List[User]: список всех пользователей
        """
        with get_db() as db:
            return db.query(User).all()
    
    def get_users_with_morning_notifications(self) -> List[User]:
        """
        Получает пользователей с включенными утренними уведомлениями
        
        Returns:
            List[User]: список пользователей
        """
        with get_db() as db:
            return db.query(User).filter(
                User.notifications_morning == True
            ).all()
    
    def get_users_with_change_notifications(self) -> List[User]:
        """
        Получает пользователей с включенными уведомлениями об изменениях
        
        Returns:
            List[User]: список пользователей
        """
        with get_db() as db:
            return db.query(User).filter(
                User.notifications_changes == True
            ).all()
