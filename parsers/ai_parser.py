"""
AI-парсер расписания с использованием GPT-4o
"""
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import time
import pandas as pd
from openai import OpenAI
from loguru import logger

from config.settings import settings
from parsers.prompts import PARSING_PROMPT_TEMPLATE, format_excel_for_ai


class AIScheduleParser:
    """Парсер расписания с использованием GPT-4o"""
    
    def __init__(self):
        """Инициализация парсера"""
        # Поддержка OpenRouter и OpenAI
        base_url = "https://openrouter.ai/api/v1" if settings.openai_api_key.startswith("sk-or-") else None
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=base_url
        )
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
    
    def parse_excel_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Парсит Excel файл с расписанием
        
        Args:
            file_path: путь к Excel файлу
            
        Returns:
            Tuple[List[Dict], List[str]]: (расписание, предупреждения)
        """
        logger.info(f"Начинаю парсинг файла: {file_path}")
        
        try:
            # Читаем все листы
            excel_file = pd.ExcelFile(file_path)
            all_schedule = []
            all_warnings = []
            
            # Определяем название группы из первого листа
            group_name = self._extract_group_name(file_path, excel_file.sheet_names[0])
            logger.info(f"Обнаружена группа: {group_name}")
            
            # Парсим каждый лист (каждая неделя)
            for sheet_idx, sheet_name in enumerate(excel_file.sheet_names):
                logger.info(f"Парсинг листа {sheet_idx + 1}/{len(excel_file.sheet_names)}: {sheet_name}")
                
                week_number = sheet_idx + 1
                schedule, warnings = self._parse_sheet(
                    file_path, 
                    sheet_name, 
                    group_name, 
                    week_number
                )
                
                all_schedule.extend(schedule)
                all_warnings.extend(warnings)
            
            logger.success(f"Парсинг завершен. Найдено {len(all_schedule)} занятий")
            return all_schedule, all_warnings
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге файла: {e}")
            raise
    
    def _extract_group_name(self, file_path: str, sheet_name: str) -> str:
        """
        Извлекает название группы из таблицы
        
        Args:
            file_path: путь к файлу
            sheet_name: название листа
            
        Returns:
            str: название группы
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            # Ищем название группы в первых 15 строках
            for idx in range(min(15, len(df))):
                for col in df.columns:
                    value = str(df.iloc[idx, col])
                    
                    # Паттерны для поиска группы
                    patterns = [
                        r'БИ\(б\)-\d+/\d+',  # БИ(б)-23/1
                        r'[А-ЯЁ]{2,4}-\d+/\d+',  # любая группа
                        r'[А-ЯЁ]{2,4}-\d+',  # ИТ-23
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, value)
                        if match:
                            return match.group(0)
            
            # Если не нашли - используем имя файла
            file_name = file_path.split('/')[-1].replace('.xlsx', '').replace('.xls', '')
            return file_name
            
        except Exception as e:
            logger.warning(f"Не удалось извлечь название группы: {e}")
            return "Неизвестная группа"
    
    def _parse_sheet(
        self, 
        file_path: str, 
        sheet_name: str, 
        group_name: str, 
        week_number: int
    ) -> Tuple[List[Dict], List[str]]:
        """
        Парсит один лист Excel (одна неделя)
        
        Args:
            file_path: путь к файлу
            sheet_name: название листа
            group_name: название группы
            week_number: номер недели
            
        Returns:
            Tuple[List[Dict], List[str]]: (расписание, предупреждения)
        """
        try:
            # Читаем лист
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            # Форматируем для AI
            excel_text = format_excel_for_ai(df)
            
            # Создаем промпт
            prompt = PARSING_PROMPT_TEMPLATE.format(
                group_name=group_name,
                week_number=week_number,
                excel_content=excel_text
            )
            
            # Отправляем в GPT-4o
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по парсингу расписаний университетов. Всегда отвечай только валидным JSON без дополнительного текста."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Низкая температура для точности
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Принудительный JSON
            )
            
            # Парсим ответ
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Добавляем метаданные
            schedule = result.get('schedule', [])
            for item in schedule:
                item['group_name'] = group_name
                item['week_number'] = week_number
            
            warnings = result.get('warnings', [])
            
            logger.info(f"Лист {sheet_name}: найдено {len(schedule)} занятий, {len(warnings)} предупреждений")
            
            return schedule, warnings
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON ответа от AI: {e}")
            logger.debug(f"Ответ AI: {result_text}")
            return [], [f"Ошибка парсинга JSON: {str(e)}"]
        except Exception as e:
            logger.error(f"Ошибка при парсинге листа {sheet_name}: {e}")
            return [], [f"Ошибка: {str(e)}"]
    
    def validate_and_fix(self, schedule_item: Dict) -> Dict:
        """
        Валидирует и исправляет элемент расписания
        
        Args:
            schedule_item: элемент расписания
            
        Returns:
            Dict: исправленный элемент
        """
        fixed = schedule_item.copy()
        
        # Валидация времени
        if 'start_time' in fixed:
            fixed['start_time'] = self._normalize_time(fixed['start_time'])
        
        if 'end_time' in fixed:
            fixed['end_time'] = self._normalize_time(fixed['end_time'])
        
        # Валидация ФИО
        if 'teacher_name' in fixed and fixed['teacher_name']:
            fixed['teacher_name'] = self._normalize_teacher_name(fixed['teacher_name'])
        
        # Валидация аудитории
        if 'room' in fixed and fixed['room']:
            fixed['room'] = self._normalize_room(fixed['room'])
        
        return fixed
    
    def _normalize_time(self, time_str: str) -> str:
        """
        Нормализует формат времени
        
        Args:
            time_str: время в любом формате
            
        Returns:
            str: время в формате HH:MM
        """
        if not time_str:
            return None
        
        # Убираем лишние символы
        time_str = str(time_str).strip()
        
        # Паттерны времени
        patterns = [
            r'(\d{1,2})[.:](\d{2})',  # 9.00 или 9:00
            r'(\d{1,2})(\d{2})',      # 900
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                return f"{hours:02d}:{minutes:02d}"
        
        return time_str
    
    def _normalize_teacher_name(self, name: str) -> str:
        """
        Нормализует ФИО преподавателя
        
        Args:
            name: ФИО в любом формате
            
        Returns:
            str: ФИО в формате "Фамилия И.О."
        """
        if not name:
            return None
        
        name = str(name).strip()
        
        # Если уже в правильном формате
        if re.match(r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.[А-ЯЁ]\.$', name):
            return name
        
        # Пытаемся извлечь части
        parts = name.split()
        if len(parts) >= 3:
            # Фамилия Имя Отчество -> Фамилия И.О.
            return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
        elif len(parts) == 2:
            # Фамилия Имя -> Фамилия И.
            return f"{parts[0]} {parts[1][0]}."
        
        return name
    
    def _normalize_room(self, room: str) -> str:
        """
        Нормализует номер аудитории
        
        Args:
            room: аудитория в любом формате
            
        Returns:
            str: только номер
        """
        if not room:
            return None
        
        room = str(room).strip()
        
        # Извлекаем числа
        numbers = re.findall(r'\d+', room)
        if numbers:
            return numbers[0]
        
        return room
