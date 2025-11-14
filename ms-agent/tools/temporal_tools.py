"""
Temporal Tools для Stage 1
Инструменты для оптимизации временных слотов (без аудиторий)
"""

from typing import List, Dict, Any, Optional
import logging
import copy

from tools.base import Tool
from services.fitness import fitness_calculator

logger = logging.getLogger(__name__)


class AnalyzeScheduleTool(Tool):
    """Анализ текущего расписания"""
    
    def __init__(self, schedule_state, teacher_preferences):
        super().__init__(
            name="analyze_schedule",
            description="Проанализировать текущее расписание и получить детальные метрики: конфликты, нарушения предпочтений, размазанность, окна. Используй в начале каждой итерации."
        )
        self.schedule_state = schedule_state
        self.teacher_preferences = teacher_preferences
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить анализ"""
        result = fitness_calculator.calculate(
            self.schedule_state.current_schedule,
            self.teacher_preferences
        )
        
        return {
            "success": True,
            "total_score": result['total_score'],
            "conflicts": len(result['details']['conflicts']),
            "preference_violations": len(result['details']['preference_violations']),
            "isolated_lessons": len(result['details']['isolated_lessons']),
            "total_gaps": (
                len(result['details']['gaps']['teacher_gaps']) +
                len(result['details']['gaps']['group_gaps'])
            ),
            "breakdown": {
                "hard_constraints": result['hard_constraints'],
                "preferences": result['preference_violations'],
                "isolated": result['isolated_lessons'],
                "gaps": result['gaps']
            }
        }


class FindPreferenceViolationsTool(Tool):
    """Найти нарушения предпочтений преподавателей"""
    
    def __init__(self, schedule_state, teacher_preferences):
        super().__init__(
            name="find_preference_violations",
            description="Найти все нарушения предпочтений преподавателей. Сортировка по приоритету (Priority 1-2 - важнее всего!)."
        )
        self.schedule_state = schedule_state
        self.teacher_preferences = teacher_preferences
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "priority": {
                        "type": "integer",
                        "description": "Фильтр по приоритету (1-4). Если не указан - все нарушения"
                    }
                },
                "required": []
            }
        }
    
    def execute(self, priority: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Найти нарушения"""
        result = fitness_calculator.calculate(
            self.schedule_state.current_schedule,
            self.teacher_preferences
        )
        
        violations = result['details']['preference_violations']
        
        # Фильтровать по приоритету если указан
        if priority:
            violations = [v for v in violations if v['priority'] == priority]
        
        # Сортировать по приоритету (1 = самый важный)
        violations.sort(key=lambda v: v['priority'])
        
        return {
            "success": True,
            "total_violations": len(violations),
            "violations": violations[:20]  # Топ 20
        }


class SwapLessonsTool(Tool):
    """Поменять местами две пары"""
    
    def __init__(self, schedule_state, teacher_preferences):
        super().__init__(
            name="swap_lessons",
            description="Поменять местами две пары в расписании. КРИТИЧНО: Проверяет конфликты перед swap! Возвращает изменение скора."
        )
        self.schedule_state = schedule_state
        self.teacher_preferences = teacher_preferences
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "lesson1_id": {
                        "type": "integer",
                        "description": "ID первой пары"
                    },
                    "lesson2_id": {
                        "type": "integer",
                        "description": "ID второй пары"
                    }
                },
                "required": ["lesson1_id", "lesson2_id"]
            }
        }
    
    def execute(self, lesson1_id: int, lesson2_id: int, **kwargs) -> Dict[str, Any]:
        """Выполнить swap"""
        # Сохранить для rollback
        self.schedule_state.save_checkpoint()
        
        # Найти пары
        schedule = self.schedule_state.current_schedule
        lesson1 = next((l for l in schedule if l['id'] == lesson1_id), None)
        lesson2 = next((l for l in schedule if l['id'] == lesson2_id), None)
        
        if not lesson1 or not lesson2:
            return {
                "success": False,
                "error": f"Lessons not found: {lesson1_id}, {lesson2_id}"
            }
        
        # Скор ДО
        result_before = fitness_calculator.calculate(schedule, self.teacher_preferences)
        score_before = result_before['total_score']
        
        # Поменять временные слоты
        lesson1['day_of_week'], lesson2['day_of_week'] = lesson2['day_of_week'], lesson1['day_of_week']
        lesson1['time_slot'], lesson2['time_slot'] = lesson2['time_slot'], lesson1['time_slot']
        
        # Скор ПОСЛЕ
        result_after = fitness_calculator.calculate(schedule, self.teacher_preferences)
        score_after = result_after['total_score']
        delta = score_after - score_before
        
        # Проверить конфликты
        conflicts = result_after['details']['conflicts']
        if conflicts:
            # Откатить если создали конфликт
            self.schedule_state.rollback()
            return {
                "success": False,
                "error": f"Swap would create {len(conflicts)} conflicts",
                "conflicts": conflicts
            }
        
        logger.info(f"SWAP: {lesson1_id} ↔ {lesson2_id} | Score: {score_before} → {score_after} | Delta: {delta:+d}")
        
        return {
            "success": True,
            "score_before": score_before,
            "score_after": score_after,
            "score_delta": delta,
            "improved": delta > 0
        }


