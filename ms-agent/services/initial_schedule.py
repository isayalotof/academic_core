"""
Initial Schedule Generator
Генерация начального расписания с учётом приоритетов
"""

from typing import List, Dict, Any
import logging
import random

from services.fitness import fitness_calculator

logger = logging.getLogger(__name__)


class InitialScheduleGenerator:
    """Генератор начального расписания"""
    
    def __init__(self, course_loads: List[Dict], teacher_preferences: Dict):
        self.course_loads = course_loads
        self.teacher_preferences = teacher_preferences
        
        # Доступные слоты (6 дней x 6 пар)
        self.available_slots = [
            (day, slot) for day in range(1, 7) for slot in range(1, 7)
        ]
    
    def generate(self) -> List[Dict]:
        """
        Сгенерировать начальное расписание
        
        Стратегия:
        1. Сортировать нагрузки по приоритету преподавателей (1 = самый важный)
        2. Для Priority 1-2: назначать в предпочтительные слоты
        3. Для остальных: назначать случайно в свободные слоты
        
        Returns:
            Список занятий с временными слотами
        """
        logger.info(f"Generating initial schedule for {len(self.course_loads)} course loads...")
        
        schedule = []
        schedule_id = 1
        
        # Сортировать по приоритету
        sorted_loads = sorted(self.course_loads, key=lambda x: x['teacher_priority'])
        
        # Отслеживание занятости
        teacher_slots = {}  # {teacher_id: [(day, slot), ...]}
        group_slots = {}    # {group_id: [(day, slot), ...]}
        
        for load in sorted_loads:
            teacher_id = load['teacher_id']
            group_id = load['group_id']
            lessons_per_week = load['lessons_per_week']
            priority = load['teacher_priority']
            
            # Получить предпочтения преподавателя
            prefs = self.teacher_preferences.get(teacher_id, [])
            preferred_slots = [
                (p['day_of_week'], p['time_slot'])
                for p in prefs if p['is_preferred']
            ]
            
            # Назначить слоты для всех пар этой нагрузки
            assigned_slots = []
            
            for _ in range(lessons_per_week):
                slot = self._find_best_slot(
                    teacher_id=teacher_id,
                    group_id=group_id,
                    teacher_slots=teacher_slots,
                    group_slots=group_slots,
                    preferred_slots=preferred_slots,
                    priority=priority
                )
                
                if slot:
                    assigned_slots.append(slot)
                    teacher_slots.setdefault(teacher_id, []).append(slot)
                    group_slots.setdefault(group_id, []).append(slot)
                else:
                    logger.warning(f"Could not assign slot for teacher {teacher_id}, group {group_id}")
            
            # Создать записи расписания
            for day, time_slot in assigned_slots:
                schedule.append({
                    'id': schedule_id,
                    'course_load_id': load['id'],
                    'day_of_week': day,
                    'time_slot': time_slot,
                    'classroom_id': None,  # Stage 1: без аудиторий
                    'classroom_name': None,
                    'teacher_id': teacher_id,
                    'teacher_name': load['teacher_name'],
                    'group_id': group_id,
                    'group_name': load['group_name'],
                    'discipline_name': load['discipline_name'],
                    'lesson_type': load['lesson_type'],
                    'teacher_priority': load['teacher_priority']
                })
                schedule_id += 1
        
        logger.info(f"✅ Generated initial schedule with {len(schedule)} lessons")
        
        # Оценить начальное расписание
        result = fitness_calculator.calculate(schedule, self.teacher_preferences)
        logger.info(f"📊 Initial fitness score: {result['total_score']}")
        logger.info(f"   - Conflicts: {len(result['details']['conflicts'])}")
        logger.info(f"   - Preference violations: {len(result['details']['preference_violations'])}")
        logger.info(f"   - Isolated lessons: {len(result['details']['isolated_lessons'])}")
        
        return schedule
    
    def _find_best_slot(
        self,
        teacher_id: int,
        group_id: int,
        teacher_slots: Dict,
        group_slots: Dict,
        preferred_slots: List[tuple],
        priority: int
    ) -> tuple:
        """Найти лучший свободный слот"""
        
        # Для Priority 1-2: строго предпочтительные слоты
        if priority <= 2 and preferred_slots:
            for slot in preferred_slots:
                if self._is_slot_free(slot, teacher_id, group_id, teacher_slots, group_slots):
                    return slot
        
        # Для Priority 3: попытаться предпочтительные, иначе любой
        if priority == 3 and preferred_slots:
            for slot in preferred_slots:
                if self._is_slot_free(slot, teacher_id, group_id, teacher_slots, group_slots):
                    return slot
        
        # Случайный свободный слот
        random.shuffle(self.available_slots)
        for slot in self.available_slots:
            if self._is_slot_free(slot, teacher_id, group_id, teacher_slots, group_slots):
                return slot
        
        return None
    
    def _is_slot_free(
        self,
        slot: tuple,
        teacher_id: int,
        group_id: int,
        teacher_slots: Dict,
        group_slots: Dict
    ) -> bool:
        """Проверить свободен ли слот"""
        # Проверить преподавателя
        if slot in teacher_slots.get(teacher_id, []):
            return False
        
        # Проверить группу
        if slot in group_slots.get(group_id, []):
            return False
        
        return True

