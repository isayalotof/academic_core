"""
Stage 1 Agent
Оптимизация временных слотов с использованием GigaChat
"""

import logging
from typing import Dict, Any, List
import time

from services.gigachat_client import gigachat_client
from services.fitness import fitness_calculator
from tools.temporal_tools import ScheduleState, get_temporal_tools
from prompts.stage1_prompt import STAGE1_SYSTEM_PROMPT
from db.connection import db
from db.queries import generation_history as gen_queries, agent_actions as action_queries
from config import config

logger = logging.getLogger(__name__)


class Stage1Agent:
    """Агент для оптимизации временных слотов"""
    
    def __init__(self, generation_id: int, initial_schedule: List[Dict], teacher_preferences: Dict):
        self.generation_id = generation_id
        self.schedule_state = ScheduleState(initial_schedule)
        self.teacher_preferences = teacher_preferences
        
        # Инструменты
        self.tools = get_temporal_tools(self.schedule_state, teacher_preferences)
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # История разговора
        self.conversation_history = []
        
        # Текущая итерация
        self.current_iteration = 0
    
    def run(self, max_iterations: int) -> Dict[str, Any]:
        """
        Запустить оптимизацию
        
        Returns:
            Результат оптимизации
        """
        logger.info(f"🚀 Starting Stage 1 optimization (max {max_iterations} iterations)")
        
        # Начальный скор
        initial_result = fitness_calculator.calculate(
            self.schedule_state.current_schedule,
            self.teacher_preferences
        )
        initial_score = initial_result['total_score']
        best_score = initial_score
        
        logger.info(f"📊 Initial score: {initial_score}")
        
        # Early stopping
        iterations_without_improvement = 0
        
        for iteration in range(max_iterations):
            self.current_iteration = iteration + 1
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {self.current_iteration}/{max_iterations}")
            logger.info(f"{'='*60}")
            
            # Получить действие от агента
            action_start = time.time()
            
            try:
                action_result = self._agent_step()
                
                if not action_result['success']:
                    logger.warning(f"⚠️ Action failed: {action_result.get('error')}")
                    iterations_without_improvement += 1
                    continue
                
                # Текущий скор
                current_result = fitness_calculator.calculate(
                    self.schedule_state.current_schedule,
                    self.teacher_preferences
                )
                current_score = current_result['total_score']
                
                # Обновить лучший скор
                if current_score > best_score:
                    best_score = current_score
                    iterations_without_improvement = 0
                    logger.info(f"🎉 NEW BEST SCORE: {best_score}")
                else:
                    iterations_without_improvement += 1
                
                # Обновить БД
                db.execute_query(
                    gen_queries.UPDATE_GENERATION_ITERATION,
                    {
                        'job_id': str(self.generation_id),
                        'current_iteration': self.current_iteration,
                        'current_score': current_score,
                        'last_reasoning': action_result.get('reasoning', '')
                    },
                    fetch=False
                )
                
                # Сохранить действие
                execution_time = int((time.time() - action_start) * 1000)
                self._save_action(action_result, execution_time)
                
                # Early stopping
                if iterations_without_improvement >= config.EARLY_STOPPING_PATIENCE:
                    logger.info(f"⏹️ Early stopping: {iterations_without_improvement} iterations without improvement")
                    break
                
            except Exception as e:
                logger.error(f"❌ Error in iteration {self.current_iteration}: {e}", exc_info=True)
                iterations_without_improvement += 1
        
        # Финальный результат
        final_result = fitness_calculator.calculate(
            self.schedule_state.current_schedule,
            self.teacher_preferences
        )
        final_score = final_result['total_score']
        
        improvement = fitness_calculator.calculate_improvement(initial_score, final_score)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Stage 1 Complete!")
        logger.info(f"Initial score: {initial_score}")
        logger.info(f"Final score: {final_score}")
        logger.info(f"Best score: {best_score}")
        logger.info(f"Improvement: {improvement['delta']:+d} ({improvement['percent']:.2f}%)")
        logger.info(f"{'='*60}\n")
        
        return {
            'success': True,
            'initial_score': initial_score,
            'final_score': final_score,
            'best_score': best_score,
            'improvement': improvement,
            'iterations_completed': self.current_iteration,
            'schedule': self.schedule_state.current_schedule
        }
    
    def _agent_step(self) -> Dict[str, Any]:
        """Один шаг агента"""
        # Текущая аналитика
        analysis = self.tool_map['analyze_schedule'].execute()
        
        user_message = f"""
Итерация {self.current_iteration}

Текущее состояние расписания:
- Скор: {analysis['total_score']}
- Конфликты: {analysis['conflicts']}
- Нарушения предпочтений: {analysis['preference_violations']}
- Изолированные пары: {analysis['isolated_lessons']}
- Окна: {analysis['total_gaps']}

Что нужно улучшить? Выбери ОДНО действие.
"""
        
        # Получить ответ от GigaChat
        tools_definitions = [tool.get_definition() for tool in self.tools]
        
        response = gigachat_client.call_with_tools(
            system_prompt=STAGE1_SYSTEM_PROMPT,
            user_message=user_message,
            tools=tools_definitions,
            conversation_history=self.conversation_history[-5:]  # Последние 5
        )
        
        # Обработать ответ
        if response['type'] == 'function_call':
            func_name = response['function_name']
            func_args = response['arguments']
            reasoning = response.get('reasoning', '')
            
            logger.info(f"🤖 Agent: {reasoning}")
            logger.info(f"🔧 Calling tool: {func_name}({func_args})")
            
            # Выполнить функцию
            if func_name in self.tool_map:
                result = self.tool_map[func_name].execute(**func_args)
                
                return {
                    'success': result.get('success', True),
                    'action_type': func_name,
                    'action_params': func_args,
                    'result': result,
                    'reasoning': reasoning
                }
            else:
                return {
                    'success': False,
                    'error': f"Unknown tool: {func_name}"
                }
        
        else:
            # Текстовый ответ (возможно завершение)
            logger.info(f"💬 Agent: {response['content']}")
            return {
                'success': False,
                'error': "Agent returned text instead of function call"
            }
    
    def _save_action(self, action_result: Dict, execution_time_ms: int):
        """Сохранить действие в БД"""
        try:
            import json
            
            db.execute_query(
                action_queries.INSERT_AGENT_ACTION,
                {
                    'generation_id': self.generation_id,
                    'iteration': self.current_iteration,
                    'action_type': action_result.get('action_type', 'unknown'),
                    'action_params': json.dumps(action_result.get('action_params', {})),
                    'success': action_result['success'],
                    'score_before': action_result.get('result', {}).get('score_before'),
                    'score_after': action_result.get('result', {}).get('score_after'),
                    'score_delta': action_result.get('result', {}).get('score_delta'),
                    'reasoning': action_result.get('reasoning', ''),
                    'execution_time_ms': execution_time_ms
                },
                fetch=False
            )
        except Exception as e:
            logger.error(f"Failed to save action: {e}")

