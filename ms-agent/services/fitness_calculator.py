"""
Fitness Calculator для генетического алгоритма
Расчёт fitness для Chromosome объектов

Основано на рекомендациях статьи "Искусственный интеллект для составления расписания в вузе"
"""
import logging
from typing import Dict, List, Optional
from utils.chromosome import Chromosome, Lesson

logger = logging.getLogger(__name__)


class FitnessCalculator:
    """
    Расчёт fitness для генетического алгоритма
    
    FITNESS = 10000 - ШТРАФЫ
    
    ========== ЖЁСТКИЕ ОГРАНИЧЕНИЯ (HARD CONSTRAINTS) ==========
    Нарушение = расписание неработоспособно!
    - Конфликт преподавателя: -10000
    - Конфликт группы: -10000
    - Конфликт аудитории: -10000
    - Несоответствие аудитории (вместимость): -10000
    - Несоответствие аудитории (тип/оборудование): -10000
    - Преподаватель недоступен: -10000
    - Более 4 пар в день у студента: -10000 (ЗАКОН!)
    - Более 4 пар в день у преподавателя: -10000 (ЗАКОН!)
    
    ========== МЯГКИЕ ОГРАНИЧЕНИЯ (SOFT CONSTRAINTS) ==========
    Нарушение = ухудшение качества, но расписание работоспособно
    
    НАРУШЕНИЯ ПРЕДПОЧТЕНИЙ ⭐ ГЛАВНАЯ ОПТИМИЗАЦИЯ:
    - Приоритет 1 (внешний совместитель): -500
    - Приоритет 2 (магистрант): -200
    - Приоритет 3 (внутренний совместитель): -100
    - Приоритет 4 (штатный): -30
    
    ДЛЯ СТУДЕНТОВ:
    - Окно в расписании: -10 (главный приоритет!)
    - Не компактное расписание (разбросанные пары): -5 за разрыв
    
    ДЛЯ ПРЕПОДАВАТЕЛЕЙ:
    - Неравномерная нагрузка (в один день много, в другой мало): -15
    - Закрепление за аудиторией (частая смена): -8 за смену
    
    ОБЩИЕ:
    - Первая пара (8:00): -5
    - Шестая пара (поздно): -5
    - Низкая утилизация аудиторий: -3 за простаивающую аудиторию
    """
    
    BASE_FITNESS = 10000
    
    # ЖЁСТКИЕ ОГРАНИЧЕНИЯ
    PENALTY_TEACHER_CONFLICT = -10000
    PENALTY_GROUP_CONFLICT = -10000
    PENALTY_CLASSROOM_CONFLICT = -10000
    PENALTY_CAPACITY_MISMATCH = -10000  # Аудитория меньше группы
    PENALTY_TYPE_MISMATCH = -10000      # Несоответствие типа аудитории
    PENALTY_TEACHER_UNAVAILABLE = -10000  # Преподаватель недоступен
    PENALTY_MAX_LESSONS_STUDENT = -10000  # Более 4 пар в день у студента (ЗАКОН!)
    PENALTY_MAX_LESSONS_TEACHER = -10000  # Более 4 пар в день у преподавателя (ЗАКОН!)
    
    # НАРУШЕНИЯ ПРЕДПОЧТЕНИЙ
    PENALTY_PREFERENCE = {
        1: -500,   # Внешний совместитель - МАКСИМАЛЬНЫЙ приоритет!
        2: -200,   # Магистрант
        3: -100,   # Внутренний совместитель
        4: -30     # Штатный
    }
    
    # МЯГКИЕ ОГРАНИЧЕНИЯ ДЛЯ СТУДЕНТОВ
    PENALTY_GAP = -10              # Окно в расписании (главный приоритет!)
    PENALTY_NON_COMPACT = -5      # Не компактное расписание
    
    # МЯГКИЕ ОГРАНИЧЕНИЯ ДЛЯ ПРЕПОДАВАТЕЛЕЙ
    PENALTY_UNEVEN_LOAD = -15     # Неравномерная нагрузка
    PENALTY_CLASSROOM_CHANGE = -8  # Смена аудитории
    
    # ОБЩИЕ МЯГКИЕ ОГРАНИЧЕНИЯ
    PENALTY_EARLY = -5            # Первая пара (8:00)
    PENALTY_LATE = -5             # Шестая пара (поздно)
    PENALTY_LOW_UTILIZATION = -3  # Низкая утилизация аудиторий
    
    MAX_LESSONS_PER_DAY = 4       # Максимум пар в день для студента и преподавателя
    
    def __init__(self, teacher_preferences: Dict, classrooms: Optional[List[Dict]] = None, groups: Optional[Dict] = None):
        """
        Args:
            teacher_preferences: {
                teacher_id: {
                    'priority': int,
                    'name': str,
                    'preferences': [{day, slot, is_preferred}],
                    'availability': Optional[Dict]  # Календарь доступности
                }
            }
            classrooms: [
                {
                    'id': int,
                    'name': str,
                    'capacity': int,
                    'classroom_type': str,
                    'equipment': Optional[List[str]],
                    'building': Optional[str]
                }
            ]
            groups: {
                group_id: {
                    'id': int,
                    'name': str,
                    'size': int,
                    'building': Optional[str]
                }
            }
        """
        self.teacher_preferences = teacher_preferences
        self.classrooms = {c['id']: c for c in (classrooms or [])}
        self.groups = groups or {}
    
    def calculate(self, chromosome: Chromosome) -> float:
        """Рассчитать fitness согласно рекомендациям статьи"""
        
        fitness = self.BASE_FITNESS
        
        # ========== 1. ЖЁСТКИЕ ОГРАНИЧЕНИЯ (HARD CONSTRAINTS) ==========
        # 1.1. Конфликты ресурсов во времени
        conflicts = self._check_conflicts(chromosome.lessons)
        chromosome.conflicts_count = conflicts['total']
        
        fitness += conflicts['teacher'] * self.PENALTY_TEACHER_CONFLICT
        fitness += conflicts['group'] * self.PENALTY_GROUP_CONFLICT
        fitness += conflicts['classroom'] * self.PENALTY_CLASSROOM_CONFLICT
        
        # 1.2. Соответствие аудитории требованиям
        capacity_violations = self._check_capacity_mismatch(chromosome.lessons)
        fitness += capacity_violations * self.PENALTY_CAPACITY_MISMATCH
        
        type_violations = self._check_classroom_type_mismatch(chromosome.lessons)
        fitness += type_violations * self.PENALTY_TYPE_MISMATCH
        
        # 1.3. Доступность преподавателя
        availability_violations = self._check_teacher_availability(chromosome.lessons)
        fitness += availability_violations * self.PENALTY_TEACHER_UNAVAILABLE
        
        # 1.4. Максимум 4 пары в день (ЗАКОН!)
        max_lessons_student_violations = self._check_max_lessons_per_day_hard(chromosome.lessons, is_student=True)
        fitness += max_lessons_student_violations * self.PENALTY_MAX_LESSONS_STUDENT
        
        max_lessons_teacher_violations = self._check_max_lessons_per_day_hard(chromosome.lessons, is_student=False)
        fitness += max_lessons_teacher_violations * self.PENALTY_MAX_LESSONS_TEACHER
        
        # Если есть жесткие нарушения - низкий fitness
        hard_violations = (
            conflicts['total'] + capacity_violations + 
            type_violations + availability_violations +
            max_lessons_student_violations + max_lessons_teacher_violations
        )
        if hard_violations > 0:
            chromosome.fitness = fitness
            chromosome.hard_violations = hard_violations
            return fitness
        
        # ========== 2. МЯГКИЕ ОГРАНИЧЕНИЯ (SOFT CONSTRAINTS) ==========
        # 2.1. НАРУШЕНИЯ ПРЕДПОЧТЕНИЙ ⭐ ГЛАВНАЯ ОПТИМИЗАЦИЯ
        pref_violations = self._calculate_preference_violations(chromosome.lessons)
        chromosome.preference_violations = pref_violations
        
        for priority, count in pref_violations.items():
            fitness += count * self.PENALTY_PREFERENCE[priority]
        
        # 2.2. ДЛЯ СТУДЕНТОВ
        gaps_penalty = self._calculate_gaps_penalty(chromosome.lessons)
        chromosome.gaps_count = gaps_penalty['count']
        fitness += gaps_penalty['penalty']
        
        compactness_penalty = self._calculate_compactness_penalty(chromosome.lessons)
        fitness += compactness_penalty
        
        # 2.3. ДЛЯ ПРЕПОДАВАТЕЛЕЙ
        uneven_load_penalty = self._calculate_uneven_load_penalty(chromosome.lessons)
        fitness += uneven_load_penalty
        
        classroom_change_penalty = self._calculate_classroom_change_penalty(chromosome.lessons)
        fitness += classroom_change_penalty
        
        # 2.4. ОБЩИЕ
        time_penalty = self._calculate_time_penalty(chromosome.lessons)
        chromosome.early_lessons = time_penalty['early']
        chromosome.late_lessons = time_penalty['late']
        fitness += time_penalty['penalty']
        
        utilization_penalty = self._calculate_utilization_penalty(chromosome.lessons)
        fitness += utilization_penalty
        
        chromosome.fitness = fitness
        return fitness
    
    def _check_conflicts(self, lessons: List[Lesson]) -> Dict:
        """Проверить конфликты"""
        conflicts = {
            'teacher': 0,
            'group': 0,
            'classroom': 0,
            'total': 0
        }
        
        teacher_slots = {}
        group_slots = {}
        classroom_slots = {}
        
        for lesson in lessons:
            key = (lesson.day, lesson.slot, lesson.week)
            
            # Преподаватели
            if lesson.teacher_id not in teacher_slots:
                teacher_slots[lesson.teacher_id] = {}
            
            if key in teacher_slots[lesson.teacher_id]:
                conflicts['teacher'] += 1
            else:
                teacher_slots[lesson.teacher_id][key] = True
            
            # Группы
            if lesson.group_id not in group_slots:
                group_slots[lesson.group_id] = {}
            
            if key in group_slots[lesson.group_id]:
                conflicts['group'] += 1
            else:
                group_slots[lesson.group_id][key] = True
            
            # Аудитории
            if lesson.classroom_id not in classroom_slots:
                classroom_slots[lesson.classroom_id] = {}
            
            if key in classroom_slots[lesson.classroom_id]:
                conflicts['classroom'] += 1
            else:
                classroom_slots[lesson.classroom_id][key] = True
        
        conflicts['total'] = (
            conflicts['teacher'] +
            conflicts['group'] +
            conflicts['classroom']
        )
        
        return conflicts
    
    def _calculate_preference_violations(self, 
                                        lessons: List[Lesson]) -> Dict[int, int]:
        """
        Рассчитать нарушения предпочтений по приоритетам ⭐
        
        Returns:
            {1: count, 2: count, 3: count, 4: count}
        """
        violations = {1: 0, 2: 0, 3: 0, 4: 0}
        
        for lesson in lessons:
            teacher_id = lesson.teacher_id
            
            if teacher_id not in self.teacher_preferences:
                continue
            
            teacher_info = self.teacher_preferences[teacher_id]
            priority = teacher_info.get('priority', 4)
            
            # Проверить предпочтение для этого слота
            preference = None
            for pref in teacher_info.get('preferences', []):
                if pref.get('day_of_week') == lesson.day and \
                   pref.get('time_slot') == lesson.slot:
                    preference = pref
                    break
            
            # Если есть предпочтение и оно negative
            if preference and not preference.get('is_preferred', True):
                violations[priority] += 1
        
        return violations
    
    def _calculate_gaps_penalty(self, lessons: List[Lesson]) -> Dict:
        """Штраф за окна"""
        penalty = 0
        gap_count = 0
        
        group_days = {}
        
        for lesson in lessons:
            key = (lesson.group_id, lesson.day, lesson.week)
            
            if key not in group_days:
                group_days[key] = []
            
            group_days[key].append(lesson.slot)
        
        for key, slots in group_days.items():
            slots_sorted = sorted(set(slots))
            
            for i in range(len(slots_sorted) - 1):
                gap = slots_sorted[i + 1] - slots_sorted[i] - 1
                if gap > 0:
                    gap_count += gap
                    penalty += gap * self.PENALTY_GAP
        
        return {'penalty': penalty, 'count': gap_count}
    
    def _calculate_time_penalty(self, lessons: List[Lesson]) -> Dict:
        """Штраф за неудобное время"""
        penalty = 0
        early = 0
        late = 0
        
        for lesson in lessons:
            if lesson.slot == 1:
                early += 1
                penalty += self.PENALTY_EARLY
            elif lesson.slot == 6:
                late += 1
                penalty += self.PENALTY_LATE
        
        return {'penalty': penalty, 'early': early, 'late': late}
    
    def _check_capacity_mismatch(self, lessons: List[Lesson]) -> int:
        """
        Проверить соответствие вместимости аудитории размеру группы
        
        ЖЁСТКОЕ ОГРАНИЧЕНИЕ: Аудитория должна быть >= размера группы
        """
        violations = 0
        
        for lesson in lessons:
            if lesson.classroom_id == 0:
                continue  # Виртуальная аудитория
            
            classroom = self.classrooms.get(lesson.classroom_id)
            if not classroom:
                continue
            
            group = self.groups.get(lesson.group_id)
            if not group or not group.get('size'):
                continue
            
            group_size = group['size']
            classroom_capacity = classroom.get('capacity', 0)
            
            if classroom_capacity < group_size:
                violations += 1
                logger.debug(
                    f"Capacity mismatch: Group {lesson.group_name} "
                    f"(size={group_size}) in classroom {classroom.get('name')} "
                    f"(capacity={classroom_capacity})"
                )
        
        return violations
    
    def _check_classroom_type_mismatch(self, lessons: List[Lesson]) -> int:
        """
        Проверить соответствие типа аудитории требованиям дисциплины
        
        ЖЁСТКОЕ ОГРАНИЧЕНИЕ: Тип аудитории должен соответствовать типу занятия
        """
        violations = 0
        
        # Маппинг типов занятий на типы аудиторий
        lesson_type_to_classroom_type = {
            'Лабораторная': ['LAB', 'Лаборатория', 'LABORATORY'],
            'Лекция': ['LECTURE', 'Лекционная', 'AUDITORIUM'],
            'Практика': ['PRACTICE', 'Практическая', 'SEMINAR'],
            'Семинар': ['SEMINAR', 'Семинарская', 'PRACTICE']
        }
        
        for lesson in lessons:
            if lesson.classroom_id == 0:
                continue
            
            classroom = self.classrooms.get(lesson.classroom_id)
            if not classroom:
                continue
            
            lesson_type = lesson.lesson_type or ''
            classroom_type = (classroom.get('classroom_type') or '').upper()
            
            # Проверить соответствие типа
            required_types = lesson_type_to_classroom_type.get(lesson_type, [])
            if required_types and not any(rt in classroom_type for rt in required_types):
                # Для лабораторных - строгое требование
                if lesson_type == 'Лабораторная':
                    violations += 1
                    logger.debug(
                        f"Type mismatch: {lesson_type} requires LAB, "
                        f"but got {classroom_type}"
                    )
        
        return violations
    
    def _check_teacher_availability(self, lessons: List[Lesson]) -> int:
        """
        Проверить доступность преподавателя в указанное время
        
        ЖЁСТКОЕ ОГРАНИЧЕНИЕ: Преподаватель должен быть доступен
        """
        violations = 0
        
        for lesson in lessons:
            teacher_id = lesson.teacher_id
            if teacher_id not in self.teacher_preferences:
                continue
            
            teacher_info = self.teacher_preferences[teacher_id]
            availability = teacher_info.get('availability')
            
            if not availability:
                continue  # Нет данных о доступности - пропускаем
            
            # Проверить доступность для дня и времени
            day = lesson.day
            slot = lesson.slot
            
            # Формат availability: {day: {slot: bool}}
            if isinstance(availability, dict):
                day_availability = availability.get(day, {})
                if isinstance(day_availability, dict):
                    is_available = day_availability.get(slot, True)
                    if not is_available:
                        violations += 1
                        logger.debug(
                            f"Teacher {teacher_id} unavailable "
                            f"on day {day}, slot {slot}"
                        )
        
        return violations
    
    def _check_max_lessons_per_day_hard(self, lessons: List[Lesson], is_student: bool = True) -> int:
        """
        Проверить максимальное количество пар в день (ЖЁСТКОЕ ОГРАНИЧЕНИЕ - ЗАКОН!)
        
        ЖЁСТКОЕ ОГРАНИЧЕНИЕ: Не более MAX_LESSONS_PER_DAY пар в день
        Нарушение делает расписание неработоспособным!
        
        Args:
            lessons: Список занятий
            is_student: True для студентов, False для преподавателей
        
        Returns:
            Количество нарушений
        """
        violations = 0
        
        if is_student:
            # Группировать по группе и дню
            group_days = {}
            for lesson in lessons:
                key = (lesson.group_id, lesson.day, lesson.week)
                if key not in group_days:
                    group_days[key] = []
                group_days[key].append(lesson.slot)
            
            for key, slots in group_days.items():
                unique_slots = len(set(slots))
                if unique_slots > self.MAX_LESSONS_PER_DAY:
                    violations += 1
                    logger.debug(
                        f"Hard violation: Group {key[0]} has {unique_slots} "
                        f"lessons on day {key[1]}, week {key[2]} "
                        f"(max allowed: {self.MAX_LESSONS_PER_DAY})"
                    )
        else:
            # Группировать по преподавателю и дню
            teacher_days = {}
            for lesson in lessons:
                key = (lesson.teacher_id, lesson.day, lesson.week)
                if key not in teacher_days:
                    teacher_days[key] = []
                teacher_days[key].append(lesson.slot)
            
            for key, slots in teacher_days.items():
                unique_slots = len(set(slots))
                if unique_slots > self.MAX_LESSONS_PER_DAY:
                    violations += 1
                    logger.debug(
                        f"Hard violation: Teacher {key[0]} has {unique_slots} "
                        f"lessons on day {key[1]}, week {key[2]} "
                        f"(max allowed: {self.MAX_LESSONS_PER_DAY})"
                    )
        
        return violations
    
    def _calculate_compactness_penalty(self, lessons: List[Lesson]) -> int:
        """
        Штраф за некомпактное расписание (разбросанные пары)
        
        МЯГКОЕ ОГРАНИЧЕНИЕ: Пары должны идти компактными блоками
        """
        penalty = 0
        
        # Группировать по группе и дню
        group_days = {}
        for lesson in lessons:
            key = (lesson.group_id, lesson.day, lesson.week)
            if key not in group_days:
                group_days[key] = []
            group_days[key].append(lesson.slot)
        
        for key, slots in group_days.items():
            slots_sorted = sorted(set(slots))
            
            # Если больше 1 пары, проверить компактность
            if len(slots_sorted) > 1:
                # Найти разрывы между парами
                for i in range(len(slots_sorted) - 1):
                    gap = slots_sorted[i + 1] - slots_sorted[i] - 1
                    if gap > 1:  # Разрыв больше 1 пары
                        penalty += gap * self.PENALTY_NON_COMPACT
        
        return penalty
    
    def _calculate_uneven_load_penalty(self, lessons: List[Lesson]) -> int:
        """
        Штраф за неравномерную нагрузку преподавателя
        
        МЯГКОЕ ОГРАНИЧЕНИЕ: Равномерное распределение часов по неделе
        """
        penalty = 0
        
        # Группировать по преподавателю и дню
        teacher_days = {}
        for lesson in lessons:
            key = (lesson.teacher_id, lesson.week)
            if key not in teacher_days:
                teacher_days[key] = {}
            
            day = lesson.day
            if day not in teacher_days[key]:
                teacher_days[key][day] = 0
            teacher_days[key][day] += 1
        
        # Для каждого преподавателя проверить равномерность
        for (teacher_id, week), days_load in teacher_days.items():
            if len(days_load) < 2:
                continue
            
            loads = list(days_load.values())
            max_load = max(loads)
            min_load = min(loads)
            
            # Если разница больше 2 пар - штраф
            if max_load - min_load > 2:
                penalty += (max_load - min_load - 2) * self.PENALTY_UNEVEN_LOAD
        
        return penalty
    
    def _calculate_classroom_change_penalty(self, lessons: List[Lesson]) -> int:
        """
        Штраф за частую смену аудитории у преподавателя
        
        МЯГКОЕ ОГРАНИЧЕНИЕ: Закрепление за аудиторией
        """
        penalty = 0
        
        # Группировать по преподавателю и дню
        teacher_day_classrooms = {}
        for lesson in lessons:
            key = (lesson.teacher_id, lesson.day, lesson.week)
            if key not in teacher_day_classrooms:
                teacher_day_classrooms[key] = set()
            teacher_day_classrooms[key].add(lesson.classroom_id)
        
        # Подсчитать смены аудиторий в один день
        for key, classrooms in teacher_day_classrooms.items():
            if len(classrooms) > 1:
                # Преподаватель меняет аудиторию в один день
                penalty += (len(classrooms) - 1) * self.PENALTY_CLASSROOM_CHANGE
        
        return penalty
    
    def _calculate_utilization_penalty(self, lessons: List[Lesson]) -> int:
        """
        Штраф за низкую утилизацию аудиторий
        
        МЯГКОЕ ОГРАНИЧЕНИЕ: Максимизация использования аудиторного фонда
        """
        penalty = 0
        
        # Подсчитать использование каждой аудитории
        classroom_usage = {}
        total_slots = 6 * 6 * 16  # 6 дней * 6 пар * 16 недель
        
        for lesson in lessons:
            if lesson.classroom_id == 0:
                continue
            
            if lesson.classroom_id not in classroom_usage:
                classroom_usage[lesson.classroom_id] = 0
            classroom_usage[lesson.classroom_id] += 1
        
        # Проверить простаивающие аудитории
        for classroom_id, classroom in self.classrooms.items():
            usage_count = classroom_usage.get(classroom_id, 0)
            utilization = usage_count / total_slots if total_slots > 0 else 0
            
            # Если утилизация меньше 10% - штраф
            if utilization < 0.1 and classroom_id in classroom_usage:
                penalty += self.PENALTY_LOW_UTILIZATION
        
        return penalty

