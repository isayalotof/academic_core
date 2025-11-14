"""
Fitness Calculator
Оценка качества расписания с учётом приоритетов преподавателей
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Приоритеты преподавателей (KEY FEATURE!)
TEACHER_PRIORITIES = {
    1: {'name': 'Внешний совместитель', 'penalty': -500},
    2: {'name': 'Магистрант-преподаватель', 'penalty': -200},
    3: {'name': 'Внутренний совместитель', 'penalty': -100},
    4: {'name': 'Штатный', 'penalty': -30}
}

# Штрафы за окна
GAP_PENALTIES = {
    1: -20,   # 1 окно
    2: -100,  # 2 окна подряд
    3: -300   # 3+ окна
}


class FitnessCalculator:
    """Вычисление fitness-функции расписания"""
    
    def __init__(self):
        pass
    
    def calculate(
        self,
        schedule: List[Dict],
        teacher_preferences: Dict[int, List[Dict]]
    ) -> Dict[str, Any]:
        """
        Вычислить общий скор расписания
        
        Args:
            schedule: Список занятий
            teacher_preferences: {teacher_id: [{day, time, is_preferred}, ...]}
        
        Returns:
            {
                'total_score': int,
                'hard_constraints': int,
                'preference_violations': int,
                'isolated_lessons': int,
                'gaps': int,
                'details': {...}
            }
        """
        score = 0
        details = {}
        
        # 1. Hard Constraints (конфликты) - КРИТИЧНО!
        conflicts = self._find_conflicts(schedule)
        hard_score = len(conflicts) * -10000
        score += hard_score
        details['conflicts'] = conflicts
        details['hard_constraints_score'] = hard_score
        
        # 1.1. Максимум 4 пары в день (ЖЁСТКОЕ ОГРАНИЧЕНИЕ - ЗАКОН!)
        max_lessons_violations = self._check_max_lessons_per_day(schedule)
        max_lessons_score = max_lessons_violations * -10000
        score += max_lessons_score
        details['max_lessons_violations'] = max_lessons_violations
        details['max_lessons_score'] = max_lessons_score
        
        # 2. Soft Constraint #1: Предпочтения преподавателей (⭐ KEY FEATURE)
        pref_violations, pref_score = self._check_preferences(
            schedule, teacher_preferences
        )
        score += pref_score
        details['preference_violations'] = pref_violations
        details['preferences_score'] = pref_score
        
        # 3. Soft Constraint #2: Размазанность (isolated lessons)
        isolated = self._find_isolated_lessons(schedule)
        isolated_score = len(isolated) * -300
        score += isolated_score
        details['isolated_lessons'] = isolated
        details['isolated_score'] = isolated_score
        
        # 4. Soft Constraint #3: Окна
        gaps = self._find_gaps(schedule)
        gaps_score = self._calculate_gap_penalty(gaps)
        score += gaps_score
        details['gaps'] = gaps
        details['gaps_score'] = gaps_score
        
        # 5. Soft Constraint #4: Равномерное распределение по дням недели
        day_distribution_penalty = self._calculate_day_distribution_penalty(schedule)
        score += day_distribution_penalty
        details['day_distribution_penalty'] = day_distribution_penalty
        
        return {
            'total_score': score,
            'hard_constraints': hard_score,
            'preference_violations': pref_score,
            'isolated_lessons': isolated_score,
            'gaps': gaps_score,
            'day_distribution': day_distribution_penalty,
            'details': details
        }
    
    def _find_conflicts(self, schedule: List[Dict]) -> List[Dict]:
        """Найти все конфликты (hard constraints)"""
        conflicts = []
        
        # Индексация по времени
        teacher_slots = {}
        group_slots = {}
        classroom_slots = {}
        
        for lesson in schedule:
            key = (lesson['day_of_week'], lesson['time_slot'])
            
            # Конфликты преподавателей
            teacher_id = lesson['teacher_id']
            if teacher_id in teacher_slots.get(key, set()):
                conflicts.append({
                    'type': 'teacher',
                    'teacher_id': teacher_id,
                    'teacher_name': lesson['teacher_name'],
                    'day': lesson['day_of_week'],
                    'time': lesson['time_slot']
                })
            teacher_slots.setdefault(key, set()).add(teacher_id)
            
            # Конфликты групп
            group_id = lesson['group_id']
            if group_id in group_slots.get(key, set()):
                conflicts.append({
                    'type': 'group',
                    'group_id': group_id,
                    'group_name': lesson['group_name'],
                    'day': lesson['day_of_week'],
                    'time': lesson['time_slot']
                })
            group_slots.setdefault(key, set()).add(group_id)
            
            # Конфликты аудиторий
            if lesson.get('classroom_id'):
                classroom_id = lesson['classroom_id']
                if classroom_id in classroom_slots.get(key, set()):
                    conflicts.append({
                        'type': 'classroom',
                        'classroom_id': classroom_id,
                        'classroom_name': lesson.get('classroom_name', ''),
                        'day': lesson['day_of_week'],
                        'time': lesson['time_slot']
                    })
                classroom_slots.setdefault(key, set()).add(classroom_id)
        
        return conflicts
    
    def _check_preferences(
        self,
        schedule: List[Dict],
        preferences: Dict[int, List[Dict]]
    ) -> Tuple[List[Dict], int]:
        """
        Проверить нарушения предпочтений преподавателей
        
        Returns:
            (список_нарушений, общий_штраф)
        """
        violations = []
        total_penalty = 0
        
        for lesson in schedule:
            teacher_id = lesson['teacher_id']
            teacher_prefs = preferences.get(teacher_id, [])
            
            # Проверить, есть ли предпочтение для этого слота
            slot_key = (lesson['day_of_week'], lesson['time_slot'])
            is_preferred = any(
                p['day_of_week'] == slot_key[0] and 
                p['time_slot'] == slot_key[1] and 
                p['is_preferred']
                for p in teacher_prefs
            )
            
            # Если НЕ предпочтительно, штраф по приоритету
            if not is_preferred:
                priority = lesson.get('teacher_priority', 4)
                penalty = TEACHER_PRIORITIES[priority]['penalty']
                total_penalty += penalty
                
                violations.append({
                    'teacher_id': teacher_id,
                    'teacher_name': lesson['teacher_name'],
                    'priority': priority,
                    'priority_name': TEACHER_PRIORITIES[priority]['name'],
                    'day': lesson['day_of_week'],
                    'time': lesson['time_slot'],
                    'penalty': penalty,
                    'lesson_id': lesson.get('id')
                })
        
        return violations, total_penalty
    
    def _find_isolated_lessons(self, schedule: List[Dict]) -> List[Dict]:
        """
        Найти размазанные занятия (одиночные пары в день)
        
        Для каждого преподавателя: пара считается изолированной,
        если это единственная пара в день
        """
        isolated = []
        
        # Группировка по преподавателю и дню
        teacher_days = {}
        for lesson in schedule:
            teacher_id = lesson['teacher_id']
            day = lesson['day_of_week']
            key = (teacher_id, day)
            
            teacher_days.setdefault(key, []).append(lesson)
        
        # Найти дни с одной парой
        for (teacher_id, day), lessons in teacher_days.items():
            if len(lessons) == 1:
                isolated.append({
                    'teacher_id': teacher_id,
                    'teacher_name': lessons[0]['teacher_name'],
                    'day': day,
                    'lesson_id': lessons[0].get('id'),
                    'discipline': lessons[0]['discipline_name']
                })
        
        return isolated
    
    def _find_gaps(self, schedule: List[Dict]) -> Dict:
        """
        Найти окна в расписании
        
        Окно = пустой слот между парами в один день
        """
        gaps = {
            'teacher_gaps': [],
            'group_gaps': []
        }
        
        # По преподавателям
        teacher_schedule = self._group_by_teacher_day(schedule)
        for (teacher_id, day), lessons in teacher_schedule.items():
            time_slots = sorted([l['time_slot'] for l in lessons])
            
            for i in range(len(time_slots) - 1):
                gap_size = time_slots[i+1] - time_slots[i] - 1
                if gap_size > 0:
                    gaps['teacher_gaps'].append({
                        'teacher_id': teacher_id,
                        'teacher_name': lessons[0]['teacher_name'],
                        'day': day,
                        'gap_size': gap_size,
                        'between': (time_slots[i], time_slots[i+1])
                    })
        
        # По группам
        group_schedule = self._group_by_group_day(schedule)
        for (group_id, day), lessons in group_schedule.items():
            time_slots = sorted([l['time_slot'] for l in lessons])
            
            for i in range(len(time_slots) - 1):
                gap_size = time_slots[i+1] - time_slots[i] - 1
                if gap_size > 0:
                    gaps['group_gaps'].append({
                        'group_id': group_id,
                        'group_name': lessons[0]['group_name'],
                        'day': day,
                        'gap_size': gap_size,
                        'between': (time_slots[i], time_slots[i+1])
                    })
        
        return gaps
    
    def _calculate_gap_penalty(self, gaps: Dict) -> int:
        """Вычислить штраф за окна"""
        total_penalty = 0
        
        for gap in gaps['teacher_gaps']:
            size = min(gap['gap_size'], 3)
            penalty = GAP_PENALTIES.get(size, GAP_PENALTIES[3])
            total_penalty += penalty
        
        for gap in gaps['group_gaps']:
            size = min(gap['gap_size'], 3)
            penalty = GAP_PENALTIES.get(size, GAP_PENALTIES[3])
            total_penalty += penalty
        
        return total_penalty
    
    def _group_by_teacher_day(self, schedule: List[Dict]) -> Dict:
        """Группировать расписание по преподавателю и дню"""
        result = {}
        for lesson in schedule:
            key = (lesson['teacher_id'], lesson['day_of_week'])
            result.setdefault(key, []).append(lesson)
        return result
    
    def _group_by_group_day(self, schedule: List[Dict]) -> Dict:
        """Группировать расписание по группе и дню"""
        result = {}
        for lesson in schedule:
            key = (lesson['group_id'], lesson['day_of_week'])
            result.setdefault(key, []).append(lesson)
        return result
    
    def _calculate_day_distribution_penalty(self, schedule: List[Dict]) -> int:
        """
        Вычислить штраф за неравномерное распределение пар по дням недели
        
        Штрафуется:
        - Сильная неравномерность распределения для групп (все пары в один день)
        - Сильная неравномерность распределения для преподавателей
        
        Returns:
            Общий штраф (отрицательное число)
        """
        total_penalty = 0
        
        # 1. Проверить распределение по группам
        group_schedule = self._group_by_group_day(schedule)
        group_distributions = {}
        
        for (group_id, day), lessons in group_schedule.items():
            if group_id not in group_distributions:
                group_distributions[group_id] = {}
            group_distributions[group_id][day] = len(lessons)
        
        # Для каждой группы проверить равномерность
        for group_id, day_counts in group_distributions.items():
            total_lessons = sum(day_counts.values())
            if total_lessons == 0:
                continue
            
            # Идеальное распределение: равномерно по всем дням
            ideal_per_day = total_lessons / 6.0  # 6 дней в неделе
            
            # Вычислить дисперсию (насколько неравномерно)
            variance = 0
            max_day = max(day_counts.values()) if day_counts else 0
            min_day = min(day_counts.values()) if day_counts else 0
            
            for day in range(1, 7):
                actual = day_counts.get(day, 0)
                variance += abs(actual - ideal_per_day)
            
            # Штраф за неравномерность
            # Если все пары в один день - большой штраф
            if max_day > 0 and min_day == 0 and len(day_counts) == 1:
                # Все пары в один день - очень плохо
                total_penalty += -50 * total_lessons
            elif variance > ideal_per_day * 2:
                # Сильная неравномерность
                total_penalty += -20 * int(variance)
            elif variance > ideal_per_day:
                # Умеренная неравномерность
                total_penalty += -10 * int(variance)
        
        # 2. Проверить распределение по преподавателям
        teacher_schedule = self._group_by_teacher_day(schedule)
        teacher_distributions = {}
        
        for (teacher_id, day), lessons in teacher_schedule.items():
            if teacher_id not in teacher_distributions:
                teacher_distributions[teacher_id] = {}
            teacher_distributions[teacher_id][day] = len(lessons)
        
        # Для каждого преподавателя проверить равномерность
        for teacher_id, day_counts in teacher_distributions.items():
            total_lessons = sum(day_counts.values())
            if total_lessons == 0:
                continue
            
            ideal_per_day = total_lessons / 6.0
            
            variance = 0
            max_day = max(day_counts.values()) if day_counts else 0
            min_day = min(day_counts.values()) if day_counts else 0
            
            for day in range(1, 7):
                actual = day_counts.get(day, 0)
                variance += abs(actual - ideal_per_day)
            
            # Штраф за неравномерность (меньше чем для групп, т.к. для преподавателей это менее критично)
            if max_day > 0 and min_day == 0 and len(day_counts) == 1:
                # Все пары в один день
                total_penalty += -30 * total_lessons
            elif variance > ideal_per_day * 2:
                total_penalty += -15 * int(variance)
            elif variance > ideal_per_day:
                total_penalty += -5 * int(variance)
        
        return total_penalty
    
    def _check_max_lessons_per_day(self, schedule: List[Dict]) -> int:
        """
        Проверить максимальное количество пар в день (ЖЁСТКОЕ ОГРАНИЧЕНИЕ - ЗАКОН!)
        
        ЖЁСТКОЕ ОГРАНИЧЕНИЕ: Не более 4 пар в день для студентов и преподавателей
        Нарушение делает расписание неработоспособным!
        
        Returns:
            Количество нарушений
        """
        MAX_LESSONS_PER_DAY = 4
        violations = 0
        
        # 1. Проверить для групп (студентов)
        group_day_lessons = {}  # {(group_id, day): [time_slots]}
        for lesson in schedule:
            group_id = lesson.get('group_id')
            day = lesson.get('day_of_week')
            time_slot = lesson.get('time_slot')
            
            if not group_id or not day or not time_slot:
                continue
            
            key = (group_id, day)
            if key not in group_day_lessons:
                group_day_lessons[key] = []
            group_day_lessons[key].append(time_slot)
        
        # Проверить превышение максимума для групп
        for (group_id, day), time_slots in group_day_lessons.items():
            unique_slots = len(set(time_slots))
            if unique_slots > MAX_LESSONS_PER_DAY:
                violations += 1
                logger.warning(
                    f"Hard violation: Group {group_id} has {unique_slots} "
                    f"lessons on day {day} (max allowed: {MAX_LESSONS_PER_DAY})"
                )
        
        # 2. Проверить для преподавателей
        teacher_day_lessons = {}  # {(teacher_id, day): [time_slots]}
        for lesson in schedule:
            teacher_id = lesson.get('teacher_id')
            day = lesson.get('day_of_week')
            time_slot = lesson.get('time_slot')
            
            if not teacher_id or not day or not time_slot:
                continue
            
            key = (teacher_id, day)
            if key not in teacher_day_lessons:
                teacher_day_lessons[key] = []
            teacher_day_lessons[key].append(time_slot)
        
        # Проверить превышение максимума для преподавателей
        for (teacher_id, day), time_slots in teacher_day_lessons.items():
            unique_slots = len(set(time_slots))
            if unique_slots > MAX_LESSONS_PER_DAY:
                violations += 1
                logger.warning(
                    f"Hard violation: Teacher {teacher_id} has {unique_slots} "
                    f"lessons on day {day} (max allowed: {MAX_LESSONS_PER_DAY})"
                )
        
        return violations
    
    def calculate_improvement(
        self,
        old_score: int,
        new_score: int
    ) -> Dict[str, Any]:
        """
        Вычислить улучшение между двумя скорами
        
        Returns:
            {
                'improved': bool,
                'delta': int,
                'percent': float
            }
        """
        delta = new_score - old_score
        
        # Процент улучшения
        if old_score < 0:
            percent = (abs(delta) / abs(old_score)) * 100
        else:
            percent = 0
        
        return {
            'improved': delta > 0,
            'delta': delta,
            'percent': round(percent, 2)
        }


# Singleton instance
fitness_calculator = FitnessCalculator()

