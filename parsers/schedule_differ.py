"""
Определение изменений в расписании
"""
from typing import List, Dict, Tuple
from datetime import datetime
from loguru import logger


class ScheduleDiffer:
    """Класс для определения изменений в расписании"""
    
    def compare_schedules(
        self,
        old_schedule: List[Dict],
        new_schedule: List[Dict]
    ) -> List[Dict]:
        """
        Сравнивает старое и новое расписание
        
        Args:
            old_schedule: старое расписание
            new_schedule: новое расписание
            
        Returns:
            List[Dict]: список изменений
        """
        changes = []
        
        # Создаем индексы для быстрого поиска
        old_index = self._create_index(old_schedule)
        new_index = self._create_index(new_schedule)
        
        # Находим новые и измененные занятия
        for key, new_item in new_index.items():
            if key not in old_index:
                # Новое занятие
                changes.append({
                    "change_type": "new_class",
                    "group_name": new_item.get("group_name"),
                    "subject_name": new_item.get("subject_name"),
                    "day_of_week": new_item.get("day_of_week"),
                    "start_time": new_item.get("start_time"),
                    "old_value": None,
                    "new_value": self._format_class(new_item),
                })
            else:
                # Проверяем изменения
                old_item = old_index[key]
                item_changes = self._compare_items(old_item, new_item)
                changes.extend(item_changes)
        
        # Находим удаленные занятия
        for key, old_item in old_index.items():
            if key not in new_index:
                changes.append({
                    "change_type": "deleted",
                    "group_name": old_item.get("group_name"),
                    "subject_name": old_item.get("subject_name"),
                    "day_of_week": old_item.get("day_of_week"),
                    "start_time": old_item.get("start_time"),
                    "old_value": self._format_class(old_item),
                    "new_value": None,
                })
        
        logger.info(f"Обнаружено {len(changes)} изменений")
        return changes
    
    def _create_index(self, schedule: List[Dict]) -> Dict[str, Dict]:
        """
        Создает индекс расписания для быстрого поиска
        
        Args:
            schedule: расписание
            
        Returns:
            Dict[str, Dict]: индекс {ключ: элемент}
        """
        index = {}
        for item in schedule:
            key = self._make_key(item)
            index[key] = item
        return index
    
    def _make_key(self, item: Dict) -> str:
        """
        Создает уникальный ключ для занятия
        
        Args:
            item: элемент расписания
            
        Returns:
            str: уникальный ключ
        """
        return f"{item.get('group_name')}_{item.get('week_number')}_{item.get('day_of_week')}_{item.get('start_time')}"
    
    def _compare_items(self, old_item: Dict, new_item: Dict) -> List[Dict]:
        """
        Сравнивает два элемента расписания
        
        Args:
            old_item: старый элемент
            new_item: новый элемент
            
        Returns:
            List[Dict]: список изменений
        """
        changes = []
        
        # Проверяем изменение времени
        if old_item.get("start_time") != new_item.get("start_time") or \
           old_item.get("end_time") != new_item.get("end_time"):
            changes.append({
                "change_type": "time_changed",
                "group_name": new_item.get("group_name"),
                "subject_name": new_item.get("subject_name"),
                "day_of_week": new_item.get("day_of_week"),
                "start_time": new_item.get("start_time"),
                "old_value": f"{old_item.get('start_time')}-{old_item.get('end_time')}",
                "new_value": f"{new_item.get('start_time')}-{new_item.get('end_time')}",
            })
        
        # Проверяем изменение аудитории
        if old_item.get("room") != new_item.get("room"):
            changes.append({
                "change_type": "room_changed",
                "group_name": new_item.get("group_name"),
                "subject_name": new_item.get("subject_name"),
                "day_of_week": new_item.get("day_of_week"),
                "start_time": new_item.get("start_time"),
                "old_value": old_item.get("room") or "не указана",
                "new_value": new_item.get("room") or "не указана",
            })
        
        # Проверяем изменение преподавателя
        if old_item.get("teacher_name") != new_item.get("teacher_name"):
            changes.append({
                "change_type": "teacher_changed",
                "group_name": new_item.get("group_name"),
                "subject_name": new_item.get("subject_name"),
                "day_of_week": new_item.get("day_of_week"),
                "start_time": new_item.get("start_time"),
                "old_value": old_item.get("teacher_name") or "не указан",
                "new_value": new_item.get("teacher_name") or "не указан",
            })
        
        return changes
    
    def _format_class(self, item: Dict) -> str:
        """
        Форматирует занятие в строку
        
        Args:
            item: элемент расписания
            
        Returns:
            str: форматированная строка
        """
        parts = [
            item.get("subject_name", "?"),
            f"{item.get('start_time', '?')}-{item.get('end_time', '?')}",
        ]
        
        if item.get("teacher_name"):
            parts.append(item.get("teacher_name"))
        
        if item.get("room"):
            parts.append(f"ауд. {item.get('room')}")
        
        return ", ".join(parts)
