"""
Agent Orchestrator
Оркестратор двухэтапной генерации расписания
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from services.stage1_agent import Stage1Agent
from services.initial_schedule import InitialScheduleGenerator
from services.fitness import fitness_calculator
from services.generation_orchestrator import GenerationOrchestrator
from db.connection import db
from db.queries import (
    course_loads as load_queries,
    generation_history as gen_queries,
    schedules as schedule_queries,
    teacher_preferences as pref_queries
)
from config import config

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrator для управления процессом генерации"""
    
    def __init__(self):
        self.running_jobs = {}  # {job_id: orchestrator_instance}
    
    def start_generation(
        self,
        semester: int,
        max_iterations: Optional[int] = None,
        skip_stage1: bool = False,
        skip_stage2: bool = False,
        created_by: Optional[int] = None,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Запустить генерацию расписания
        
        Args:
            semester: Номер семестра (1 или 2)
            max_iterations: Максимум итераций (default: config.MAX_ITERATIONS)
            skip_stage1: Пропустить Stage 1 (использовать существующее расписание)
            skip_stage2: Пропустить Stage 2 (не назначать аудитории)
            created_by: ID пользователя
        
        Returns:
            {'success': bool, 'job_id': str, 'message': str}
        """
        try:
            # Сгенерировать job_id
            job_id = str(uuid.uuid4())
            
            logger.info(f"🚀 Starting schedule generation for semester {semester}")
            logger.info(f"Job ID: {job_id}")
            
            # Загрузить нагрузки
            course_loads = db.execute_query(
                load_queries.SELECT_COURSE_LOADS_BY_SEMESTER,
                {'semester': semester},
                fetch=True
            )
            
            if not course_loads:
                error_msg = f"No course loads found for semester {semester}. Please create course loads first using /api/course-loads endpoint."
                logger.warning(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            logger.info(f"📚 Loaded {len(course_loads)} course loads")
            
            # Загрузить предпочтения преподавателей
            teacher_prefs_raw = db.execute_query(
                pref_queries.SELECT_ALL_PREFERENCES,
                {},
                fetch=True
            )
            
            teacher_preferences = {}
            for row in teacher_prefs_raw:
                teacher_preferences[row['teacher_id']] = row['preferences']
            
            logger.info(f"👥 Loaded preferences for {len(teacher_preferences)} teachers")
            
            # Создать запись о генерации
            generation_result = db.execute_query(
                gen_queries.INSERT_GENERATION,
                {
                    'job_id': job_id,
                    'stage': 1,
                    'stage_name': 'temporal',
                    'status': 'running',
                    'max_iterations': max_iterations or config.MAX_ITERATIONS,
                    'initial_score': None,
                    'created_by': created_by
                },
                fetch=True
            )
            
            generation_id = generation_result[0]['id']
            
            # Всегда используем ГА с LLM агентом
            logger.info("🧬 Using Genetic Algorithm + LLM Agent (hybrid approach)")
            ga_orchestrator = GenerationOrchestrator()
            
            # Запустить асинхронно (но синхронно для простоты)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                ga_orchestrator.generate_schedule(
                    generation_id=generation_id,
                    semester=semester,
                    academic_year=academic_year or "2024/2025",
                    population_size=50,
                    max_iterations=max_iterations or 100
                )
            )
            
            # Проверить результат генерации
            if not result.get('success', False):
                return {
                    'success': False,
                    'error': result.get('error', 'Generation failed')
                }
            
            return {
                'success': True,
                'job_id': job_id,
                'message': 'Generation completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to start generation: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_generation_sync(
        self,
        generation_id: int,
        job_id: str,
        course_loads: list,
        teacher_preferences: dict,
        max_iterations: int,
        skip_stage1: bool,
        skip_stage2: bool
    ) -> Dict[str, Any]:
        """Запустить генерацию синхронно"""
        try:
            # Stage 1: Temporal Optimization
            if not skip_stage1:
                logger.info("=" * 60)
                logger.info("STAGE 1: TEMPORAL OPTIMIZATION")
                logger.info("=" * 60)
                
                # Сгенерировать начальное расписание
                logger.info("Generating initial schedule...")
                generator = InitialScheduleGenerator(course_loads, teacher_preferences)
                initial_schedule = generator.generate()
                
                # Оценить
                initial_result = fitness_calculator.calculate(initial_schedule, teacher_preferences)
                initial_score = initial_result['total_score']
                
                # Обновить БД
                db.execute_query(
                    gen_queries.UPDATE_GENERATION_ITERATION,
                    {
                        'job_id': job_id,
                        'current_iteration': 0,
                        'current_score': initial_score,
                        'last_reasoning': 'Initial schedule generated'
                    },
                    fetch=False
                )
                
                # Запустить оптимизацию
                agent = Stage1Agent(generation_id, initial_schedule, teacher_preferences)
                stage1_result = agent.run(max_iterations)
                
                if not stage1_result['success']:
                    raise Exception("Stage 1 failed")
                
                optimized_schedule = stage1_result['schedule']
                
            else:
                logger.info("⏭️ Skipping Stage 1 (using existing schedule)")
                # Загрузить активное расписание
                optimized_schedule = db.execute_query(
                    schedule_queries.SELECT_ACTIVE_SCHEDULES,
                    {},
                    fetch=True
                )
            
            # Сохранить расписание в БД
            logger.info("💾 Saving schedule to database...")
            self._save_schedule(optimized_schedule, generation_id)
            
            # Stage 2: Classroom Assignment (TODO: implement)
            if not skip_stage2:
                logger.info("⏭️ Stage 2 not yet implemented")
            
            # Завершить
            db.execute_query(
                gen_queries.UPDATE_GENERATION_STATUS,
                {
                    'job_id': job_id,
                    'status': 'completed',
                    'error_message': None
                },
                fetch=False
            )
            
            logger.info(f"✅ Generation {job_id} completed successfully!")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            
            # Обновить статус
            db.execute_query(
                gen_queries.UPDATE_GENERATION_STATUS,
                {
                    'job_id': job_id,
                    'status': 'failed',
                    'error_message': str(e)
                },
                fetch=False
            )
            
            return {'success': False, 'error': str(e)}
    
    def _save_schedule(self, schedule: list, generation_id: int):
        """Сохранить расписание в БД"""
        # Деактивировать старые
        db.execute_query(
            schedule_queries.DEACTIVATE_OLD_SCHEDULES,
            {},
            fetch=False
        )
        
        # Вставить новое
        for lesson in schedule:
            db.execute_query(
                schedule_queries.INSERT_SCHEDULE,
                {
                    'course_load_id': lesson['course_load_id'],
                    'day_of_week': lesson['day_of_week'],
                    'time_slot': lesson['time_slot'],
                    'classroom_id': lesson.get('classroom_id'),
                    'classroom_name': lesson.get('classroom_name'),
                    'teacher_id': lesson['teacher_id'],
                    'teacher_name': lesson['teacher_name'],
                    'group_id': lesson['group_id'],
                    'group_name': lesson['group_name'],
                    'discipline_name': lesson['discipline_name'],
                    'lesson_type': lesson['lesson_type'],
                    'generation_id': generation_id,
                    'is_active': True
                },
                fetch=False
            )


# Singleton instance
agent_orchestrator = AgentOrchestrator()

