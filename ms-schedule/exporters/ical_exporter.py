"""
iCal exporter for schedule
Экспорт расписания в iCal формат для календарей (Google Calendar, Apple Calendar, etc.)
"""

from icalendar import Calendar, Event
from datetime import datetime, timedelta, time
import pytz
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ICalExporter:
    """Экспорт расписания в iCal"""
    
    TIME_SLOTS = {
        1: (time(9, 0), time(10, 30)),
        2: (time(10, 45), time(12, 15)),
        3: (time(13, 0), time(14, 30)),
        4: (time(14, 45), time(16, 15)),
        5: (time(16, 30), time(18, 0)),
        6: (time(18, 15), time(19, 45))
    }
    
    def export_schedule(
        self,
        lessons: List[Dict],
        start_date: datetime,
        end_date: datetime,
        entity_type: str = 'group',
        entity_name: str = '',
        semester: int = 1,
        academic_year: str = '',
        timezone: str = 'Asia/Vladivostok'
    ) -> bytes:
        """
        Экспорт расписания в iCal формат
        
        Args:
            lessons: Список занятий
            start_date: Начало семестра
            end_date: Конец семестра
            entity_type: Тип сущности ('group', 'teacher', 'classroom')
            entity_name: Название сущности
            semester: Номер семестра
            academic_year: Учебный год
            timezone: Часовой пояс
            
        Returns:
            iCal file as bytes
        """
        logger.info(f"Exporting iCal for {entity_type} {entity_name}")
        
        # Создать календарь
        cal = Calendar()
        cal.add('prodid', '-//University Schedule System//mxm.dk//')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', f'Расписание: {entity_name}')
        cal.add('x-wr-timezone', timezone)
        cal.add('x-wr-caldesc', f'Расписание {entity_type} {entity_name} ({semester} семестр, {academic_year})')
        
        tz = pytz.timezone(timezone)
        
        # Генерация событий для каждого занятия
        events_count = 0
        
        for lesson in lessons:
            events_count += self._create_recurring_events(
                cal,
                lesson,
                start_date,
                end_date,
                tz,
                entity_type
            )
        
        logger.info(f"iCal export completed: {events_count} events created")
        return cal.to_ical()
    
    def _create_recurring_events(
        self,
        cal: Calendar,
        lesson: Dict,
        start_date: datetime,
        end_date: datetime,
        tz: pytz.timezone,
        entity_type: str
    ) -> int:
        """
        Создать повторяющиеся события для одного занятия
        
        Returns:
            Количество созданных событий
        """
        count = 0
        
        # Найти первое вхождение нужного дня недели
        current_date = start_date
        while current_date.weekday() + 1 != lesson['day_of_week']:
            current_date += timedelta(days=1)
        
        # Получить время начала и конца
        start_time, end_time = self.TIME_SLOTS.get(
            lesson['time_slot'],
            (time(9, 0), time(10, 30))
        )
        
        # Создать события до конца семестра
        week_number = 1
        while current_date <= end_date:
            # Проверка week_type (числитель/знаменатель)
            is_odd_week = week_number % 2 == 1
            week_type = lesson.get('week_type', 'both')
            
            # Пропустить если не подходит по типу недели
            if week_type == 'odd' and not is_odd_week:
                current_date += timedelta(weeks=1)
                week_number += 1
                continue
            elif week_type == 'even' and is_odd_week:
                current_date += timedelta(weeks=1)
                week_number += 1
                continue
            
            # Создать событие
            event = Event()
            
            # Время начала и конца
            dtstart = tz.localize(datetime.combine(current_date, start_time))
            dtend = tz.localize(datetime.combine(current_date, end_time))
            
            # Название события
            summary = self._format_event_summary(lesson, entity_type)
            
            # Описание
            description = self._format_event_description(lesson, entity_type)
            
            # Локация
            location = self._format_location(lesson)
            
            event.add('summary', summary)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            event.add('location', location)
            event.add('description', description)
            event.add('uid', f"{lesson['id']}-{current_date.strftime('%Y%m%d')}-w{week_number}@university.ru")
            event.add('dtstamp', datetime.now(tz))
            
            # Категории
            categories = [lesson['lesson_type']]
            if entity_type == 'group':
                categories.append(f"Группа: {lesson['group_name']}")
            elif entity_type == 'teacher':
                categories.append(f"Преподаватель: {lesson['teacher_name']}")
            
            event.add('categories', categories)
            
            # Цвет (опционально)
            if 'лекция' in lesson['lesson_type'].lower():
                event.add('color', 'blue')
            elif 'практика' in lesson['lesson_type'].lower():
                event.add('color', 'green')
            elif 'лаборатор' in lesson['lesson_type'].lower():
                event.add('color', 'orange')
            
            cal.add_component(event)
            count += 1
            
            # Следующая неделя
            current_date += timedelta(weeks=1)
            week_number += 1
        
        return count
    
    def _format_event_summary(self, lesson: Dict, entity_type: str) -> str:
        """Форматировать название события"""
        discipline = lesson['discipline_name']
        lesson_type = lesson['lesson_type']
        
        if entity_type == 'group':
            # Для группы показываем дисциплину и тип
            return f"{discipline} ({lesson_type})"
        elif entity_type == 'teacher':
            # Для преподавателя показываем дисциплину и группу
            return f"{discipline} - {lesson['group_name']} ({lesson_type})"
        elif entity_type == 'classroom':
            # Для аудитории показываем дисциплину и группу
            return f"{lesson['group_name']}: {discipline}"
        else:
            return f"{discipline} ({lesson_type})"
    
    def _format_event_description(self, lesson: Dict, entity_type: str) -> str:
        """Форматировать описание события"""
        lines = []
        
        lines.append(f"Дисциплина: {lesson['discipline_name']}")
        
        if entity_type != 'teacher':
            lines.append(f"Преподаватель: {lesson['teacher_name']}")
        
        if entity_type != 'group':
            lines.append(f"Группа: {lesson['group_name']}")
        
        lines.append(f"Тип занятия: {lesson['lesson_type']}")
        
        if lesson.get('classroom_name'):
            lines.append(f"Аудитория: {lesson['classroom_name']}")
        
        if lesson.get('building_name'):
            lines.append(f"Корпус: {lesson['building_name']}")
        
        week_type = lesson.get('week_type', 'both')
        if week_type == 'odd':
            lines.append("Неделя: числитель")
        elif week_type == 'even':
            lines.append("Неделя: знаменатель")
        
        if lesson.get('notes'):
            lines.append(f"\\nПримечания: {lesson['notes']}")
        
        return "\\n".join(lines)
    
    def _format_location(self, lesson: Dict) -> str:
        """Форматировать локацию"""
        parts = []
        
        if lesson.get('building_name'):
            parts.append(lesson['building_name'])
        
        if lesson.get('classroom_name'):
            parts.append(f"ауд. {lesson['classroom_name']}")
        
        return ", ".join(parts) if parts else "Аудитория не указана"


# Global instance
ical_exporter = ICalExporter()

