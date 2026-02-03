"""
Форматирование расписания для вывода в Telegram
"""
from typing import List
from datetime import date, datetime
from models.schedule import Schedule


class ScheduleFormatter:
    """Форматирование расписания"""
    
    # Эмодзи для типов занятий
    CLASS_TYPE_EMOJI = {
        "лекция": "📚",
        "практика": "✏️",
        "лабораторная": "🔬",
        "семинар": "💬",
        "другое": "📖"
    }
    
    # Эмодзи для дней недели
    DAY_EMOJI = {
        "понедельник": "📅",
        "вторник": "📅",
        "среда": "📅",
        "четверг": "📅",
        "пятница": "📅",
        "суббота": "📅",
        "воскресенье": "📅"
    }
    
    def format_schedule_for_day(
        self,
        schedule: List[Schedule],
        target_date: date
    ) -> str:
        """
        Форматирует расписание на день
        
        Args:
            schedule: список занятий
            target_date: дата
            
        Returns:
            str: форматированное расписание
        """
        if not schedule:
            return self._format_no_classes(target_date)
        
        # Форматируем дату
        day_name = self._get_russian_day_name(target_date)
        date_str = target_date.strftime("%d.%m.%Y")
        
        result = [
            f"📅 <b>Расписание на {day_name}, {date_str}</b>\n"
        ]
        
        for class_item in schedule:
            result.append(self._format_class(class_item))
        
        return "\n".join(result)
    
    def format_schedule_for_week(
        self,
        schedule_by_days: dict,
        start_date: date
    ) -> str:
        """
        Форматирует расписание на неделю
        
        Args:
            schedule_by_days: расписание по дням
            start_date: начало недели
            
        Returns:
            str: форматированное расписание
        """
        result = [
            "📆 <b>Расписание на неделю</b>\n"
        ]
        
        days_order = [
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота"
        ]
        
        for day_name in days_order:
            schedule = schedule_by_days.get(day_name, [])
            
            if schedule:
                result.append(f"\n<b>{day_name.upper()}</b>")
                for class_item in schedule:
                    result.append(self._format_class_short(class_item))
            else:
                result.append(f"\n<b>{day_name.upper()}</b>")
                result.append("  Нет занятий")
        
        return "\n".join(result)
    
    def format_next_class(self, class_item: Schedule) -> str:
        """
        Форматирует следующее занятие
        
        Args:
            class_item: занятие
            
        Returns:
            str: форматированное сообщение
        """
        if not class_item:
            return "📝 Сегодня больше нет занятий"
        
        return f"""
🔔 <b>Следующая пара</b>

{self._format_class(class_item)}
"""
    
    def format_class_change(self, change: dict) -> str:
        """
        Форматирует изменение в расписании
        
        Args:
            change: изменение
            
        Returns:
            str: форматированное сообщение
        """
        change_type = change.get("change_type")
        subject = change.get("subject_name", "?")
        day = change.get("day_of_week", "?")
        time = change.get("start_time", "?")
        
        emoji = "❗"
        
        if change_type == "cancelled":
            return f"{emoji} <b>Отменено занятие</b>\n\n{day.capitalize()} в {time}\n{subject}"
        
        elif change_type == "time_changed":
            old = change.get("old_value")
            new = change.get("new_value")
            return f"{emoji} <b>Изменено время</b>\n\n{subject}\n{day.capitalize()}\n{old} → {new}"
        
        elif change_type == "room_changed":
            old = change.get("old_value")
            new = change.get("new_value")
            return f"{emoji} <b>Изменена аудитория</b>\n\n{subject}\n{day.capitalize()} в {time}\nАуд. {old} → {new}"
        
        elif change_type == "teacher_changed":
            old = change.get("old_value")
            new = change.get("new_value")
            return f"{emoji} <b>Изменен преподаватель</b>\n\n{subject}\n{day.capitalize()} в {time}\n{old} → {new}"
        
        elif change_type == "new_class":
            return f"✨ <b>Новое занятие</b>\n\n{subject}\n{day.capitalize()} в {time}"
        
        elif change_type == "deleted":
            return f"🗑 <b>Удалено занятие</b>\n\n{subject}\n{day.capitalize()} в {time}"
        
        return f"{emoji} <b>Изменение в расписании</b>\n\n{subject}"
    
    def _format_class(self, class_item: Schedule) -> str:
        """
        Форматирует одно занятие (полный формат)
        
        Args:
            class_item: занятие
            
        Returns:
            str: форматированная строка
        """
        emoji = self.CLASS_TYPE_EMOJI.get(class_item.class_type.value, "📖")
        
        result = [
            f"\n{emoji} <b>{class_item.start_time.strftime('%H:%M')} - {class_item.end_time.strftime('%H:%M')}</b>",
            f"   <b>{class_item.subject_name}</b>"
        ]
        
        if class_item.teacher_name:
            result.append(f"   👨‍🏫 {class_item.teacher_name}")
        
        if class_item.room:
            result.append(f"   📍 Аудитория: {class_item.room}")
        
        if class_item.class_type.value != "другое":
            result.append(f"   📝 {class_item.class_type.value.capitalize()}")
        
        return "\n".join(result)
    
    def _format_class_short(self, class_item: Schedule) -> str:
        """
        Форматирует одно занятие (короткий формат)
        
        Args:
            class_item: занятие
            
        Returns:
            str: форматированная строка
        """
        result = f"  {class_item.start_time.strftime('%H:%M')} - {class_item.subject_name}"
        
        if class_item.teacher_name:
            result += f"\n     👨‍🏫 {class_item.teacher_name}"
        
        if class_item.room:
            result += f" | Ауд. {class_item.room}"
        
        return result
    
    def _format_no_classes(self, target_date: date) -> str:
        """
        Форматирует сообщение об отсутствии занятий
        
        Args:
            target_date: дата
            
        Returns:
            str: форматированное сообщение
        """
        day_name = self._get_russian_day_name(target_date)
        date_str = target_date.strftime("%d.%m.%Y")
        
        return f"📅 <b>{day_name.capitalize()}, {date_str}</b>\n\n🎉 В этот день нет занятий!"
    
    def _get_russian_day_name(self, target_date: date) -> str:
        """
        Получает название дня недели на русском
        
        Args:
            target_date: дата
            
        Returns:
            str: название дня
        """
        days = [
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота",
            "воскресенье"
        ]
        return days[target_date.weekday()]
