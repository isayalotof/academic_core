"""
Generation Orchestrator для генетического алгоритма
Полный цикл генерации расписания через ГА
"""
import logging
from typing import List, Dict, Optional
from services.context_builder import ScheduleContextBuilder
from services.population_initializer import PopulationInitializer
from services.fitness_calculator import FitnessCalculator
from services.genetic_operators import (
    SelectionOperator, CrossoverOperator, MutationOperator
)
from services.gigachat_improver import GigaChatImprover
from services.llm_agent_improver import LLMAgentImprover
from db.connection import db
from db.queries import schedules as schedule_queries

logger = logging.getLogger(__name__)


class GenerationOrchestrator:
    """
    Оркестратор генетического алгоритма
    
    Процесс:
    1. Получить данные из ms-core (course_loads из Excel!)
    2. Создать 50 валидных расписаний
    3. ~100 итераций эволюции
    4. Сохранить лучшее
    """
    
    def __init__(self):
        self.context_builder = ScheduleContextBuilder()
        self.selection = SelectionOperator()
        self.crossover = CrossoverOperator()
        self.gigachat_improver = GigaChatImprover()
        self.llm_agent_improver = None  # Инициализируется позже
    
    async def generate_schedule(self,
                               generation_id: int,
                               semester: int,
                               academic_year: str,
                               group_ids: Optional[List[int]] = None,
                               population_size: int = 50,
                               max_iterations: int = 100) -> Dict:
        """Запустить генетический алгоритм"""
        
        try:
            logger.info(f"🧬 Starting GA for generation {generation_id}")
            
            # ШАГ 1: Получить данные из ms-core
            logger.info("📊 Building context from ms-core...")
            context = await self.context_builder.build_context(
                semester=semester,
                academic_year=academic_year,
                group_ids=group_ids
            )
            
            logger.info(
                f"Context: {len(context['course_loads'])} loads, "
                f"{len(context['teacher_preferences'])} teachers, "
                f"{len(context['classrooms'])} classrooms"
            )
            
            if len(context['course_loads']) == 0:
                return {
                    'success': False,
                    'message': 'No course loads found'
                }
            
            # ШАГ 2: Создать начальную популяцию
            logger.info(f"🎲 Creating population of {population_size}...")
            initializer = PopulationInitializer(context)
            population = initializer.create_population(population_size)
            
            if len(population) == 0:
                return {
                    'success': False,
                    'message': 'Failed to create initial population'
                }
            
            logger.info(f"✅ Initial population: {len(population)} chromosomes")
            
            # Инициализация операторов с учетом новых параметров
            fitness_calculator = FitnessCalculator(
                teacher_preferences=context['teacher_preferences'],
                classrooms=context['classrooms'],
                groups=context['groups']
            )
            mutation = MutationOperator(context['classrooms'])
            
            # Инициализировать LLM Agent Improver с полным контекстом
            self.llm_agent_improver = LLMAgentImprover(
                generation_id=generation_id,
                teacher_preferences=context['teacher_preferences'],
                classrooms=context['classrooms'],
                groups=context['groups']
            )
            
            # Оценить начальную популяцию
            for chromosome in population:
                fitness_calculator.calculate(chromosome)
            
            # ШАГ 3: Эволюция ~100 итераций
            best_chromosome = None
            best_fitness = float('-inf')
            
            for iteration in range(max_iterations):
                logger.info(f"=== Iteration {iteration + 1}/{max_iterations} ===")
                
                # Проверка на пустую популяцию
                if not population:
                    logger.warning("⚠️ Population is empty! Reinitializing...")
                    population = initializer.create_population(population_size)
                    for chromosome in population:
                        fitness_calculator.calculate(chromosome)
                
                # 3.1. Оценить fitness
                for chromosome in population:
                    fitness_calculator.calculate(chromosome)
                
                # 3.2. Найти лучшего
                current_best = max(population, key=lambda c: c.fitness)
                
                if current_best.fitness > best_fitness:
                    best_fitness = current_best.fitness
                    best_chromosome = current_best.copy()
                    
                    logger.info(
                        f"🏆 NEW BEST! Fitness: {best_fitness:.0f}, "
                        f"Hard violations: {best_chromosome.hard_violations}, "
                        f"Conflicts: {best_chromosome.conflicts_count}, "
                        f"Pref violations: {best_chromosome.preference_violations}"
                    )
                
                # 3.3. Элитизм
                elite = self.selection.elitism_selection(
                    population, elite_size=10
                )
                
                # 3.4. Создать новое поколение
                new_population = elite.copy()
                
                while len(new_population) < population_size:
                    # Селекция
                    parent1 = self.selection.tournament_selection(population)
                    parent2 = self.selection.tournament_selection(population)
                    
                    # Кроссовер
                    child1, child2 = self.crossover.single_point_crossover(
                        parent1, parent2
                    )
                    
                    # Мутация
                    child1 = mutation.mutate(child1, mutation_rate=0.1)
                    child2 = mutation.mutate(child2, mutation_rate=0.1)
                    
                    new_population.extend([child1, child2])
                
                new_population = new_population[:population_size]
                
                # 3.5. Отфильтровать невалидных (с жесткими нарушениями)
                valid_population = []
                for c in new_population:
                    fitness_calculator.calculate(c)
                    if c.is_valid():  # Проверяет hard_violations == 0
                        valid_population.append(c)
                
                if len(valid_population) < population_size // 2:
                    # Добавить валидных из старой популяции
                    valid_from_old = [
                        c for c in population if c.is_valid()
                    ]
                    valid_population.extend(valid_from_old)
                    valid_population = valid_population[:population_size]
                
                # Если все еще пусто, добавить лучших из старой популяции (даже невалидных)
                if not valid_population:
                    logger.warning("⚠️ No valid chromosomes! Using best from previous population...")
                    sorted_old = sorted(population, key=lambda c: c.fitness, reverse=True)
                    valid_population = sorted_old[:min(population_size, len(sorted_old))]
                
                # Если все еще пусто, пересоздать популяцию
                if not valid_population:
                    logger.warning("⚠️ Population completely lost! Reinitializing...")
                    valid_population = initializer.create_population(population_size)
                    for chromosome in valid_population:
                        fitness_calculator.calculate(chromosome)
                
                population = valid_population
                
                logger.info(f"✅ Valid: {len(population)}/{population_size}")
                
                # 3.6. Каждые 10 итераций - LLM улучшения (GigaChat + Stage1Agent)
                if (iteration + 1) % 10 == 0 and len(population) >= 3:
                    logger.info("🤖 Applying LLM improvements (GigaChat + Stage1Agent)...")
                    
                    # Шаг 1: GigaChat улучшение (быстрое, через промпты)
                    improved_gigachat = await self.gigachat_improver.improve_top_chromosomes(
                        chromosomes=population,
                        teacher_preferences=context['teacher_preferences'],
                        top_n=3
                    )
                    
                    # Пересчитать fitness для GigaChat улучшений
                    for chromosome in improved_gigachat:
                        fitness_calculator.calculate(chromosome)
                    
                    # Шаг 2: Stage1Agent улучшение (глубокое, с инструментами)
                    # Применяем к лучшим из GigaChat улучшений
                    improved_agent = self.llm_agent_improver.improve_top_chromosomes(
                        chromosomes=improved_gigachat,
                        max_iterations=5,  # Небольшое количество итераций
                        top_n=2  # Только топ-2 для глубокой оптимизации
                    )
                    
                    # Пересчитать fitness для Stage1Agent улучшений
                    for chromosome in improved_agent:
                        fitness_calculator.calculate(chromosome)
                    
                    # Добавить все улучшения в популяцию
                    population.extend(improved_gigachat)
                    population.extend(improved_agent)
                    
                    # Отфильтровать и взять лучших (только валидные)
                    valid = [c for c in population if c.is_valid()]
                    population = sorted(
                        valid,
                        key=lambda c: c.fitness,
                        reverse=True
                    )[:population_size]
                    
                    if population:
                        logger.info(
                            f"After LLM improvements: "
                            f"best fitness = {population[0].fitness:.0f}"
                        )
            
            # ШАГ 4: Сохранить лучшее (только если валидно)
            if best_chromosome and best_chromosome.is_valid():
                logger.info("💾 Saving best schedule...")
                
                await self._save_schedule(
                    generation_id=generation_id,
                    schedule=best_chromosome.to_schedule_dict(),
                    semester=semester,
                    academic_year=academic_year
                )
                
                return {
                    'success': True,
                    'generation_id': generation_id,
                    'best_chromosome': best_chromosome,
                    'statistics': {
                        'total_lessons': len(best_chromosome.lessons),
                        'hard_violations': 0,  # ГАРАНТИРОВАНО!
                        'conflicts': 0,  # ГАРАНТИРОВАНО!
                        'fitness_score': best_chromosome.fitness,
                        'preference_violations': best_chromosome.preference_violations,
                        'iterations': max_iterations
                    },
                    'message': f'Schedule generated! Fitness: {best_fitness:.0f}'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to generate valid schedule'
                }
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    async def _save_schedule(self,
                           generation_id: int,
                           schedule: List[Dict],
                           semester: int,
                           academic_year: str):
        """Сохранить расписание в БД"""
        # Получить актуальные имена преподавателей из БД напрямую
        teacher_names_cache = {}
        teacher_ids = set(lesson.get('teacher_id', 0) for lesson in schedule if lesson.get('teacher_id', 0) > 0)
        if teacher_ids:
            logger.info(f"📋 Fetching actual teacher names for {len(teacher_ids)} teachers from database (genetic algorithm)")
            try:
                # Получить актуальные имена преподавателей из таблицы teachers
                teachers_data = db.execute_query(
                    "SELECT id, full_name FROM teachers WHERE id = ANY(%(teacher_ids)s)",
                    {'teacher_ids': list(teacher_ids)},
                    fetch=True
                )
                for teacher_row in teachers_data:
                    teacher_names_cache[teacher_row['id']] = teacher_row.get('full_name', '')
                    logger.info(f"  ✅ Teacher {teacher_row['id']}: {teacher_names_cache[teacher_row['id']]}")
            except Exception as e:
                logger.error(f"  ❌ Failed to fetch teacher names from database: {e}")
        
        # Обновить teacher_name в расписании актуальными данными
        updated_count = 0
        for lesson in schedule:
            teacher_id = lesson.get('teacher_id', 0)
            if teacher_id > 0 and teacher_id in teacher_names_cache:
                old_name = lesson.get('teacher_name', '')
                lesson['teacher_name'] = teacher_names_cache[teacher_id]
                if old_name != teacher_names_cache[teacher_id]:
                    updated_count += 1
                    logger.info(f"  🔄 Updated lesson teacher_name: teacher_id={teacher_id}, old='{old_name}', new='{teacher_names_cache[teacher_id]}'")
        if updated_count > 0:
            logger.info(f"✅ Updated {updated_count} lessons with actual teacher names")
        
        # Деактивировать старые
        db.execute_query(
            schedule_queries.DEACTIVATE_OLD_SCHEDULES,
            {},
            fetch=False
        )
        
        # Вставить новое
        for lesson in schedule:
            # КРИТИЧЕСКАЯ ФИНАЛЬНАЯ ПРОВЕРКА: Воскресенье (0 или 7) ЗАПРЕЩЕНО!
            day_of_week = lesson.get('day_of_week', 1)
            if day_of_week == 0 or day_of_week == 7 or day_of_week < 1 or day_of_week > 6:
                logger.error(
                    f"CRITICAL ERROR: Attempting to save lesson with invalid day_of_week={day_of_week}! "
                    f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN! "
                    f"Lesson: discipline={lesson.get('discipline_name')}, "
                    f"teacher={lesson.get('teacher_id')}, group={lesson.get('group_id')}. "
                    f"SKIPPING SAVE!"
                )
                continue  # НЕ сохраняем занятие с воскресеньем!
            
            db.execute_query(
                schedule_queries.INSERT_SCHEDULE,
                {
                    'course_load_id': lesson.get('course_load_id', 0),
                    'day_of_week': day_of_week,  # Используем проверенное значение
                    'time_slot': lesson.get('time_slot', 1),
                    'classroom_id': lesson.get('classroom_id', 0),
                    'classroom_name': lesson.get('classroom_name'),
                    'teacher_id': lesson.get('teacher_id', 0),
                    'teacher_name': lesson.get('teacher_name', ''),
                    'group_id': lesson.get('group_id', 0),
                    'group_name': lesson.get('group_name', ''),
                    'discipline_name': lesson.get('discipline_name', ''),
                    'lesson_type': lesson.get('lesson_type', 'Практика'),
                    'generation_id': generation_id,
                    'is_active': True,
                    'semester': semester,
                    'academic_year': academic_year
                },
                fetch=False
            )
        
        logger.info(f"Saved {len(schedule)} lessons to database")

