"""
LLM Agent Improver для генетического алгоритма
Использование Stage1Agent для локальной оптимизации лучших расписаний
"""
import logging
from typing import List, Dict
from utils.chromosome import Chromosome, Lesson
from services.stage1_agent import Stage1Agent

logger = logging.getLogger(__name__)


class LLMAgentImprover:
    """Улучшение через Stage1Agent (LLM с инструментами)"""
    
    def __init__(self, generation_id: int, teacher_preferences: Dict, 
                 classrooms: List[Dict] = None, groups: Dict = None):
        self.generation_id = generation_id
        self.teacher_preferences = teacher_preferences
        self.classrooms = classrooms or []
        self.groups = groups or {}
    
    def improve_top_chromosomes(self,
                               chromosomes: List[Chromosome],
                               max_iterations: int = 5,
                               top_n: int = 3) -> List[Chromosome]:
        """
        Улучшить топ-N расписаний через Stage1Agent
        
        Args:
            chromosomes: Список хромосом
            max_iterations: Максимум итераций для каждого улучшения
            top_n: Количество лучших для улучшения
        
        Returns:
            Улучшенные хромосомы
        """
        sorted_chroms = sorted(
            chromosomes,
            key=lambda c: c.fitness,
            reverse=True
        )
        top = sorted_chroms[:top_n]
        
        improved = []
        
        for i, chromosome in enumerate(top):
            try:
                logger.info(
                    f"🤖 Improving chromosome {i + 1}/{top_n} "
                    f"via Stage1Agent (LLM with tools)"
                )
                
                # Преобразовать Chromosome в формат для Stage1Agent
                schedule_dict = self._chromosome_to_schedule(chromosome)
                
                # Создать агента
                agent = Stage1Agent(
                    generation_id=self.generation_id,
                    initial_schedule=schedule_dict,
                    teacher_preferences=self.teacher_preferences
                )
                
                # Запустить оптимизацию
                result = agent.run(max_iterations=max_iterations)
                
                if result.get('success'):
                    # Преобразовать обратно в Chromosome
                    improved_schedule = result.get('schedule', schedule_dict)
                    improved_chromosome = self._schedule_to_chromosome(
                        improved_schedule,
                        chromosome
                    )
                    
                    # Пересчитать fitness с учетом новых параметров
                    from services.fitness_calculator import FitnessCalculator
                    fitness_calc = FitnessCalculator(
                        teacher_preferences=self.teacher_preferences,
                        classrooms=self.classrooms,
                        groups=self.groups
                    )
                    fitness_calc.calculate(improved_chromosome)
                    
                    improved.append(improved_chromosome)
                    
                    logger.info(
                        f"✅ Improved: {chromosome.fitness:.0f} → "
                        f"{improved_chromosome.fitness:.0f}"
                    )
                else:
                    logger.warning("Stage1Agent failed, keeping original")
                    improved.append(chromosome)
                    
            except Exception as e:
                logger.error(f"Error improving chromosome {i + 1}: {e}")
                improved.append(chromosome)
        
        return improved
    
    def _chromosome_to_schedule(self, chromosome: Chromosome) -> List[Dict]:
        """Преобразовать Chromosome в формат для Stage1Agent"""
        schedule = []
        
        for idx, lesson in enumerate(chromosome.lessons):
            schedule.append({
                'id': idx,  # Уникальный индекс
                'course_load_id': lesson.course_load_id,
                'discipline_name': lesson.discipline_name,
                'lesson_type': lesson.lesson_type,
                'group_id': lesson.group_id,
                'group_name': lesson.group_name,
                'teacher_id': lesson.teacher_id,
                'teacher_name': lesson.teacher_name,
                'classroom_id': lesson.classroom_id,
                'day_of_week': lesson.day,
                'time_slot': lesson.slot,
                'week_number': lesson.week,
                'teacher_priority': self._get_teacher_priority(lesson.teacher_id)
            })
        
        return schedule
    
    def _schedule_to_chromosome(self,
                               schedule: List[Dict],
                               original: Chromosome) -> Chromosome:
        """Преобразовать расписание обратно в Chromosome"""
        lessons = []
        
        # Создать маппинг по индексу
        original_lessons = list(original.lessons)
        
        for lesson_dict in schedule:
            lesson_id = lesson_dict.get('id', -1)
            
            # Найти оригинальный lesson по индексу
            if 0 <= lesson_id < len(original_lessons):
                original_lesson = original_lessons[lesson_id]
                # Обновить день и слот
                lesson = original_lesson.copy()
                lesson.day = lesson_dict.get('day_of_week', lesson.day)
                lesson.slot = lesson_dict.get('time_slot', lesson.slot)
                lessons.append(lesson)
            else:
                # Создать новый lesson из словаря
                lesson = Lesson(
                    course_load_id=lesson_dict.get('course_load_id', 0),
                    discipline_name=lesson_dict.get('discipline_name', ''),
                    lesson_type=lesson_dict.get('lesson_type', 'Практика'),
                    group_id=lesson_dict.get('group_id', 0),
                    group_name=lesson_dict.get('group_name', ''),
                    teacher_id=lesson_dict.get('teacher_id', 0),
                    teacher_name=lesson_dict.get('teacher_name', ''),
                    classroom_id=lesson_dict.get('classroom_id', 0),
                    day=lesson_dict.get('day_of_week', 1),
                    slot=lesson_dict.get('time_slot', 1),
                    week=lesson_dict.get('week_number', 1)
                )
                lessons.append(lesson)
        
        return Chromosome(lessons)
    
    def _get_teacher_priority(self, teacher_id: int) -> int:
        """Получить приоритет преподавателя"""
        if teacher_id in self.teacher_preferences:
            return self.teacher_preferences[teacher_id].get('priority', 4)
        return 4

