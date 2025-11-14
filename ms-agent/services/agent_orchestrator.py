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
        academic_year: Optional[str] = None,
        demo_mode: bool = False
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
            
            # Вычислить academic_year если не передан
            if not academic_year:
                from datetime import datetime
                current_year = datetime.now().year
                # Учебный год: если сентябрь-декабрь, то текущий/следующий, иначе предыдущий/текущий
                current_month = datetime.now().month
                if current_month >= 9:  # Сентябрь-декабрь
                    academic_year = f"{current_year}/{current_year + 1}"
                else:  # Январь-август
                    academic_year = f"{current_year - 1}/{current_year}"
            
            logger.info(f"🚀 Starting schedule generation for semester {semester}, academic year {academic_year}")
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
            
            # Используем простой генератор + агент (без ГА)
            logger.info("🤖 Using Simple Generator + LLM Agent")
            
            # Запустить генерацию в фоне
            import threading
            
            def run_generation():
                """Запустить генерацию в фоновом потоке"""
                try:
                    from services.simple_schedule_generator import SimpleScheduleGenerator
                    
                    # Загрузить аудитории
                    classrooms = db.execute_query(
                        "SELECT id, name, capacity, classroom_type FROM classrooms WHERE is_active = true",
                        {},
                        fetch=True
                    )
                    
                    logger.info(f"📚 Loaded {len(classrooms)} classrooms")
                    
                    # Создать простой генератор
                    generator = SimpleScheduleGenerator(course_loads, classrooms)
                    
                    # Сгенерировать начальное расписание
                    logger.info("🎲 Generating initial schedule...")
                    initial_schedule = generator.generate()
                    
                    logger.info(f"✅ Generated {len(initial_schedule)} lessons")
                    
                    # Получить актуальные имена преподавателей из БД напрямую
                    teacher_names_cache = {}
                    teacher_ids = set(lesson.get('teacher_id', 0) for lesson in initial_schedule if lesson.get('teacher_id', 0) > 0)
                    if teacher_ids:
                        logger.info(f"📋 Fetching actual teacher names for {len(teacher_ids)} teachers from database (initial schedule)")
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
                    for lesson in initial_schedule:
                        teacher_id = lesson.get('teacher_id', 0)
                        if teacher_id > 0 and teacher_id in teacher_names_cache:
                            old_name = lesson.get('teacher_name', '')
                            lesson['teacher_name'] = teacher_names_cache[teacher_id]
                            if old_name != teacher_names_cache[teacher_id]:
                                updated_count += 1
                                logger.info(f"  🔄 Updated lesson teacher_name: teacher_id={teacher_id}, old='{old_name}', new='{teacher_names_cache[teacher_id]}'")
                    if updated_count > 0:
                        logger.info(f"✅ Updated {updated_count} lessons with actual teacher names")
                    
                    # Оценить начальное расписание
                    initial_result = fitness_calculator.calculate(initial_schedule, teacher_preferences)
                    initial_score = initial_result['total_score']
                    
                    logger.info(f"📊 Initial score: {initial_score}")
                    
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
                    
                    # Деактивировать старые расписания перед сохранением нового
                    db.execute_query(
                        schedule_queries.DEACTIVATE_OLD_SCHEDULES,
                        {},
                        fetch=False
                    )
                    logger.info("🔄 Deactivated old schedules")
                    
                    # КРИТИЧЕСКАЯ ОЧИСТКА: Удалить все неактивные расписания старше текущей генерации
                    # чтобы избежать путаницы и дубликатов
                    db.execute_query(
                        """
                        DELETE FROM schedules
                        WHERE is_active = false
                        AND (generation_id IS NULL OR generation_id < %(generation_id)s)
                        """,
                        {'generation_id': generation_id},
                        fetch=False
                    )
                    logger.info(f"🧹 Cleaned up old inactive schedules")
                    
                    # КРИТИЧЕСКАЯ ПРОВЕРКА: Проверить дубликаты в начальном расписании перед сохранением
                    seen_slots = {}  # {(day, time_slot, teacher_id, group_id): lesson}
                    duplicates = []
                    for lesson in initial_schedule:
                        day = lesson.get('day_of_week')
                        slot = lesson.get('time_slot')
                        teacher_id = lesson.get('teacher_id')
                        group_id = lesson.get('group_id')
                        slot_key = (day, slot, teacher_id, group_id)
                        
                        if slot_key in seen_slots:
                            duplicates.append({
                                'existing': seen_slots[slot_key],
                                'duplicate': lesson
                            })
                            logger.error(
                                f"❌ DUPLICATE DETECTED in initial_schedule! "
                                f"Slot (day={day}, slot={slot}, teacher={teacher_id}, group={group_id}) "
                                f"Existing: {seen_slots[slot_key].get('discipline_name')}, "
                                f"Duplicate: {lesson.get('discipline_name')}"
                            )
                        else:
                            seen_slots[slot_key] = lesson
                    
                    if duplicates:
                        logger.error(
                            f"❌ CRITICAL: Found {len(duplicates)} duplicate lessons in initial_schedule! "
                            f"Removing duplicates before saving."
                        )
                        # Удалить дубликаты из initial_schedule
                        initial_schedule = list(seen_slots.values())
                        logger.info(f"✅ After removing duplicates: {len(initial_schedule)} unique lessons")
                    
                    # Сохранить начальное расписание в БД
                    saved_count = 0
                    skipped_count = 0
                    for lesson in initial_schedule:
                        # КРИТИЧЕСКАЯ ФИНАЛЬНАЯ ПРОВЕРКА: Воскресенье (0 или 7) ЗАПРЕЩЕНО!
                        day_of_week = lesson.get('day_of_week')
                        if day_of_week == 0 or day_of_week == 7 or day_of_week < 1 or day_of_week > 6:
                            logger.error(
                                f"CRITICAL ERROR: Attempting to save lesson with invalid day_of_week={day_of_week}! "
                                f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN! "
                                f"Lesson: discipline={lesson.get('discipline_name')}, "
                                f"teacher={lesson.get('teacher_id')}, group={lesson.get('group_id')}. "
                                f"SKIPPING SAVE!"
                            )
                            continue  # НЕ сохраняем занятие с воскресеньем!
                        
                        try:
                            db.execute_query(
                                schedule_queries.INSERT_SCHEDULE,
                                {
                                    'generation_id': generation_id,
                                    'course_load_id': lesson['course_load_id'],
                                    'day_of_week': day_of_week,  # Используем проверенное значение
                                    'time_slot': lesson['time_slot'],
                                    'classroom_id': lesson.get('classroom_id') or None,
                                    'classroom_name': lesson.get('classroom_name') or None,
                                    'teacher_id': lesson['teacher_id'],
                                    'teacher_name': lesson.get('teacher_name', ''),
                                    'group_id': lesson['group_id'],
                                    'group_name': lesson.get('group_name', ''),
                                    'discipline_name': lesson['discipline_name'],
                                    'lesson_type': lesson['lesson_type'],
                                    'is_active': True,
                                    'semester': semester,
                                    'academic_year': academic_year
                                },
                                fetch=False
                            )
                            saved_count += 1
                        except Exception as e:
                            logger.error(
                                f"❌ Failed to save lesson {lesson.get('id')} "
                                f"(day={day_of_week}, slot={lesson.get('time_slot')}, "
                                f"teacher={lesson.get('teacher_id')}, group={lesson.get('group_id')}): {e}"
                            )
                            skipped_count += 1
                    
                    logger.info(
                        f"💾 Saved initial schedule: {saved_count} lessons saved, {skipped_count} skipped. "
                        f"Using semester={semester}, academic_year={academic_year}"
                    )
                    
                    # КРИТИЧЕСКАЯ ПРОВЕРКА: Удалить дубликаты из БД после сохранения
                    # Дубликаты - это записи с одинаковым (day_of_week, time_slot, teacher_id, group_id)
                    # оставляем только самую новую запись (с максимальным id)
                    cleanup_result = db.execute_query(
                        """
                        DELETE FROM schedules
                        WHERE id IN (
                            SELECT id
                            FROM (
                                SELECT id,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY day_of_week, time_slot, teacher_id, group_id, generation_id
                                        ORDER BY id DESC
                                    ) as rn
                                FROM schedules
                                WHERE is_active = true AND generation_id = %(generation_id)s
                            ) ranked
                            WHERE rn > 1
                        )
                        RETURNING id
                        """,
                        {'generation_id': generation_id},
                        fetch=True
                    )
                    if cleanup_result:
                        logger.warning(
                            f"⚠️ Removed {len(cleanup_result)} duplicate schedules from database for generation_id={generation_id}"
                        )
                    
                    # Проверить дубликаты по group_id и day_of_week, time_slot
                    # В один слот может быть только одна пара для группы!
                    group_duplicates = db.execute_query(
                        """
                        SELECT day_of_week, time_slot, group_id, COUNT(*) as count
                        FROM schedules
                        WHERE is_active = true AND generation_id = %(generation_id)s
                        GROUP BY day_of_week, time_slot, group_id
                        HAVING COUNT(*) > 1
                        """,
                        {'generation_id': generation_id},
                        fetch=True
                    )
                    if group_duplicates:
                        logger.error(
                            f"❌ CRITICAL: Found {len(group_duplicates)} duplicate slots in database! "
                            f"One group has multiple lessons in the same slot: {group_duplicates}"
                        )
                        # Удалить дубликаты, оставив только одну запись (с минимальным id)
                        removed_count = db.execute_query(
                            """
                            DELETE FROM schedules
                            WHERE id IN (
                                SELECT id
                                FROM (
                                    SELECT id,
                                        ROW_NUMBER() OVER (
                                            PARTITION BY day_of_week, time_slot, group_id
                                            ORDER BY id ASC
                                        ) as rn
                                    FROM schedules
                                    WHERE is_active = true AND generation_id = %(generation_id)s
                                ) ranked
                                WHERE rn > 1
                            )
                            RETURNING id
                            """,
                            {'generation_id': generation_id},
                            fetch=True
                        )
                        if removed_count:
                            logger.info(f"🧹 Removed {len(removed_count)} duplicate slots from database")
                    
                    # Проверить, что начальное расписание сохранено и активно
                    if initial_schedule:
                        logger.info(f"✅ Initial schedule with generation_id={generation_id} is ACTIVE")
                    
                    # Запустить агента для оптимизации (опционально)
                    if max_iterations and max_iterations > 0:
                        
                        import os
                        use_demo = True  
                        
                        if use_demo:
                            
                            logger.info(f"🤖 Starting agent optimization ({max_iterations} iterations)...")
                            agent = Stage1Agent(generation_id, initial_schedule, teacher_preferences)
                            result = agent.run_demo(max_iterations or 5)
                        else:
                            logger.info(f"🤖 Starting agent optimization ({max_iterations} iterations)...")
                            agent = Stage1Agent(generation_id, initial_schedule, teacher_preferences)
                            result = agent.run(max_iterations or 5)
                        
                        if result.get('success'):
                            final_score = result.get('best_score', initial_score)
                            logger.info(f"✅ Optimization completed. Final score: {final_score}")
                            
                            # Сохранить оптимизированное расписание
                            optimized_schedule = agent.schedule_state.current_schedule
                            if optimized_schedule:
                                logger.info(f"💾 Saving optimized schedule ({len(optimized_schedule)} lessons)...")
                                logger.info(f"   Semester: {semester}, Academic Year: {academic_year}")
                                
                                # Получить актуальные имена преподавателей из БД напрямую для оптимизированного расписания
                                teacher_names_cache = {}
                                teacher_ids = set(lesson.get('teacher_id', 0) for lesson in optimized_schedule if lesson.get('teacher_id', 0) > 0)
                                if teacher_ids:
                                    logger.info(f"📋 Fetching actual teacher names for {len(teacher_ids)} teachers from database (optimized schedule)")
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
                                
                                # Обновить teacher_name в оптимизированном расписании актуальными данными
                                updated_count = 0
                                for lesson in optimized_schedule:
                                    teacher_id = lesson.get('teacher_id', 0)
                                    if teacher_id > 0 and teacher_id in teacher_names_cache:
                                        old_name = lesson.get('teacher_name', '')
                                        lesson['teacher_name'] = teacher_names_cache[teacher_id]
                                        if old_name != teacher_names_cache[teacher_id]:
                                            updated_count += 1
                                            logger.info(f"  🔄 Updated optimized lesson teacher_name: teacher_id={teacher_id}, old='{old_name}', new='{teacher_names_cache[teacher_id]}'")
                                if updated_count > 0:
                                    logger.info(f"✅ Updated {updated_count} optimized lessons with actual teacher names")
                                
                                # КРИТИЧЕСКАЯ ПРОВЕРКА 1: Удалить занятия на воскресенье (day 0 или 7)
                                sunday_lessons = [l for l in optimized_schedule if l.get('day_of_week') == 0 or l.get('day_of_week') == 7]
                                if sunday_lessons:
                                    logger.error(
                                        f"❌ CRITICAL: Found {len(sunday_lessons)} lessons with Sunday (day 0 or 7) in optimized_schedule! "
                                        f"Removing them before saving."
                                    )
                                    optimized_schedule = [l for l in optimized_schedule if l.get('day_of_week') not in [0, 7]]
                                
                                # КРИТИЧЕСКАЯ ПРОВЕРКА 2: Удалить занятия с невалидным day_of_week (< 1 or > 6)
                                invalid_lessons = [l for l in optimized_schedule if l.get('day_of_week', 0) < 1 or l.get('day_of_week', 0) > 6]
                                if invalid_lessons:
                                    logger.error(
                                        f"❌ CRITICAL: Found {len(invalid_lessons)} lessons with invalid day_of_week in optimized_schedule! "
                                        f"Removing them before saving."
                                    )
                                    optimized_schedule = [l for l in optimized_schedule if 1 <= l.get('day_of_week', 0) <= 6]
                                
                                # КРИТИЧЕСКАЯ ПРОВЕРКА 3: Проверить дубликаты в оптимизированном расписании перед сохранением
                                # Дубликаты - это занятия с одинаковым (day, time_slot, group_id)
                                seen_slots = {}  # {(day, time_slot, group_id): lesson}
                                duplicates = []
                                for lesson in optimized_schedule:
                                    day = lesson.get('day_of_week')
                                    slot = lesson.get('time_slot')
                                    group_id = lesson.get('group_id')
                                    # КРИТИЧНО: В один слот может быть ТОЛЬКО ОДНА ПАРА для группы!
                                    slot_key = (day, slot, group_id)
                                    
                                    if slot_key in seen_slots:
                                        duplicates.append({
                                            'existing': seen_slots[slot_key],
                                            'duplicate': lesson
                                        })
                                        logger.error(
                                            f"❌ DUPLICATE DETECTED in optimized_schedule! "
                                            f"Slot (day={day}, slot={slot}, group={group_id}) "
                                            f"Existing: {seen_slots[slot_key].get('discipline_name')}, teacher={seen_slots[slot_key].get('teacher_id')}, "
                                            f"Duplicate: {lesson.get('discipline_name')}, teacher={lesson.get('teacher_id')}"
                                        )
                                    else:
                                        seen_slots[slot_key] = lesson
                                
                                if duplicates:
                                    logger.error(
                                        f"❌ CRITICAL: Found {len(duplicates)} duplicate lessons in optimized_schedule! "
                                        f"Removing duplicates before saving."
                                    )
                                    # Удалить дубликаты из optimized_schedule (оставляем только первое вхождение)
                                    optimized_schedule = list(seen_slots.values())
                                    logger.info(f"✅ After removing duplicates: {len(optimized_schedule)} unique lessons")
                                
                                # Удалить старое расписание с этим generation_id (начальное)
                                db.execute_query(
                                    schedule_queries.DELETE_SCHEDULES_BY_GENERATION,
                                    {'generation_id': generation_id},
                                    fetch=False
                                )
                                logger.info(f"🗑️ Deleted old schedule for generation_id={generation_id}")
                                
                                # Деактивировать все остальные активные расписания
                                db.execute_query(
                                    schedule_queries.DEACTIVATE_OLD_SCHEDULES,
                                    {},
                                    fetch=False
                                )
                                logger.info("🔄 Deactivated all old active schedules")
                                
                                # Сохранить оптимизированное расписание
                                saved_count = 0
                                skipped_count = 0
                                for lesson in optimized_schedule:
                                    # КРИТИЧЕСКАЯ ФИНАЛЬНАЯ ПРОВЕРКА: Воскресенье (0 или 7) ЗАПРЕЩЕНО!
                                    day_of_week = lesson.get('day_of_week', 1)
                                    if day_of_week == 0 or day_of_week == 7 or day_of_week < 1 or day_of_week > 6:
                                        logger.error(
                                            f"CRITICAL ERROR: Attempting to save optimized lesson with invalid day_of_week={day_of_week}! "
                                            f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN! "
                                            f"Lesson: discipline={lesson.get('discipline_name')}, "
                                            f"teacher={lesson.get('teacher_id')}, group={lesson.get('group_id')}. "
                                            f"SKIPPING SAVE!"
                                        )
                                        continue  # НЕ сохраняем занятие с воскресеньем!
                                    
                                    try:
                                        db.execute_query(
                                            schedule_queries.INSERT_SCHEDULE,
                                            {
                                                'generation_id': generation_id,
                                                'course_load_id': lesson.get('course_load_id', 0),
                                                'day_of_week': day_of_week,  # Используем проверенное значение
                                                'time_slot': lesson.get('time_slot', 1),
                                                'classroom_id': lesson.get('classroom_id') or None,
                                                'classroom_name': lesson.get('classroom_name') or None,
                                                'teacher_id': lesson.get('teacher_id', 0),
                                                'teacher_name': lesson.get('teacher_name', ''),
                                                'group_id': lesson.get('group_id', 0),
                                                'group_name': lesson.get('group_name', ''),
                                                'discipline_name': lesson.get('discipline_name', ''),
                                                'lesson_type': lesson.get('lesson_type', 'Практика'),
                                                'is_active': True,
                                                'semester': semester,
                                                'academic_year': academic_year
                                            },
                                            fetch=False
                                        )
                                        saved_count += 1
                                    except Exception as e:
                                        logger.error(
                                            f"❌ Failed to save optimized lesson {lesson.get('id')} "
                                            f"(day={day_of_week}, slot={lesson.get('time_slot')}, "
                                            f"teacher={lesson.get('teacher_id')}, group={lesson.get('group_id')}): {e}"
                                        )
                                        skipped_count += 1
                                logger.info(
                                    f"✅ Optimized schedule saved successfully: {saved_count}/{len(optimized_schedule)} lessons saved, {skipped_count} skipped. "
                                    f"Using semester={semester}, academic_year={academic_year}"
                                )
                                
                                # КРИТИЧЕСКАЯ ПРОВЕРКА: Удалить дубликаты из БД после сохранения оптимизированного расписания
                                cleanup_result = db.execute_query(
                                    """
                                    DELETE FROM schedules
                                    WHERE id IN (
                                        SELECT id
                                        FROM (
                                            SELECT id,
                                                ROW_NUMBER() OVER (
                                                    PARTITION BY day_of_week, time_slot, teacher_id, group_id, generation_id
                                                    ORDER BY id DESC
                                                ) as rn
                                            FROM schedules
                                            WHERE is_active = true AND generation_id = %(generation_id)s
                                        ) ranked
                                        WHERE rn > 1
                                    )
                                    RETURNING id
                                    """,
                                    {'generation_id': generation_id},
                                    fetch=True
                                )
                                if cleanup_result:
                                    logger.warning(
                                        f"⚠️ Removed {len(cleanup_result)} duplicate schedules from database after optimization for generation_id={generation_id}"
                                    )
                                
                                # Проверить дубликаты по group_id и day_of_week, time_slot
                                group_duplicates = db.execute_query(
                                    """
                                    SELECT day_of_week, time_slot, group_id, COUNT(*) as count
                                    FROM schedules
                                    WHERE is_active = true AND generation_id = %(generation_id)s
                                    GROUP BY day_of_week, time_slot, group_id
                                    HAVING COUNT(*) > 1
                                    """,
                                    {'generation_id': generation_id},
                                    fetch=True
                                )
                                if group_duplicates:
                                    logger.error(
                                        f"❌ CRITICAL: Found {len(group_duplicates)} duplicate slots in database after optimization! "
                                        f"One group has multiple lessons in the same slot: {group_duplicates}"
                                    )
                                    # Удалить дубликаты, оставив только одну запись (с минимальным id)
                                    removed_count = db.execute_query(
                                        """
                                        DELETE FROM schedules
                                        WHERE id IN (
                                            SELECT id
                                            FROM (
                                                SELECT id,
                                                    ROW_NUMBER() OVER (
                                                        PARTITION BY day_of_week, time_slot, group_id
                                                        ORDER BY id ASC
                                                    ) as rn
                                                FROM schedules
                                                WHERE is_active = true AND generation_id = %(generation_id)s
                                            ) ranked
                                            WHERE rn > 1
                                        )
                                        RETURNING id
                                        """,
                                        {'generation_id': generation_id},
                                        fetch=True
                                    )
                                    if removed_count:
                                        logger.info(f"🧹 Removed {len(removed_count)} duplicate slots from database after optimization")
                                
                                logger.info(f"✅ Schedule with generation_id={generation_id} is now ACTIVE")
                        else:
                            logger.warning(f"⚠️ Optimization failed: {result.get('error')}")
                    
                    # Обновить статус на завершено
                    db.execute_query(
                        gen_queries.UPDATE_GENERATION_STATUS,
                        {
                            'job_id': job_id,
                            'status': 'completed',
                            'error_message': None
                        },
                        fetch=False
                    )
                    
                    logger.info(f"✅ Generation completed successfully: {job_id}")
                    
                except Exception as e:
                    logger.error(f"Error in background generation: {e}", exc_info=True)
                    db.execute_query(
                        gen_queries.UPDATE_GENERATION_STATUS,
                        {
                            'job_id': job_id,
                            'status': 'failed',
                            'error_message': str(e)
                        },
                        fetch=False
                    )
            
            # Запустить в отдельном потоке
            thread = threading.Thread(target=run_generation, daemon=True)
            thread.start()
            
            # Сразу вернуть job_id
            return {
                'success': True,
                'job_id': job_id,
                'message': 'Generation started successfully'
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
            self._save_schedule(optimized_schedule, generation_id, semester=None, academic_year=None)
            
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
    
    def _save_schedule(self, schedule: list, generation_id: int, semester: Optional[int] = None, academic_year: Optional[str] = None):
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
                    'is_active': True,
                    'semester': semester,
                    'academic_year': academic_year
                },
                fetch=False
            )


# Singleton instance
agent_orchestrator = AgentOrchestrator()

