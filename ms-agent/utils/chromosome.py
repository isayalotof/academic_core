"""
Chromosome and Lesson structures for Genetic Algorithm
Хромосома = полное расписание (массив Lesson объектов)
"""
import copy
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Lesson:
    """Одно занятие в расписании"""
    
    def __init__(self,
                 course_load_id: int,
                 discipline_name: str,
                 lesson_type: str,
                 group_id: int,
                 group_name: str,
                 teacher_id: int,
                 teacher_name: str,
                 classroom_id: int,
                 day: int,          # 1-6 (Понедельник-Суббота)
                 slot: int,         # 1-6 (1-6 пара)
                 week: int):        # 1-16 (неделя семестра)
        self.course_load_id = course_load_id
        self.discipline_name = discipline_name
        self.lesson_type = lesson_type
        self.group_id = group_id
        self.group_name = group_name
        self.teacher_id = teacher_id
        self.teacher_name = teacher_name
        self.classroom_id = classroom_id
        self.day = day
        self.slot = slot
        self.week = week
    
    def __repr__(self):
        return (
            f"Lesson({self.discipline_name[:20]}, "
            f"T{self.teacher_id}, G{self.group_id}, "
            f"D{self.day}S{self.slot}W{self.week})"
        )
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь для сохранения"""
        return {
            'course_load_id': self.course_load_id,
            'discipline_name': self.discipline_name,
            'lesson_type': self.lesson_type,
            'group_id': self.group_id,
            'group_name': self.group_name,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher_name,
            'classroom_id': self.classroom_id,
            'day_of_week': self.day,
            'time_slot': self.slot,
            'week_number': self.week
        }
    
    def copy(self) -> 'Lesson':
        """Создать копию"""
        return Lesson(
            course_load_id=self.course_load_id,
            discipline_name=self.discipline_name,
            lesson_type=self.lesson_type,
            group_id=self.group_id,
            group_name=self.group_name,
            teacher_id=self.teacher_id,
            teacher_name=self.teacher_name,
            classroom_id=self.classroom_id,
            day=self.day,
            slot=self.slot,
            week=self.week
        )


class Chromosome:
    """
    Хромосома = полное расписание
    
    Массив из 500-1000 Lesson объектов
    """
    
    def __init__(self, lessons: List[Lesson]):
        self.lessons = lessons
        self.fitness = 0.0
        self.conflicts_count = 0  # ДОЛЖНО БЫТЬ 0!
        self.hard_violations = 0  # Все жесткие нарушения (конфликты + несоответствия)
        self.preference_violations = {1: 0, 2: 0, 3: 0, 4: 0}
        self.gaps_count = 0
        self.early_lessons = 0
        self.late_lessons = 0
    
    def copy(self) -> 'Chromosome':
        """Глубокое копирование"""
        new_chromosome = Chromosome([lesson.copy() for lesson in self.lessons])
        new_chromosome.fitness = self.fitness
        new_chromosome.conflicts_count = self.conflicts_count
        new_chromosome.hard_violations = self.hard_violations
        new_chromosome.preference_violations = self.preference_violations.copy()
        new_chromosome.gaps_count = self.gaps_count
        new_chromosome.early_lessons = self.early_lessons
        new_chromosome.late_lessons = self.late_lessons
        return new_chromosome
    
    def is_valid(self) -> bool:
        """Проверка на отсутствие жестких нарушений"""
        return self.hard_violations == 0
    
    def to_schedule_dict(self) -> List[Dict]:
        """Преобразование для сохранения в БД"""
        return [lesson.to_dict() for lesson in self.lessons]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику хромосомы"""
        return {
            'total_lessons': len(self.lessons),
            'fitness': self.fitness,
            'conflicts': self.conflicts_count,
            'preference_violations': self.preference_violations.copy(),
            'gaps': self.gaps_count,
            'early_lessons': self.early_lessons,
            'late_lessons': self.late_lessons,
            'is_valid': self.is_valid()
        }

