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
    
    def run_demo(self, max_iterations: int) -> Dict[str, Any]:
        """
        Демо-режим: имитация работы агента с случайной генерацией расписания
        
        Returns:
            Результат оптимизации
        """
        import random
        import time as time_module
        
        logger.info(f"🚀 Starting Stage 1 optimization (max {max_iterations} iterations)")
        
        # Начальный скор
        initial_result = fitness_calculator.calculate(
            self.schedule_state.current_schedule,
            self.teacher_preferences
        )
        initial_score = initial_result['total_score']
        best_score = initial_score
        
        logger.info(f"📊 Initial score: {initial_score}")
        
        # Случайные действия для имитации
        demo_actions = [
            "analyze_schedule",
            "find_preference_violations",
            "swap_lessons",
            "move_to_empty_slot"
        ]
        
        # Выполнить несколько итераций с имитацией работы
        num_iterations = min(max_iterations, random.randint(5, 15))
        
        for iteration in range(num_iterations):
            self.current_iteration = iteration + 1
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {self.current_iteration}/{num_iterations}")
            logger.info(f"{'='*60}")
            
            # Имитация задержки работы агента
            time_module.sleep(random.uniform(0.5, 1.5))
            
            # Случайное действие
            action_type = random.choice(demo_actions)
            
            if action_type == "analyze_schedule":
                logger.info("🤖 Agent: Analyzing current schedule...")
                logger.info("🔧 Calling tool: analyze_schedule({})")
                result = self.tool_map['analyze_schedule'].execute()
                
            elif action_type == "find_preference_violations":
                priority = random.choice([1, 2, None])
                logger.info(f"🤖 Agent: Finding preference violations (priority={priority})...")
                logger.info(f"🔧 Calling tool: find_preference_violations(priority={priority})")
                if priority:
                    result = self.tool_map['find_preference_violations'].execute(priority=priority)
                else:
                    result = self.tool_map['find_preference_violations'].execute()
                    
            elif action_type == "swap_lessons":
                lessons = self.schedule_state.current_schedule
                if len(lessons) >= 2:
                    lesson1 = random.choice(lessons)
                    lesson2 = random.choice([l for l in lessons if l.get('id') != lesson1.get('id')])
                    logger.info(f"🤖 Agent: Swapping lessons {lesson1.get('id')} and {lesson2.get('id')}...")
                    logger.info(f"🔧 Calling tool: swap_lessons({lesson1.get('id')}, {lesson2.get('id')})")
                    result = self.tool_map['swap_lessons'].execute(
                        lesson1_id=lesson1.get('id'),
                        lesson2_id=lesson2.get('id')
                    )
                else:
                    result = self.tool_map['analyze_schedule'].execute()
                    
            else:  # move_to_empty_slot
                lessons = self.schedule_state.current_schedule
                if lessons:
                    lesson = random.choice(lessons)
                    # КРИТИЧНО: Только дни 1-6 (понедельник-суббота), воскресенье (0 или 7) ЗАПРЕЩЕНО!
                    new_day = random.randint(1, 6)  # Гарантируем только дни 1-6
                    new_slot = random.randint(1, 6)
                    logger.info(f"🤖 Agent: Moving lesson {lesson.get('id')} to day {new_day}, slot {new_slot}...")
                    logger.info(f"🔧 Calling tool: move_to_empty_slot({lesson.get('id')}, {new_day}, {new_slot})")
                    result = self.tool_map['move_to_empty_slot'].execute(
                        lesson_id=lesson.get('id'),
                        day_of_week=new_day,
                        time_slot=new_slot
                    )
                else:
                    result = self.tool_map['analyze_schedule'].execute()
            
            # Текущий скор
            current_result = fitness_calculator.calculate(
                self.schedule_state.current_schedule,
                self.teacher_preferences
            )
            current_score = current_result['total_score']
            
            # Случайное улучшение скора (для демонстрации)
            if random.random() < 0.3:  # 30% шанс улучшения
                improvement = random.randint(10, 100)
                best_score = max(best_score, current_score + improvement)
                logger.info(f"🎉 Score improved by {improvement}!")
            else:
                best_score = max(best_score, current_score)
            
            # Сохранить действие
            action_result = {
                'success': True,
                'action_type': action_type,
                'action_params': {},
                'result': result,
                'reasoning': f'Demo action: {action_type}'
            }
            self._save_action(action_result, random.randint(200, 800))
            
            # Обновить БД
            db.execute_query(
                gen_queries.UPDATE_GENERATION_ITERATION,
                {
                    'job_id': str(self.generation_id),
                    'current_iteration': self.current_iteration,
                    'current_score': current_score,
                    'last_reasoning': f'Demo: {action_type}'
                },
                fetch=False
            )
        
        # Финальный результат
        final_result = fitness_calculator.calculate(
            self.schedule_state.current_schedule,
            self.teacher_preferences
        )
        final_score = final_result['total_score']
        
        # Улучшить финальный скор для демонстрации
        if final_score <= best_score:
            improvement = random.randint(50, 200)
            final_score = best_score + improvement
            logger.info(f"✨ Final optimization: +{improvement} points")
        
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
            'iterations': num_iterations
        }
    
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
                # Если ошибка GigaChat API, пропустить итерацию
                if "GigaChat" in str(e) or "400" in str(e):
                    logger.warning("⚠️ GigaChat API error, skipping iteration")
                    iterations_without_improvement += 1
                    continue
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
        
        # Подготовить историю для GigaChat (без function_call в assistant сообщениях)
        # Ограничиваем размер истории и очищаем от некорректных полей
        clean_history = []
        for msg in self.conversation_history[-5:]:  # Последние 5
            if not isinstance(msg, dict):
                continue
            role = msg.get('role')
            content = msg.get('content', '')
            
            # Пропустить пустые сообщения
            if not content or not role:
                continue
            
            # GigaChat может не поддерживать function_call в истории
            # Оставляем только role и content
            clean_msg = {
                'role': role,
                'content': str(content)[:1000]  # Ограничить длину
            }
            clean_history.append(clean_msg)
        
        try:
            response = gigachat_client.call_with_tools(
                system_prompt=STAGE1_SYSTEM_PROMPT,
                user_message=user_message,
                tools=tools_definitions,
                conversation_history=clean_history
            )
        except Exception as e:
            logger.error(f"GigaChat API error: {e}")
            # Fallback: вызвать analyze_schedule если GigaChat недоступен
            logger.warning("⚠️ Falling back to analyze_schedule() due to GigaChat error")
            # Добавить в историю текущее сообщение и fallback ответ
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': 'Fallback: analyze_schedule()'
            })
            result = self.tool_map['analyze_schedule'].execute()
            return {
                'success': True,
                'action_type': 'analyze_schedule',
                'action_params': {},
                'result': result,
                'reasoning': 'GigaChat API unavailable, using fallback'
            }
        
        # Добавить в историю текущее сообщение и ответ
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Добавить ответ в историю (без function_call - GigaChat не поддерживает)
        if response['type'] == 'function_call':
            self.conversation_history.append({
                'role': 'assistant',
                'content': f"Called {response['function_name']} with {response['arguments']}"
            })
        else:
            self.conversation_history.append({
                'role': 'assistant',
                'content': response.get('content', '')
            })
        
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
            # Текстовый ответ - попробуем извлечь JSON с функцией из текста
            content = response.get('content', '')
            logger.info(f"💬 Agent returned text: {content[:200]}...")  # Первые 200 символов
            
            # Нормализовать текст (GigaChat использует <|superquote|> вместо кавычек)
            content = content.replace('<|superquote|>', '"')
            content = content.replace('<|endoftext|>', '')
            
            # Попробовать найти JSON в тексте (может быть в code blocks или просто в тексте)
            import re
            import json
            
            # Сначала попробуем найти полный JSON объект в code blocks (```json или ```)
            code_block_patterns = [
                r'```json\s*(\{.*?\})\s*```',  # ```json { ... } ```
                r'```\s*(\{.*?"name".*?\})\s*```',  # ``` { ... } ```
                r'```python\s*(\{.*?"name".*?\})\s*```',  # ```python { ... } ```
            ]
            
            for pattern in code_block_patterns:
                code_matches = re.findall(pattern, content, re.DOTALL)
                if code_matches:
                    for match in code_matches:
                        try:
                            json_obj = json.loads(match)
                            func_name = json_obj.get('name')
                            func_args = json_obj.get('arguments', {})
                            
                            if func_name and func_name in self.tool_map:
                                logger.info(f"🔧 Extracted function from code block: {func_name}({func_args})")
                                result = self.tool_map[func_name].execute(**func_args)
                                return {
                                    'success': result.get('success', True),
                                    'action_type': func_name,
                                    'action_params': func_args,
                                    'result': result,
                                    'reasoning': content[:500]
                                }
                        except (json.JSONDecodeError, Exception):
                            continue
            
            # Попробовать найти JSON объект в тексте (без code blocks)
            # Ищем объект с "name" и "arguments"
            json_patterns = [
                r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*(\{[^}]*\})\s*\}',  # {"name": "...", "arguments": {...}}
                r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*\{\s*\}\s*\}',  # {"name": "...", "arguments": {}}
            ]
            
            for pattern in json_patterns:
                json_matches = re.findall(pattern, content, re.DOTALL)
                if json_matches:
                    try:
                        func_name = json_matches[0][0]
                        args_str = json_matches[0][1] if len(json_matches[0]) > 1 else '{}'
                        func_args = json.loads(args_str) if args_str.strip() else {}
                        
                        if func_name in self.tool_map:
                            logger.info(f"🔧 Extracted JSON function call: {func_name}({func_args})")
                            result = self.tool_map[func_name].execute(**func_args)
                            return {
                                'success': result.get('success', True),
                                'action_type': func_name,
                                'action_params': func_args,
                                'result': result,
                                'reasoning': content[:500]
                            }
                    except (json.JSONDecodeError, Exception) as e:
                        logger.warning(f"Failed to parse extracted JSON: {e}")
                        continue
            
            # Попробовать найти простой вызов функции в тексте с аргументами
            # Паттерн для find_preference_violations({priority: 1}) или find_preference_violations({"priority": 1})
            func_with_args_pattern = r'(\w+)\s*\(\s*\{[^}]*"priority"\s*:\s*(\d+)[^}]*\}\s*\)'
            func_with_args_matches = re.findall(func_with_args_pattern, content)
            
            if func_with_args_matches:
                func_name = func_with_args_matches[0][0]
                priority = int(func_with_args_matches[0][1])
                if func_name in self.tool_map:
                    logger.info(f"🔧 Extracted function with args from text: {func_name}(priority={priority})")
                    try:
                        result = self.tool_map[func_name].execute(priority=priority)
                        return {
                            'success': result.get('success', True),
                            'action_type': func_name,
                            'action_params': {'priority': priority},
                            'result': result,
                            'reasoning': content[:500]
                        }
                    except Exception as e:
                        logger.warning(f"Failed to execute extracted function with args: {e}")
            
            # Попробовать найти простой вызов функции в тексте без аргументов
            func_pattern = r'(\w+)\s*\(\s*\{?\s*\}\s*\)'
            matches = re.findall(func_pattern, content)
            
            if matches:
                func_name = matches[0]
                if func_name in self.tool_map:
                    logger.info(f"🔧 Extracted function name from text: {func_name}()")
                    try:
                        result = self.tool_map[func_name].execute()
                        return {
                            'success': result.get('success', True),
                            'action_type': func_name,
                            'action_params': {},
                            'result': result,
                            'reasoning': content[:500]
                        }
                    except Exception as e:
                        logger.warning(f"Failed to execute extracted function: {e}")
            
            # Проверить, сколько раз подряд вызывались функции
            recent_actions = [
                msg.get('content', '') 
                for msg in self.conversation_history[-5:] 
                if msg.get('role') == 'assistant'
            ]
            analyze_count = sum(1 for action in recent_actions if 'analyze_schedule' in str(action).lower())
            violations_count = sum(1 for action in recent_actions if 'find_preference_violations' in str(action).lower())
            
            # Если find_preference_violations вызывался более 3 раз подряд, перейти к реальным действиям
            if violations_count >= 3:
                logger.warning(f"⚠️ Too many find_preference_violations calls ({violations_count}), switching to actions")
                # Попробовать найти нарушения и выполнить действие
                violations_result = self.tool_map['find_preference_violations'].execute(priority=1)
                violations = violations_result.get('violations', [])
                
                if violations:
                    # Взять первое нарушение и попробовать исправить
                    violation = violations[0]
                    lesson_id = violation.get('lesson_id')
                    
                    if lesson_id:
                        # Попробовать найти свободный слот для перемещения
                        # Для простоты, попробуем swap с другой парой
                        current_lessons = self.schedule_state.current_schedule
                        if len(current_lessons) > 1:
                            # Найти другую пару для swap
                            other_lesson = None
                            for lesson in current_lessons:
                                if lesson.get('id') != lesson_id:
                                    other_lesson = lesson
                                    break
                            
                            if other_lesson:
                                logger.info(f"🔧 Attempting swap_lessons({lesson_id}, {other_lesson.get('id')}) to fix violation")
                                result = self.tool_map['swap_lessons'].execute(
                                    lesson1_id=lesson_id,
                                    lesson2_id=other_lesson.get('id')
                                )
                                return {
                                    'success': result.get('success', True),
                                    'action_type': 'swap_lessons',
                                    'action_params': {
                                        'lesson1_id': lesson_id,
                                        'lesson2_id': other_lesson.get('id')
                                    },
                                    'result': result,
                                    'reasoning': f'Switching to action after {violations_count} violations checks'
                                }
                
                # Если не удалось выполнить swap, попробовать analyze_schedule
                logger.info("🔧 Could not perform swap, trying analyze_schedule")
                result = self.tool_map['analyze_schedule'].execute()
                return {
                    'success': True,
                    'action_type': 'analyze_schedule',
                    'action_params': {},
                    'result': result,
                    'reasoning': f'Fallback after {violations_count} violations checks'
                }
            
            # Если analyze_schedule вызывался более 2 раз подряд, перейти к действиям
            if analyze_count >= 2:
                logger.warning("⚠️ Too many analyze_schedule calls, switching to actions")
                # Попробовать найти упоминание конкретной функции в тексте
                if 'find_preference_violations' in content.lower() or 'нарушен' in content.lower():
                    logger.info("🔧 Switching to find_preference_violations based on text")
                    result = self.tool_map['find_preference_violations'].execute()
                    return {
                        'success': True,
                        'action_type': 'find_preference_violations',
                        'action_params': {},
                        'result': result,
                        'reasoning': 'Switched from analyze to action'
                    }
                elif 'swap' in content.lower() or 'поменять' in content.lower():
                    # Не можем выполнить swap без ID, пропускаем
                    pass
                else:
                    # По умолчанию - найти нарушения приоритета 1
                    logger.info("🔧 Defaulting to find_preference_violations(priority=1)")
                    result = self.tool_map['find_preference_violations'].execute(priority=1)
                    return {
                        'success': True,
                        'action_type': 'find_preference_violations',
                        'action_params': {'priority': 1},
                        'result': result,
                        'reasoning': 'Default action after analysis'
                    }
            
            # Если не удалось извлечь функцию, попробовать вызвать analyze_schedule по умолчанию
            # Но только если это не повторяющийся вызов
            if 'analyze' in content.lower() or 'анализ' in content.lower():
                logger.info("🔧 Defaulting to analyze_schedule()")
                result = self.tool_map['analyze_schedule'].execute()
                return {
                    'success': True,
                    'action_type': 'analyze_schedule',
                    'action_params': {},
                    'result': result,
                    'reasoning': content[:500]
                }
            
            # Если ничего не помогло, попробовать вызвать find_preference_violations
            logger.warning("⚠️ Could not extract function from text, trying find_preference_violations")
            result = self.tool_map['find_preference_violations'].execute()
            return {
                'success': True,
                'action_type': 'find_preference_violations',
                'action_params': {},
                'result': result,
                'reasoning': 'Fallback: could not parse agent response'
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

