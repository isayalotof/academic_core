"""
Simple Schedule Generator
Простой генератор расписания на основе нагрузок и аудиторий

Требования:
- Пары с понедельника по субботу (1-6)
- В один временной слот только одна пара
- Пары идут без окон (подряд в один день)
- Используется lessons_per_week из нагрузки
"""

import random
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SimpleScheduleGenerator:
    """Простой генератор расписания с соблюдением всех требований"""
    
    DAYS_PER_WEEK = 6  # Понедельник - Суббота (1-6)
    SLOTS_PER_DAY = 6  # 6 пар в день (1-6)
    
    def __init__(self, course_loads: List[Dict], classrooms: List[Dict]):
        """
        Args:
            course_loads: Список нагрузок (с преподавателями и группами)
            classrooms: Список аудиторий
        """
        self.course_loads = course_loads
        self.classrooms = classrooms
        
        # Отслеживание занятости слотов
        # Ключ: (day, time_slot), значение: информация о занятии
        self.occupied_slots: Dict[Tuple[int, int], Dict] = {}
        
        # Отслеживание занятости преподавателей, групп, аудиторий
        # Ключ: (day, time_slot), значение: set(ids)
        self.teacher_slots: Dict[Tuple[int, int], Set[int]] = {}
        self.group_slots: Dict[Tuple[int, int], Set[int]] = {}
        self.classroom_slots: Dict[Tuple[int, int], Set[int]] = {}
        
        # Для проверки непрерывности пар в день
        # Ключ: (day, entity_id, entity_type), значение: список занятых слотов
        # entity_type: 'teacher' или 'group'
        self.entity_day_slots: Dict[Tuple[int, int, str], List[int]] = {}
    
    def generate(self) -> List[Dict]:
        """
        Сгенерировать расписание
        
        Returns:
            Список занятий
        """
        schedule = []
        schedule_id = 1
        
        # Перемешать нагрузки для случайного порядка
        shuffled_loads = self.course_loads.copy()
        random.shuffle(shuffled_loads)
        
        logger.info(f"📚 Processing {len(shuffled_loads)} course loads")
        logger.info("🔒 Sunday (day 0 or 7) is STRICTLY FORBIDDEN! Only days 1-6 (Monday-Saturday) will be used.")
        
        for load in shuffled_loads:
            teacher_id = load.get('teacher_id')
            group_id = load.get('group_id')
            # Брать lessons_per_week из нагрузки - это основное поле для определения количества пар
            # Это поле автоматически вычисляется при создании нагрузки (hours_per_semester / 32)
            lessons_per_week = load.get('lessons_per_week', 1)
            
            # Пропустить если нет преподавателя или группы
            if not teacher_id or not group_id:
                logger.warning(f"Skipping load {load.get('id')}: missing teacher or group")
                continue
            
            # Валидация lessons_per_week - это критически важно для правильной генерации
            if not lessons_per_week or lessons_per_week <= 0:
                logger.warning(
                    f"Invalid lessons_per_week={lessons_per_week} for load {load.get('id')}, "
                    f"discipline={load.get('discipline_name')}. Using default 1."
                )
                lessons_per_week = 1
            
            # Максимум пар в неделю: 6 дней (понедельник-суббота) * 6 пар в день = 36 пар
            max_lessons_per_week = 6 * self.SLOTS_PER_DAY  # 6 дней (Пн-Сб) * 6 пар = 36
            if lessons_per_week > max_lessons_per_week:
                logger.warning(
                    f"lessons_per_week={lessons_per_week} too large for load {load.get('id')}, "
                    f"limiting to {max_lessons_per_week} (6 days * {self.SLOTS_PER_DAY} slots)"
                )
                lessons_per_week = max_lessons_per_week
            
            # Распределить пары по дням недели на основе lessons_per_week
            day_distribution = self._distribute_lessons_across_days(lessons_per_week)
            logger.info(
                f"📚 Processing load {load.get('id')} ({load.get('discipline_name')}): "
                f"lessons_per_week={lessons_per_week}, distribution={day_distribution}, "
                f"teacher_id={teacher_id}, group_id={group_id}"
            )
            
            # Разместить пары для каждой нагрузки - используем lessons_per_week из нагрузки
            # КРИТИЧНО: Отслеживаем все использованные слоты для этой нагрузки на ВСЕЙ неделе!
            used_slots_for_load = set()  # {(day, time_slot)} - все использованные слоты для этой нагрузки
            lessons_placed = 0
            
            for day, count_in_day in day_distribution.items():
                if count_in_day == 0:
                    continue
                
                # КРИТИЧЕСКАЯ ПРОВЕРКА: Только дни 1-6 (понедельник-суббота), ВОСКРЕСЕНЬЕ ЗАПРЕЩЕНО!
                # Жесткая проверка - воскресенье (0 или 7) НИКОГДА не допускается!
                valid_days = {1, 2, 3, 4, 5, 6}  # Только рабочие дни
                if day not in valid_days:
                    logger.error(
                        f"CRITICAL ERROR: Invalid day_of_week={day} for load {load.get('id')}, "
                        f"discipline={load.get('discipline_name')}. "
                        f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN! Skipping."
                    )
                    continue
                
                # Найти непрерывный блок слотов для размещения count_in_day пар подряд
                # НО учитывать уже использованные слоты для этой нагрузки!
                slot_block = self._find_continuous_slot_block_for_load(
                    day, count_in_day, teacher_id, group_id, used_slots_for_load
                )
                
                if not slot_block:
                    logger.warning(
                        f"Could not find continuous slot block for day {day}, "
                        f"teacher {teacher_id}, group {group_id}, count {count_in_day}"
                    )
                    # Попробовать разместить по отдельности - но ВАЖНО: каждая пара в РАЗНЫЙ слот!
                    for _ in range(count_in_day):
                        slot = self._find_any_free_slot_for_load_global(
                            day, teacher_id, group_id, used_slots_for_load
                        )
                        if slot:
                            slot_key = (day, slot)
                            
                            # КРИТИЧЕСКАЯ ПРОВЕРКА 1: Слот не должен быть уже использован для этой нагрузки
                            if slot_key in used_slots_for_load:
                                logger.warning(
                                    f"Slot {slot_key} already used for this load, skipping. "
                                    f"Load: {load.get('discipline_name')}"
                                )
                                continue
                            
                            # КРИТИЧЕСКАЯ ПРОВЕРКА 2: Слот должен быть свободен (проверка конфликтов)
                            if self._has_conflict(slot_key, teacher_id, group_id):
                                logger.warning(
                                    f"Slot {slot_key} has conflict after finding, skipping. "
                                    f"Load: {load.get('discipline_name')}"
                                )
                                continue
                            
                            # КРИТИЧЕСКАЯ ПРОВЕРКА 3: Убедиться, что слот не занят в occupied_slots
                            if slot_key in self.occupied_slots:
                                logger.error(
                                    f"CRITICAL ERROR: Slot {slot_key} already in occupied_slots when trying to place individually! "
                                    f"Existing: {self.occupied_slots[slot_key].get('discipline_name')}. "
                                    f"Trying to place: {load.get('discipline_name')}. Skipping."
                                )
                                continue
                            
                            # Проверить конфликты еще раз перед созданием урока
                            if self._has_conflict(slot_key, teacher_id, group_id):
                                logger.warning(
                                    f"Slot {slot_key} has conflict before creating lesson. "
                                    f"Load: {load.get('discipline_name')}. Skipping this slot."
                                )
                                continue
                            
                            # Создать урок БЕЗ предварительного помещения в used_slots_for_load
                            # (чтобы избежать проблем, если урок не создастся)
                            lesson = self._create_lesson(
                                schedule_id, load, day, slot, teacher_id, group_id
                            )
                            if lesson:
                                # ТОЛЬКО ПОСЛЕ успешного создания урока:
                                # 1. Пометить слот как использованный для этой нагрузки
                                used_slots_for_load.add(slot_key)
                                # 2. Пометить слот как занятый глобально
                                self._mark_slot_occupied(day, slot, lesson)
                                # 3. Добавить урок в расписание
                                schedule.append(lesson)
                                schedule_id += 1
                                lessons_placed += 1
                            else:
                                # Если урок не создан, слот уже не помечен, так что просто пропускаем
                                logger.warning(
                                    f"Failed to create lesson for slot {slot_key}. "
                                    f"Load: {load.get('discipline_name')}. Skipping this slot."
                                )
                        else:
                            logger.warning(
                                f"Could not find free slot for day {day}, "
                                f"teacher {teacher_id}, group {group_id}. "
                                f"Load: {load.get('discipline_name')}"
                            )
                    continue
                
                # Разместить пары в найденном блоке
                # КРИТИЧНО: Проверить ВСЕ слоты в блоке ПЕРЕД размещением, чтобы избежать частичного размещения
                slots_to_place = []
                for time_slot in slot_block:
                    slot_key = (day, time_slot)
                    
                    # КРИТИЧЕСКАЯ ПРОВЕРКА 1: Слот не должен быть уже использован для этой нагрузки
                    if slot_key in used_slots_for_load:
                        logger.warning(
                            f"Slot {slot_key} already used for this load in block, cannot place all pairs. "
                            f"Load: {load.get('discipline_name')}. Breaking block placement."
                        )
                        slots_to_place = []  # Сбросить весь блок, если один слот уже занят
                        break
                    
                    # КРИТИЧЕСКАЯ ПРОВЕРКА 2: Слот должен быть свободен (проверка конфликтов)
                    if self._has_conflict(slot_key, teacher_id, group_id):
                        logger.warning(
                            f"Slot {slot_key} has conflict in block, cannot place all pairs. "
                            f"Load: {load.get('discipline_name')}. Breaking block placement."
                        )
                        slots_to_place = []  # Сбросить весь блок, если есть конфликт
                        break
                    
                    # КРИТИЧЕСКАЯ ПРОВЕРКА 3: Убедиться, что слот не занят в occupied_slots
                    if slot_key in self.occupied_slots:
                        logger.error(
                            f"CRITICAL ERROR: Slot {slot_key} already in occupied_slots when trying to place in block! "
                            f"Existing: {self.occupied_slots[slot_key].get('discipline_name')}. "
                            f"Trying to place: {load.get('discipline_name')}. Breaking block placement."
                        )
                        slots_to_place = []  # Сбросить весь блок, если слот уже занят
                        break
                    
                    # Слот валиден - добавить в список для размещения
                    slots_to_place.append(time_slot)
                
                # Разместить пары только если ВСЕ слоты в блоке свободны
                if len(slots_to_place) != count_in_day:
                    logger.warning(
                        f"Cannot place {count_in_day} pairs in block for day {day} - not all slots are free. "
                        f"Found {len(slots_to_place)} free slots, need {count_in_day}. "
                        f"Load: {load.get('discipline_name')}. Trying individual placement."
                    )
                    # Попробовать разместить по отдельности - но ВАЖНО: каждая пара в РАЗНЫЙ слот!
                    for _ in range(count_in_day):
                        slot = self._find_any_free_slot_for_load_global(
                            day, teacher_id, group_id, used_slots_for_load
                        )
                        if slot:
                            slot_key = (day, slot)
                            
                            # КРИТИЧЕСКАЯ ПРОВЕРКА 1: Слот не должен быть уже использован для этой нагрузки
                            if slot_key in used_slots_for_load:
                                logger.warning(
                                    f"Slot {slot_key} already used for this load, skipping. "
                                    f"Load: {load.get('discipline_name')}"
                                )
                                continue
                            
                            # КРИТИЧЕСКАЯ ПРОВЕРКА 2: Слот должен быть свободен (проверка конфликтов)
                            if self._has_conflict(slot_key, teacher_id, group_id):
                                logger.warning(
                                    f"Slot {slot_key} has conflict after finding, skipping. "
                                    f"Load: {load.get('discipline_name')}"
                                )
                                continue
                            
                            # КРИТИЧЕСКАЯ ПРОВЕРКА 3: Убедиться, что слот не занят в occupied_slots
                            if slot_key in self.occupied_slots:
                                logger.error(
                                    f"CRITICAL ERROR: Slot {slot_key} already in occupied_slots when trying to place individually! "
                                    f"Existing: {self.occupied_slots[slot_key].get('discipline_name')}. "
                                    f"Trying to place: {load.get('discipline_name')}. Skipping."
                                )
                                continue
                            
                            # Проверить конфликты еще раз перед созданием урока
                            if self._has_conflict(slot_key, teacher_id, group_id):
                                logger.warning(
                                    f"Slot {slot_key} has conflict before creating lesson. "
                                    f"Load: {load.get('discipline_name')}. Skipping this slot."
                                )
                                continue
                            
                            # Создать урок БЕЗ предварительного помещения в used_slots_for_load
                            # (чтобы избежать проблем, если урок не создастся)
                            lesson = self._create_lesson(
                                schedule_id, load, day, slot, teacher_id, group_id
                            )
                            if lesson:
                                # ТОЛЬКО ПОСЛЕ успешного создания урока:
                                # 1. Пометить слот как использованный для этой нагрузки
                                used_slots_for_load.add(slot_key)
                                # 2. Пометить слот как занятый глобально
                                self._mark_slot_occupied(day, slot, lesson)
                                # 3. Добавить урок в расписание
                                schedule.append(lesson)
                                schedule_id += 1
                                lessons_placed += 1
                            else:
                                # Если урок не создан, слот уже не помечен, так что просто пропускаем
                                logger.warning(
                                    f"Failed to create lesson for slot {slot_key}. "
                                    f"Load: {load.get('discipline_name')}. Skipping this slot."
                                )
                        else:
                            logger.warning(
                                f"Could not find free slot for day {day}, "
                                f"teacher {teacher_id}, group {group_id}. "
                                f"Load: {load.get('discipline_name')}"
                            )
                    continue
                
                # Все слоты в блоке свободны - разместить пары
                for time_slot in slots_to_place:
                    slot_key = (day, time_slot)
                    
                    # КРИТИЧЕСКАЯ ФИНАЛЬНАЯ ПРОВЕРКА: Убедиться, что слот все еще свободен
                    # (на случай, если другой поток или итерация занял слот между проверкой и размещением)
                    if slot_key in used_slots_for_load:
                        logger.error(
                            f"CRITICAL ERROR: Slot {slot_key} already in used_slots_for_load! "
                            f"Load: {load.get('discipline_name')}. This should not happen! Skipping this slot."
                        )
                        continue
                    
                    if slot_key in self.occupied_slots:
                        logger.error(
                            f"CRITICAL ERROR: Slot {slot_key} already in occupied_slots! "
                            f"Existing: {self.occupied_slots[slot_key].get('discipline_name')}. "
                            f"Load: {load.get('discipline_name')}. Skipping this slot."
                        )
                        continue
                    
                    # Проверить конфликты еще раз перед созданием урока
                    if self._has_conflict(slot_key, teacher_id, group_id):
                        logger.warning(
                            f"Slot {slot_key} has conflict before creating lesson. "
                            f"Load: {load.get('discipline_name')}. Skipping this slot."
                        )
                        continue
                    
                    # Создать урок БЕЗ предварительного помещения в used_slots_for_load
                    # (чтобы избежать проблем, если урок не создастся)
                    lesson = self._create_lesson(
                        schedule_id, load, day, time_slot, teacher_id, group_id
                    )
                    if lesson:
                        # ТОЛЬКО ПОСЛЕ успешного создания урока:
                        # 1. Пометить слот как использованный для этой нагрузки
                        used_slots_for_load.add(slot_key)
                        # 2. Пометить слот как занятый глобально
                        self._mark_slot_occupied(day, time_slot, lesson)
                        # 3. Добавить урок в расписание
                        schedule.append(lesson)
                        schedule_id += 1
                        lessons_placed += 1
                        logger.debug(
                            f"✓ Placed lesson {lessons_placed} for load {load.get('id')} "
                            f"({load.get('discipline_name')}) at day {day}, slot {time_slot}"
                        )
                    else:
                        # Если урок не создан, слот уже не помечен, так что просто пропускаем
                        logger.warning(
                            f"❌ Failed to create lesson for slot {slot_key}. "
                            f"Load: {load.get('discipline_name')}. Skipping this slot."
                        )
            
            logger.info(
                f"✅ Load {load.get('id')} ({load.get('discipline_name')}): "
                f"placed {lessons_placed}/{lessons_per_week} lessons. "
                f"Used slots: {sorted(used_slots_for_load)}"
            )
            
            if lessons_placed < lessons_per_week:
                logger.warning(
                    f"⚠️ Load {load.get('id')} ({load.get('discipline_name')}): "
                    f"Placed only {lessons_placed}/{lessons_per_week} lessons! "
                    f"This may indicate insufficient free slots or conflicts."
                )
        
        # ФИНАЛЬНАЯ ПРОВЕРКА: Убедиться, что в расписании нет воскресенья
        sunday_lessons = [l for l in schedule if l.get('day_of_week') == 0 or l.get('day_of_week') == 7]
        if sunday_lessons:
            logger.error(
                f"CRITICAL ERROR: Found {len(sunday_lessons)} lessons with Sunday (day 0 or 7) in generated schedule! "
                f"Removing them!"
            )
            schedule = [l for l in schedule if l.get('day_of_week') not in [0, 7]]
        
        # Дополнительная проверка: все дни должны быть 1-6
        invalid_lessons = [l for l in schedule if l.get('day_of_week', 0) < 1 or l.get('day_of_week', 0) > 6]
        if invalid_lessons:
            logger.error(
                f"CRITICAL ERROR: Found {len(invalid_lessons)} lessons with invalid day_of_week! "
                f"Removing them!"
            )
            schedule = [l for l in schedule if 1 <= l.get('day_of_week', 0) <= 6]
        
        logger.info(f"✅ Generated schedule with {len(schedule)} lessons (Sunday FORBIDDEN, only days 1-6)")
        return schedule
    
    def _distribute_lessons_across_days(self, lessons_per_week: int) -> Dict[int, int]:
        """
        Распределить пары по дням недели (ТОЛЬКО понедельник-суббота, дни 1-6)
        
        КРИТИЧНО: ВОСКРЕСЕНЬЕ НИКОГДА НЕ ИСПОЛЬЗУЕТСЯ! Только дни 1-6!
        
        Args:
            lessons_per_week: Количество пар в неделю
            
        Returns:
            Словарь {day: count}, где day - день недели (1=Пн, 2=Вт, 3=Ср, 4=Чт, 5=Пт, 6=Сб), 
            count - количество пар в этот день
            ВОСКРЕСЕНЬЕ (день 0 или 7) НИКОГДА НЕ ВОЗВРАЩАЕТСЯ!
        """
        # ЖЕСТКО: Только дни 1-6 (понедельник-суббота), ВОСКРЕСЕНЬЕ ИСКЛЮЧЕНО!
        # Дни недели: 1=Понедельник, 2=Вторник, 3=Среда, 4=Четверг, 5=Пятница, 6=Суббота
        # Воскресенье (0 или 7) НИКОГДА не используется!
        valid_days = [1, 2, 3, 4, 5, 6]  # Жестко задаем только рабочие дни
        
        distribution = {day: 0 for day in valid_days}  # Только дни 1-6
        
        # Простое распределение: равномерно по дням, остаток случайно
        base_count = lessons_per_week // 6  # 6 дней недели (понедельник-суббота)
        remainder = lessons_per_week % 6
        
        # Базовое количество в каждый день (1-6)
        for day in valid_days:
            distribution[day] = base_count
        
        # Распределить остаток случайно (только по дням 1-6)
        days_list = valid_days.copy()  # Копируем список валидных дней (1-6)
        random.shuffle(days_list)
        for i in range(remainder):
            distribution[days_list[i]] += 1
        
        # ЖЕСТКАЯ ФИЛЬТРАЦИЯ: Убрать дни с нулевым количеством и ВОСКРЕСЕНЬЕ
        filtered = {}
        for day, count in distribution.items():
            # КРИТИЧЕСКАЯ ПРОВЕРКА: Только дни 1-6, воскресенье (0 и 7) исключено
            if day in valid_days and count > 0:
                filtered[day] = count
            elif day not in valid_days:
                logger.error(f"CRITICAL ERROR: Invalid day={day} found in distribution! Skipping.")
        
        # Финальная проверка - убедиться, что нет воскресенья
        if 0 in filtered or 7 in filtered:
            logger.error(f"CRITICAL ERROR: Sunday (0 or 7) detected in final distribution! Removing.")
            filtered = {day: count for day, count in filtered.items() if day not in [0, 7]}
        
        return filtered
    
    def _find_continuous_slot_block(
        self, 
        day: int, 
        count: int, 
        teacher_id: int, 
        group_id: int
    ) -> Optional[List[int]]:
        """
        Найти непрерывный блок свободных слотов для размещения count пар подряд
        
        Args:
            day: День недели (1-6, только понедельник-суббота, без воскресенья!)
            count: Количество пар подряд
            teacher_id: ID преподавателя
            group_id: ID группы
            
        Returns:
            Список слотов [slot1, slot2, ...] или None, если не найдено
        """
        # ВАЛИДАЦИЯ: День недели должен быть только 1-6 (понедельник-суббота)
        # Воскресенье (день 0 или 7) НЕ допускается!
        if day == 0 or day == 7:
            logger.error(f"CRITICAL: Sunday detected (day={day})! Cannot find slot block. Sunday is not allowed.")
            return None
        if day < 1 or day > 6:
            logger.error(f"Invalid day_of_week={day}. Must be between 1 (Monday) and 6 (Saturday).")
            return None
        
        # Перебрать все возможные начальные позиции
        # Последний возможный старт: SLOTS_PER_DAY - count + 1
        # Например, для 6 слотов и count=3, последний старт = 4 (блок 4,5,6)
        max_start = self.SLOTS_PER_DAY - count + 1
        for start_slot in range(1, max_start + 1):
            # Проверить, можно ли разместить count пар начиная с start_slot
            end_slot = start_slot + count - 1
            
            # Проверить границы
            if end_slot > self.SLOTS_PER_DAY:
                continue
            
            # Проверить все слоты в блоке
            slots_to_check = list(range(start_slot, end_slot + 1))
            can_place = True
            
            for time_slot in slots_to_check:
                key = (day, time_slot)
                
                # Проверить конфликты
                if self._has_conflict(key, teacher_id, group_id):
                    can_place = False
                    break
            
            if can_place:
                return slots_to_check
        
        return None
    
    def _find_continuous_slot_block_for_load(
        self, 
        day: int, 
        count: int, 
        teacher_id: int, 
        group_id: int,
        used_slots: Set[Tuple[int, int]]
    ) -> Optional[List[int]]:
        """
        Найти непрерывный блок свободных слотов для размещения count пар подряд,
        исключая уже использованные слоты для этой нагрузки
        
        КРИТИЧНО: Для одной нагрузки нельзя размещать несколько пар в один слот!
        
        Args:
            day: День недели (1-6, только понедельник-суббота, без воскресенья!)
            count: Количество пар подряд
            teacher_id: ID преподавателя
            group_id: ID группы
            used_slots: Множество уже использованных слотов {(day, time_slot)} для этой нагрузки
            
        Returns:
            Список слотов [slot1, slot2, ...] или None, если не найдено
        """
        # ВАЛИДАЦИЯ: День недели должен быть только 1-6 (понедельник-суббота)
        # Воскресенье (день 0 или 7) НЕ допускается!
        if day == 0 or day == 7:
            logger.error(f"CRITICAL: Sunday detected (day={day})! Cannot find slot block. Sunday is not allowed.")
            return None
        if day < 1 or day > 6:
            logger.error(f"Invalid day_of_week={day}. Must be between 1 (Monday) and 6 (Saturday).")
            return None
        
        # Перебрать все возможные начальные позиции
        max_start = self.SLOTS_PER_DAY - count + 1
        for start_slot in range(1, max_start + 1):
            end_slot = start_slot + count - 1
            
            # Проверить границы
            if end_slot > self.SLOTS_PER_DAY:
                continue
            
            # Проверить все слоты в блоке
            slots_to_check = list(range(start_slot, end_slot + 1))
            can_place = True
            
            for time_slot in slots_to_check:
                key = (day, time_slot)
                
                # КРИТИЧЕСКАЯ ПРОВЕРКА 1: Слот не должен быть уже использован для этой нагрузки
                if key in used_slots:
                    can_place = False
                    break
                
                # КРИТИЧЕСКАЯ ПРОВЕРКА 2: Убедиться, что слот не занят в occupied_slots
                if key in self.occupied_slots:
                    can_place = False
                    break
                
                # ПРОВЕРКА 3: Проверить конфликты с другими нагрузками
                if self._has_conflict(key, teacher_id, group_id):
                    can_place = False
                    break
            
            if can_place:
                return slots_to_check
        
        return None
    
    def _find_any_free_slot(
        self, 
        day: int, 
        teacher_id: int, 
        group_id: int
    ) -> Optional[int]:
        """
        Найти любой свободный слот в указанный день
        
        Args:
            day: День недели (1-6, только понедельник-суббота, без воскресенья!)
            teacher_id: ID преподавателя
            group_id: ID группы
            
        Returns:
            Номер слота или None
        """
        # ВАЛИДАЦИЯ: День недели должен быть только 1-6 (понедельник-суббота)
        # Воскресенье (день 0 или 7) НЕ допускается!
        if day == 0 or day == 7:
            logger.error(f"CRITICAL: Sunday detected (day={day})! Cannot find slot block. Sunday is not allowed.")
            return None
        if day < 1 or day > 6:
            logger.error(f"Invalid day_of_week={day}. Must be between 1 (Monday) and 6 (Saturday).")
            return None
        
        # Перебрать все слоты в день
        for time_slot in range(1, self.SLOTS_PER_DAY + 1):
            key = (day, time_slot)
            if not self._has_conflict(key, teacher_id, group_id):
                return time_slot
        
        return None
    
    def _find_any_free_slot_for_load(
        self, 
        day: int, 
        teacher_id: int, 
        group_id: int,
        used_slots: Set[int]
    ) -> Optional[int]:
        """
        Найти любой свободный слот в указанный день, исключая уже использованные для этой нагрузки в этот день
        
        КРИТИЧНО: Для одной нагрузки нельзя размещать несколько пар в один слот!
        
        Args:
            day: День недели (1-6, только понедельник-суббота, без воскресенья!)
            teacher_id: ID преподавателя
            group_id: ID группы
            used_slots: Множество уже использованных слотов (time_slot) для этой нагрузки в этот день
            
        Returns:
            Номер слота или None
        """
        # ВАЛИДАЦИЯ: День недели должен быть только 1-6 (понедельник-суббота)
        # Воскресенье (день 0 или 7) НЕ допускается!
        if day == 0 or day == 7:
            logger.error(f"CRITICAL: Sunday detected (day={day})! Cannot find slot. Sunday is not allowed.")
            return None
        if day < 1 or day > 6:
            logger.error(f"Invalid day_of_week={day}. Must be between 1 (Monday) and 6 (Saturday).")
            return None
        
        # Перебрать все слоты в день, исключая уже использованные
        for time_slot in range(1, self.SLOTS_PER_DAY + 1):
            # КРИТИЧНО: Пропустить слот, если он уже используется для этой нагрузки
            if time_slot in used_slots:
                continue
            
            slot_key = (day, time_slot)
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: Убедиться, что слот не занят в occupied_slots
            if slot_key in self.occupied_slots:
                continue
            
            # Проверить конфликты
            if not self._has_conflict(slot_key, teacher_id, group_id):
                return time_slot
        
        return None
    
    def _find_any_free_slot_for_load_global(
        self, 
        day: int, 
        teacher_id: int, 
        group_id: int,
        used_slots: Set[Tuple[int, int]]
    ) -> Optional[int]:
        """
        Найти любой свободный слот в указанный день, исключая уже использованные слоты для этой нагрузки на всей неделе
        
        КРИТИЧНО: Для одной нагрузки нельзя размещать несколько пар в один слот на всей неделе!
        
        Args:
            day: День недели (1-6, только понедельник-суббота, без воскресенья!)
            teacher_id: ID преподавателя
            group_id: ID группы
            used_slots: Множество уже использованных слотов {(day, time_slot)} для этой нагрузки на всей неделе
            
        Returns:
            Номер слота или None
        """
        # ВАЛИДАЦИЯ: День недели должен быть только 1-6 (понедельник-суббота)
        # Воскресенье (день 0 или 7) НЕ допускается!
        if day == 0 or day == 7:
            logger.error(f"CRITICAL: Sunday detected (day={day})! Cannot find slot. Sunday is not allowed.")
            return None
        if day < 1 or day > 6:
            logger.error(f"Invalid day_of_week={day}. Must be between 1 (Monday) and 6 (Saturday).")
            return None
        
        # Перебрать все слоты в день, исключая уже использованные для этой нагрузки
        for time_slot in range(1, self.SLOTS_PER_DAY + 1):
            slot_key = (day, time_slot)
            
            # КРИТИЧНО: Пропустить слот, если он уже используется для этой нагрузки
            if slot_key in used_slots:
                continue
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: Убедиться, что слот не занят в occupied_slots
            if slot_key in self.occupied_slots:
                continue
            
            # Проверить конфликты с другими нагрузками
            if not self._has_conflict(slot_key, teacher_id, group_id):
                return time_slot
        
        return None
    
    def _has_conflict(
        self, 
        slot_key: Tuple[int, int], 
        teacher_id: int, 
        group_id: int
    ) -> bool:
        """
        Проверить конфликты в слоте
        
        КРИТИЧНО: В один слот может быть ТОЛЬКО ОДНА ПАРА!
        
        Args:
            slot_key: (day, time_slot)
            teacher_id: ID преподавателя
            group_id: ID группы
            
        Returns:
            True если есть конфликт
        """
        day, time_slot = slot_key
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА: Воскресенье (0 или 7) ЗАПРЕЩЕНО!
        valid_days = {1, 2, 3, 4, 5, 6}  # Только рабочие дни
        if day not in valid_days:
            logger.error(
                f"CRITICAL ERROR: Invalid day_of_week={day}! "
                f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN!"
            )
            return True
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА 1: В слоте уже есть занятие - КОНФЛИКТ!
        # Это самая важная проверка - в один слот может быть ТОЛЬКО ОДНА ПАРА!
        if slot_key in self.occupied_slots:
            existing_lesson = self.occupied_slots[slot_key]
            logger.warning(
                f"CONFLICT: Slot {slot_key} already occupied! "
                f"Existing: teacher={existing_lesson.get('teacher_id')}, "
                f"group={existing_lesson.get('group_id')}, "
                f"discipline={existing_lesson.get('discipline_name')}. "
                f"Trying to place: teacher={teacher_id}, group={group_id}."
            )
            return True
        
        # ПРОВЕРКА 2: Преподаватель уже занят в этот слот
        if slot_key in self.teacher_slots:
            if teacher_id in self.teacher_slots[slot_key]:
                logger.warning(
                    f"CONFLICT: Teacher {teacher_id} already busy at slot {slot_key}"
                )
                return True
        
        # ПРОВЕРКА 3: Группа уже занята в этот слот
        if slot_key in self.group_slots:
            if group_id in self.group_slots[slot_key]:
                logger.warning(
                    f"CONFLICT: Group {group_id} already busy at slot {slot_key}"
                )
                return True
        
        # ПРОВЕРКА 4: Аудитория (если будет назначена) - проверяется при выборе
        
        return False
    
    def _create_lesson(
        self,
        schedule_id: int,
        load: Dict,
        day: int,
        time_slot: int,
        teacher_id: int,
        group_id: int
    ) -> Optional[Dict]:
        """
        Создать занятие
        
        Args:
            schedule_id: ID занятия
            load: Данные нагрузки
            day: День недели (1-6, только понедельник-суббота, без воскресенья!)
            time_slot: Временной слот
            teacher_id: ID преподавателя
            group_id: ID группы
            
        Returns:
            Словарь с данными занятия или None
        """
        # КРИТИЧЕСКАЯ ВАЛИДАЦИЯ: День недели должен быть только 1-6 (понедельник-суббота)
        # Воскресенье (день 0 или 7) НЕ допускается!
        if day == 0 or day == 7:
            logger.error(
                f"CRITICAL ERROR: Sunday detected (day={day}) for lesson creation! "
                f"Sunday is not allowed! "
                f"Skipping lesson for load {load.get('id')}, discipline {load.get('discipline_name')}."
            )
            return None
        if day < 1 or day > 6:
            logger.error(
                f"CRITICAL ERROR: Invalid day_of_week={day} for lesson creation! "
                f"Day must be between 1 (Monday) and 6 (Saturday). "
                f"Skipping lesson for load {load.get('id')}, discipline {load.get('discipline_name')}."
            )
            return None
        
        slot_key = (day, time_slot)
        
        # Проверить еще раз конфликты
        if self._has_conflict(slot_key, teacher_id, group_id):
            return None
        
        # Выбрать аудиторию
        classroom = self._select_classroom(load, day, time_slot)
        
        # Создать занятие
        lesson = {
            'id': schedule_id,
            'course_load_id': load.get('id'),
            'day_of_week': day,
            'time_slot': time_slot,
            'classroom_id': classroom.get('id') if classroom else None,
            'classroom_name': classroom.get('name') if classroom else None,
            'teacher_id': teacher_id,
            'teacher_name': load.get('teacher_name', ''),
            'group_id': group_id,
            'group_name': load.get('group_name', ''),
            'discipline_name': load.get('discipline_name', ''),
            'lesson_type': load.get('lesson_type', 'Практика')
        }
        
        return lesson
    
    def _mark_slot_occupied(self, day: int, time_slot: int, lesson: Dict):
        """
        Пометить слот как занятый
        
        КРИТИЧНО: Этот метод гарантирует, что в слот помечается ТОЛЬКО ОДНА ПАРА!
        
        Args:
            day: День недели (1-6, только понедельник-суббота)
            time_slot: Временной слот
            lesson: Данные занятия
        """
        # КРИТИЧЕСКАЯ ПРОВЕРКА: Воскресенье (0 или 7) ЗАПРЕЩЕНО!
        valid_days = {1, 2, 3, 4, 5, 6}  # Только рабочие дни
        if day not in valid_days:
            logger.error(
                f"CRITICAL ERROR: Attempting to mark slot on invalid day={day}! "
                f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN! "
                f"Lesson: {lesson.get('discipline_name')}"
            )
            return  # НЕ помечаем слот, если день воскресенье!
        
        slot_key = (day, time_slot)
        teacher_id = lesson['teacher_id']
        group_id = lesson['group_id']
        classroom_id = lesson.get('classroom_id')
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА: В слот уже есть занятие - это ошибка!
        if slot_key in self.occupied_slots:
            existing = self.occupied_slots[slot_key]
            logger.error(
                f"CRITICAL ERROR: Slot {slot_key} already occupied when trying to mark! "
                f"Existing lesson: teacher={existing.get('teacher_id')}, group={existing.get('group_id')}, "
                f"discipline={existing.get('discipline_name')}. "
                f"New lesson: teacher={teacher_id}, group={group_id}, discipline={lesson.get('discipline_name')}. "
                f"This should not happen! Skipping mark."
            )
            return  # НЕ помечаем слот, если он уже занят!
        
        # ФИНАЛЬНАЯ ПРОВЕРКА: Убедиться, что день не воскресенье перед сохранением!
        if day not in valid_days:
            logger.error(
                f"CRITICAL ERROR: Final check failed - day={day} is not valid! "
                f"Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN! "
                f"Lesson: {lesson.get('discipline_name')}"
            )
            return  # НЕ помечаем слот, если день воскресенье!
        
        # Пометить слот как занятый - гарантируем, что только одна пара в слоте!
        self.occupied_slots[slot_key] = lesson
        
        # Добавить преподавателя
        if slot_key not in self.teacher_slots:
            self.teacher_slots[slot_key] = set()
        self.teacher_slots[slot_key].add(teacher_id)
        
        # Добавить группу
        if slot_key not in self.group_slots:
            self.group_slots[slot_key] = set()
        self.group_slots[slot_key].add(group_id)
        
        # Добавить аудиторию (если есть)
        if classroom_id:
            if slot_key not in self.classroom_slots:
                self.classroom_slots[slot_key] = set()
            self.classroom_slots[slot_key].add(classroom_id)
        
        # Обновить информацию о непрерывности для проверки окон
        teacher_key = (day, teacher_id, 'teacher')
        if teacher_key not in self.entity_day_slots:
            self.entity_day_slots[teacher_key] = []
        self.entity_day_slots[teacher_key].append(time_slot)
        
        group_key = (day, group_id, 'group')
        if group_key not in self.entity_day_slots:
            self.entity_day_slots[group_key] = []
        self.entity_day_slots[group_key].append(time_slot)
    
    def _select_classroom(
        self, 
        course_load: Dict, 
        day: int = None, 
        time_slot: int = None
    ) -> Optional[Dict]:
        """
        Выбрать подходящую аудиторию
        
        Args:
            course_load: Данные нагрузки
            day: День недели
            time_slot: Временной слот
            
        Returns:
            Словарь с данными аудитории или None
        """
        if not self.classrooms:
            return None
        
        group_size = course_load.get('group_size') or course_load.get('students_count', 0)
        lesson_type = course_load.get('lesson_type', 'Практика')
        
        # Фильтр подходящих аудиторий
        suitable = []
        
        for classroom in self.classrooms:
            capacity = classroom.get('capacity', 0)
            
            # Проверка вместимости
            if group_size and capacity < group_size:
                continue
            
            # Проверка занятости (если указан слот)
            if day and time_slot:
                slot_key = (day, time_slot)
                if slot_key in self.classroom_slots:
                    if classroom.get('id') in self.classroom_slots[slot_key]:
                        continue
            
            suitable.append(classroom)
        
        if not suitable:
            # Если нет подходящих, попробовать любую свободную
            for classroom in self.classrooms:
                if day and time_slot:
                    slot_key = (day, time_slot)
                    if slot_key in self.classroom_slots:
                        if classroom.get('id') in self.classroom_slots[slot_key]:
                            continue
                suitable.append(classroom)
        
        if not suitable:
            return None
        
        return random.choice(suitable)
