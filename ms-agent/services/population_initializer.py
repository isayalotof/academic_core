"""
Population Initializer для генетического алгоритма
Создание начальной популяции валидных расписаний (без конфликтов)
"""
import random
import logging
from typing import List, Dict, Any
from utils.chromosome import Chromosome, Lesson

logger = logging.getLogger(__name__)


class PopulationInitializer:
    """Создание начальной популяции валидных расписаний"""
    
    WEEKS_IN_SEMESTER = 16
    DAYS_PER_WEEK = 6
    SLOTS_PER_DAY = 6
    
    def __init__(self, context: Dict):
        """
        Args:
            context: {
                'course_loads': List[Dict],  # из Excel!
                'classrooms': List[Dict],
                'teachers': Dict[teacher_id, info],
                'groups': Dict[group_id, info]
            }
        """
        self.context = context
        self.course_loads = context.get('course_loads', [])
        self.classrooms = context.get('classrooms', [])
        self.teachers = context.get('teachers', {})
        self.groups = context.get('groups', {})
    
    def create_population(self, size: int = 50) -> List[Chromosome]:
        """
        Создать популяцию из size валидных расписаний
        
        Алгоритм:
        1. Для каждой course_load создать lessons_per_week × 16 недель пар
        2. Случайно распределить по слотам
        3. Проверить на конфликты
        4. Повторять пока не получим size валидных
        """
        
        population = []
        
        logger.info(f"Creating initial population of {size} chromosomes")
        logger.info(f"Course loads: {len(self.course_loads)}")
        
        for i in range(size):
            attempts = 0
            max_attempts = 100
            
            while attempts < max_attempts:
                try:
                    chromosome = self._create_random_chromosome()
                    
                    # КРИТИЧНО: проверить на конфликты
                    if self._has_no_conflicts(chromosome):
                        population.append(chromosome)
                        logger.info(f"Created valid chromosome {i + 1}/{size}")
                        break
                    
                    attempts += 1
                    
                except Exception as e:
                    logger.warning(f"Error creating chromosome: {e}")
                    attempts += 1
                    continue
            
            if attempts >= max_attempts:
                logger.warning(
                    f"Failed to create valid chromosome {i + 1} "
                    f"after {max_attempts} attempts"
                )
        
        logger.info(f"Created {len(population)} valid chromosomes")
        
        return population
    
    def _create_random_chromosome(self) -> Chromosome:
        """
        Создать случайное расписание
        
        Для каждой course_load из Excel:
        - lessons_per_week пар в неделю
        - 16 недель
        - Итого: lessons_per_week × 16 пар
        """
        lessons = []
        
        for course_load in self.course_loads:
            # Сколько пар в неделю (вычислено парсером из часов!)
            lessons_per_week = course_load.get('lessons_per_week', 1)
            
            # Пропустить если нет teacher_id или group_id
            teacher_id = course_load.get('teacher_id', 0)
            group_id = course_load.get('group_id', 0)
            
            if teacher_id == 0 or group_id == 0:
                continue
            
            # Для каждой из 16 недель
            for week in range(1, self.WEEKS_IN_SEMESTER + 1):
                # Создать lessons_per_week пар
                for _ in range(lessons_per_week):
                    # Случайный слот
                    day = random.randint(1, self.DAYS_PER_WEEK)
                    slot = random.randint(1, self.SLOTS_PER_DAY)
                    
                    # Случайная подходящая аудитория
                    classroom = self._select_classroom(course_load)
                    
                    lesson = Lesson(
                        course_load_id=course_load.get('id', 0),
                        discipline_name=course_load.get('discipline_name', ''),
                        lesson_type=course_load.get('lesson_type', 'Практика'),
                        group_id=group_id,
                        group_name=course_load.get('group_name', ''),
                        teacher_id=teacher_id,
                        teacher_name=course_load.get('teacher_name', ''),
                        classroom_id=classroom.get('id', 0),
                        day=day,
                        slot=slot,
                        week=week
                    )
                    
                    lessons.append(lesson)
        
        return Chromosome(lessons)
    
    def _select_classroom(self, course_load: Dict) -> Dict:
        """Выбрать подходящую аудиторию"""
        group_size = course_load.get('group_size') or course_load.get('students_count')
        lesson_type = course_load.get('lesson_type', 'Практика')
        
        # Фильтр по типу и вместимости
        suitable = []
        for classroom in self.classrooms:
            capacity = classroom.get('capacity', 0)
            classroom_type = classroom.get('classroom_type', '')
            
            # Проверка вместимости
            if group_size and capacity < group_size:
                continue
            
            # Проверка типа (если требуется)
            if lesson_type == 'Лабораторная' and 'LAB' not in classroom_type.upper():
                # Предпочтительно лаборатория, но не обязательно
                pass
            
            suitable.append(classroom)
        
        if not suitable:
            # Если нет подходящих - взять любую
            suitable = self.classrooms
        
        if not suitable:
            # Если вообще нет аудиторий - создать виртуальную
            return {'id': 0, 'name': 'Unknown', 'capacity': 100}
        
        return random.choice(suitable)
    
    def _has_no_conflicts(self, chromosome: Chromosome) -> bool:
        """
        Быстрая проверка на жесткие нарушения
        
        Проверяет:
        1. Конфликты (преподаватель/группа/аудитория в одно время)
        2. Максимум 4 пары в день для студентов (ЗАКОН!)
        3. Максимум 4 пары в день для преподавателей (ЗАКОН!)
        """
        MAX_LESSONS_PER_DAY = 4  # ЖЁСТКОЕ ОГРАНИЧЕНИЕ - ЗАКОН!
        
        teacher_slots = set()
        group_slots = set()
        classroom_slots = set()
        
        # Для проверки максимума пар в день
        group_day_lessons = {}  # {(group_id, day, week): set(slots)}
        teacher_day_lessons = {}  # {(teacher_id, day, week): set(slots)}
        
        for lesson in chromosome.lessons:
            key = (lesson.day, lesson.slot, lesson.week)
            
            # Проверка конфликтов
            teacher_key = (lesson.teacher_id,) + key
            if teacher_key in teacher_slots:
                return False
            teacher_slots.add(teacher_key)
            
            group_key = (lesson.group_id,) + key
            if group_key in group_slots:
                return False
            group_slots.add(group_key)
            
            classroom_key = (lesson.classroom_id,) + key
            if classroom_key in classroom_slots:
                return False
            classroom_slots.add(classroom_key)
            
            # Проверка максимума пар в день для студентов
            group_day_key = (lesson.group_id, lesson.day, lesson.week)
            if group_day_key not in group_day_lessons:
                group_day_lessons[group_day_key] = set()
            group_day_lessons[group_day_key].add(lesson.slot)
            
            # Проверка максимума пар в день для преподавателей
            teacher_day_key = (lesson.teacher_id, lesson.day, lesson.week)
            if teacher_day_key not in teacher_day_lessons:
                teacher_day_lessons[teacher_day_key] = set()
            teacher_day_lessons[teacher_day_key].add(lesson.slot)
        
        # Проверить максимум пар в день для студентов
        for key, slots in group_day_lessons.items():
            if len(slots) > MAX_LESSONS_PER_DAY:
                return False  # ЖЁСТКОЕ НАРУШЕНИЕ - ЗАКОН!
        
        # Проверить максимум пар в день для преподавателей
        for key, slots in teacher_day_lessons.items():
            if len(slots) > MAX_LESSONS_PER_DAY:
                return False  # ЖЁСТКОЕ НАРУШЕНИЕ - ЗАКОН!
        
        return True

