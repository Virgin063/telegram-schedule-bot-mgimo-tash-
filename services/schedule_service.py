"""
Сервис для работы с расписанием
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_
from loguru import logger

from config.database import get_db
from models.schedule import Schedule, DayOfWeek
from models.user import User


class ScheduleService:
    """Сервис для работы с расписанием"""
    
    def get_schedule_for_day(
        self,
        group_name: str,
        target_date: date
    ) -> List[Schedule]:
        """
        Получает расписание на конкретный день
        
        Args:
            group_name: название группы
            target_date: дата
            
        Returns:
            List[Schedule]: список занятий
        """
        day_name = self._get_day_name(target_date)
        week_number = self._get_week_number(target_date)
        
        with get_db() as db:
            query = db.query(Schedule).filter(
                and_(
                    Schedule.group_name == group_name,
                    Schedule.day_of_week == day_name,
                    or_(
                        Schedule.week_number == week_number,
                        Schedule.week_number == None
                    )
                )
            ).order_by(Schedule.start_time)
            
            results = query.all()
            # Делаем объекты независимыми от сессии
            for schedule in results:
                db.expunge(schedule)
            return results
    
    def get_schedule_for_week(
        self,
        group_name: str,
        start_date: date
    ) -> Dict[str, List[Schedule]]:
        """
        Получает расписание на неделю
        
        Args:
            group_name: название группы
            start_date: начало недели (понедельник)
            
        Returns:
            Dict[str, List[Schedule]]: расписание по дням
        """
        result = {}
        
        for i in range(6):  # Пн-Сб
            day = start_date + timedelta(days=i)
            schedule = self.get_schedule_for_day(group_name, day)
            day_name = self._get_day_name(day)
            result[day_name.value] = schedule
        
        return result
    
    def get_next_class(
        self,
        group_name: str,
        current_time: datetime
    ) -> Optional[Schedule]:
        """
        Получает следующее занятие
        
        Args:
            group_name: название группы
            current_time: текущее время
            
        Returns:
            Optional[Schedule]: следующее занятие или None
        """
        day_name = self._get_day_name(current_time.date())
        week_number = self._get_week_number(current_time.date())
        
        with get_db() as db:
            query = db.query(Schedule).filter(
                and_(
                    Schedule.group_name == group_name,
                    Schedule.day_of_week == day_name,
                    Schedule.start_time > current_time.time(),
                    or_(
                        Schedule.week_number == week_number,
                        Schedule.week_number == None
                    )
                )
            ).order_by(Schedule.start_time).first()
            
            if query:
                db.expunge(query)
            return query
    
    def save_schedule(self, schedule_data: List[Dict]) -> int:
        """
        Сохраняет расписание в БД
        
        Args:
            schedule_data: данные расписания
            
        Returns:
            int: количество сохраненных записей
        """
        count = 0
        
        with get_db() as db:
            for item in schedule_data:
                try:
                    schedule = Schedule(
                        group_name=item['group_name'],
                        week_number=item.get('week_number'),
                        day_of_week=DayOfWeek(item['day_of_week']),
                        start_time=datetime.strptime(item['start_time'], "%H:%M").time(),
                        end_time=datetime.strptime(item['end_time'], "%H:%M").time(),
                        class_number=item.get('class_number'),
                        subject_name=item['subject_name'],
                        teacher_name=item.get('teacher_name'),
                        room=item.get('room'),
                        class_type=item.get('class_type', 'другое'),
                        week_type=item.get('week_type', 'обе'),
                        notes=item.get('notes'),
                    )
                    
                    db.add(schedule)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка при сохранении расписания: {e}")
                    logger.debug(f"Данные: {item}")
                    continue
            
            db.commit()
        
        logger.info(f"Сохранено {count} записей расписания")
        return count
    
    def delete_schedule_for_group(self, group_name: str) -> int:
        """
        Удаляет все расписание для группы
        
        Args:
            group_name: название группы
            
        Returns:
            int: количество удаленных записей
        """
        with get_db() as db:
            count = db.query(Schedule).filter(
                Schedule.group_name == group_name
            ).delete()
            db.commit()
        
        logger.info(f"Удалено {count} записей для группы {group_name}")
        return count
    
    def _get_day_name(self, target_date: date) -> DayOfWeek:
        """
        Получает название дня недели
        
        Args:
            target_date: дата
            
        Returns:
            DayOfWeek: название дня
        """
        days = {
            0: DayOfWeek.MONDAY,
            1: DayOfWeek.TUESDAY,
            2: DayOfWeek.WEDNESDAY,
            3: DayOfWeek.THURSDAY,
            4: DayOfWeek.FRIDAY,
            5: DayOfWeek.SATURDAY,
            6: DayOfWeek.SUNDAY,
        }
        return days[target_date.weekday()]
    
    def _get_week_number(self, target_date: date) -> int:
        """
        Определяет номер недели в семестре
        
        Args:
            target_date: дата
            
        Returns:
            int: номер недели (1-19)
        """
        # Начало семестра (19 января 2026)
        semester_start = date(2026, 1, 19)
        
        if target_date < semester_start:
            return 1
        
        delta = target_date - semester_start
        week_number = (delta.days // 7) + 1
        
        return min(week_number, 19)