class MoveToEmptySlotTool(Tool):
    """Переместить пару в свободный слот"""
    
    def __init__(self, schedule_state, teacher_preferences):
        super().__init__(
            name="move_to_empty_slot",
            description="Переместить пару в свободный слот. Проверяет доступность слота и конфликты."
        )
        self.schedule_state = schedule_state
        self.teacher_preferences = teacher_preferences
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "lesson_id": {
                        "type": "integer",
                        "description": "ID пары для перемещения"
                    },
                    "day_of_week": {
                        "type": "integer",
                        "description": "Новый день (1-6)"
                    },
                    "time_slot": {
                        "type": "integer",
                        "description": "Новая пара (1-6)"
                    }
                },
                "required": ["lesson_id", "day_of_week", "time_slot"]
            }
        }
    
    def execute(self, lesson_id: int, day_of_week: int, time_slot: int, **kwargs) -> Dict[str, Any]:
        """Выполнить перемещение"""
        # КРИТИЧЕСКАЯ ПРОВЕРКА: Воскресенье (0 или 7) ЗАПРЕЩЕНО!
        if day_of_week == 0 or day_of_week == 7 or day_of_week < 1 or day_of_week > 6:
            return {
                "success": False,
                "error": f"Invalid day_of_week={day_of_week}. Only days 1-6 (Monday-Saturday) are allowed. Sunday (0 or 7) is FORBIDDEN!"
            }
        
        # Сохранить для rollback
        self.schedule_state.save_checkpoint()
        
        # Найти пару
        schedule = self.schedule_state.current_schedule
        lesson = next((l for l in schedule if l['id'] == lesson_id), None)
        
        if not lesson:
            return {
                "success": False,
                "error": f"Lesson not found: {lesson_id}"
            }
        
        # Скор ДО
        score_before = fitness_calculator.calculate(schedule, self.teacher_preferences)['total_score']
        
        # Переместить
        old_day, old_slot = lesson['day_of_week'], lesson['time_slot']
        lesson['day_of_week'] = day_of_week
        lesson['time_slot'] = time_slot
        
        # Скор ПОСЛЕ
        result_after = fitness_calculator.calculate(schedule, self.teacher_preferences)
        score_after = result_after['total_score']
        delta = score_after - score_before
        
        # Проверить конфликты
        conflicts = result_after['details']['conflicts']
        if conflicts:
            self.schedule_state.rollback()
            return {
                "success": False,
                "error": f"Move would create {len(conflicts)} conflicts",
                "conflicts": conflicts
            }
        
        logger.info(f"MOVE: Lesson {lesson_id} from ({old_day},{old_slot}) to ({day_of_week},{time_slot}) | Delta: {delta:+d}")
        
        return {
            "success": True,
            "score_before": score_before,
            "score_after": score_after,
            "score_delta": delta,
            "improved": delta > 0
        }


class RollbackTool(Tool):
    """Откатить последнее действие"""
    
    def __init__(self, schedule_state):
        super().__init__(
            name="rollback",
            description="Откатить последнее действие. Используй если действие ухудшило скор."
        )
        self.schedule_state = schedule_state
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить rollback"""
        success = self.schedule_state.rollback()
        
        if success:
            logger.info("↩️ Rollback successful")
            return {
                "success": True,
                "message": "Rollback successful"
            }
        else:
            return {
                "success": False,
                "error": "No checkpoint to rollback"
            }


class ScheduleState:
    """Состояние расписания с поддержкой checkpoint/rollback"""
    
    def __init__(self, initial_schedule: List[Dict]):
        self.current_schedule = initial_schedule
        self.checkpoints = []
        self.max_checkpoints = 10
    
    def save_checkpoint(self):
        """Сохранить текущее состояние"""
        checkpoint = copy.deepcopy(self.current_schedule)
        self.checkpoints.append(checkpoint)
        
        # Ограничить количество checkpoints
        if len(self.checkpoints) > self.max_checkpoints:
            self.checkpoints.pop(0)
    
    def rollback(self) -> bool:
        """Откатить к последнему checkpoint"""
        if not self.checkpoints:
            return False
        
        self.current_schedule = self.checkpoints.pop()
        return True


def get_temporal_tools(schedule_state: ScheduleState, teacher_preferences: Dict) -> List[Tool]:
    """Получить все инструменты для Stage 1"""
    return [
        AnalyzeScheduleTool(schedule_state, teacher_preferences),
        FindPreferenceViolationsTool(schedule_state, teacher_preferences),
        SwapLessonsTool(schedule_state, teacher_preferences),
        MoveToEmptySlotTool(schedule_state, teacher_preferences),
        RollbackTool(schedule_state)
    ]

