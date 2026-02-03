"""
Модель расписания
"""
from sqlalchemy import Column, Integer, String, DateTime, Time, Enum, UniqueConstraint
from sqlalchemy.sql import func
from config.database import Base
import enum


class ClassType(str, enum.Enum):
    """Типы занятий"""
    LECTURE = "лекция"
    PRACTICE = "практика"
    LAB = "лабораторная"
    SEMINAR = "семинар"
    OTHER = "другое"


class WeekType(str, enum.Enum):
    """Тип недели"""
    BOTH = "обе"
    ODD = "нечетная"
    EVEN = "четная"


class DayOfWeek(str, enum.Enum):
    """День недели"""
    MONDAY = "понедельник"
    TUESDAY = "вторник"
    WEDNESDAY = "среда"
    THURSDAY = "четверг"
    FRIDAY = "пятница"
    SATURDAY = "суббота"
    SUNDAY = "воскресенье"


class Schedule(Base):
    """Модель расписания"""
    __tablename__ = "schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    group_name = Column(String(100), nullable=False, index=True)
    week_number = Column(Integer, nullable=True)  # Номер недели (1-19)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    
    # Время
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    class_number = Column(Integer, nullable=True)  # Номер пары (1, 2, 3...)
    
    # Предмет и преподаватель
    subject_name = Column(String(200), nullable=False)
    teacher_name = Column(String(200), nullable=True)
    room = Column(String(50), nullable=True)
    
    # Тип занятия
    class_type = Column(Enum(ClassType), default=ClassType.OTHER)
    week_type = Column(Enum(WeekType), default=WeekType.BOTH)
    
    # Дополнительная информация
    notes = Column(String(500), nullable=True)  # Заметки из AI парсинга
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Уникальность: группа + неделя + день + время
    __table_args__ = (
        UniqueConstraint('group_name', 'week_number', 'day_of_week', 'start_time', name='unique_schedule_entry'),
    )
    
    def __repr__(self):
        return f"<Schedule(group={self.group_name}, day={self.day_of_week}, time={self.start_time}, subject={self.subject_name})>"
    
    def to_dict(self):
        """Конвертация в словарь"""
        return {
            "id": self.id,
            "group_name": self.group_name,
            "week_number": self.week_number,
            "day_of_week": self.day_of_week.value if self.day_of_week else None,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "class_number": self.class_number,
            "subject_name": self.subject_name,
            "teacher_name": self.teacher_name,
            "room": self.room,
            "class_type": self.class_type.value if self.class_type else None,
            "week_type": self.week_type.value if self.week_type else None,
            "notes": self.notes,
        }
