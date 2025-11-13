"""
GigaChat Improver для генетического алгоритма
Улучшение топ-3 расписаний через GigaChat каждые 10 итераций
"""
import json
import re
import logging
from typing import List, Dict
from utils.chromosome import Chromosome
from services.gigachat_client import GigaChatClient

logger = logging.getLogger(__name__)


class GigaChatImprover:
    """Улучшение через GigaChat"""
    
    def __init__(self):
        self.client = GigaChatClient()
    
    async def improve_top_chromosomes(self,
                                     chromosomes: List[Chromosome],
                                     teacher_preferences: Dict,
                                     top_n: int = 3) -> List[Chromosome]:
        """
        Улучшить топ-N расписаний через GigaChat
        
        Стратегия:
        1. Взять топ-3
        2. Найти нарушения предпочтений
        3. Попросить GigaChat предложить перестановки
        4. Применить рекомендации
        """
        if not self.client.access_token:
            logger.warning("GigaChat not available, skipping improvement")
            return chromosomes[:top_n]
        
        sorted_chroms = sorted(
            chromosomes, 
            key=lambda c: c.fitness, 
            reverse=True
        )
        top = sorted_chroms[:top_n]
        
        improved = []
        
        for i, chromosome in enumerate(top):
            try:
                logger.info(f"🤖 Improving chromosome {i + 1}/{top_n} via GigaChat")
                
                # Найти нарушения
                violations = self._find_violations(
                    chromosome, teacher_preferences
                )
                
                if not violations:
                    improved.append(chromosome)
                    continue
                
                # Построить промпт
                prompt = self._build_prompt(violations, chromosome)
                
                # Вызвать GigaChat
                suggestions = await self._call_gigachat(prompt)
                
                # Применить
                improved_chromosome = self._apply_suggestions(
                    chromosome, suggestions
                )
                
                improved.append(improved_chromosome)
                
            except Exception as e:
                logger.error(f"Error improving chromosome {i + 1}: {e}")
                improved.append(chromosome)
        
        return improved
    
    def _find_violations(self, chromosome: Chromosome,
                        teacher_preferences: Dict) -> List[Dict]:
        """Найти все нарушения предпочтений"""
        violations = []
        
        for lesson in chromosome.lessons:
            teacher_id = lesson.teacher_id
            
            if teacher_id not in teacher_preferences:
                continue
            
            teacher_info = teacher_preferences[teacher_id]
            priority = teacher_info.get('priority', 4)
            
            # Проверить предпочтение
            pref = None
            for p in teacher_info.get('preferences', []):
                if p.get('day_of_week') == lesson.day and \
                   p.get('time_slot') == lesson.slot:
                    pref = p
                    break
            
            if pref and not pref.get('is_preferred', True):
                violations.append({
                    'lesson_id': id(lesson),
                    'teacher': teacher_info.get('name', f'Teacher {teacher_id}'),
                    'priority': priority,
                    'current_day': lesson.day,
                    'current_slot': lesson.slot,
                    'discipline': lesson.discipline_name
                })
        
        # Сортировать по приоритету и ограничить до 20
        violations = sorted(violations, key=lambda v: v['priority'])[:20]
        
        return violations
    
    def _build_prompt(self, violations: List[Dict], 
                     chromosome: Chromosome) -> str:
        """Построить компактный промпт"""
        prompt = f"""Ты - эксперт по оптимизации расписания университета.

{len(violations)} нарушений предпочтений преподавателей (приоритет 1-4):

"""
        for i, v in enumerate(violations, 1):
            prompt += (
                f"{i}. {v['teacher']} (П{v['priority']}) | "
                f"Сейчас: День {v['current_day']}, Пара {v['current_slot']} | "
                f"Дисциплина: {v['discipline'][:30]}\n"
            )
        
        prompt += """
Предложи перестановки для улучшения. Ответ ТОЛЬКО JSON:
{
  "suggestions": [
    {
      "lesson_id": <число>,
      "new_day": <1-6>,
      "new_slot": <1-6>
    }
  ]
}

ТОЛЬКО JSON, без объяснений!
"""
        return prompt
    
    async def _call_gigachat(self, prompt: str) -> Dict:
        """Вызвать GigaChat API"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Эксперт по расписаниям. Отвечаешь только JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # GigaChat возвращает ответ в формате choices[0].message.content
            answer = ''
            if 'choices' in response and len(response['choices']) > 0:
                answer = response['choices'][0].get('message', {}).get('content', '')
            
            # Парсинг JSON
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {'suggestions': []}
            
        except Exception as e:
            logger.error(f"GigaChat API error: {e}")
            return {'suggestions': []}
    
    def _apply_suggestions(self, chromosome: Chromosome,
                          suggestions: Dict) -> Chromosome:
        """Применить рекомендации"""
        improved = chromosome.copy()
        
        # Создать маппинг lesson_id -> lesson
        lesson_map = {id(lesson): lesson for lesson in improved.lessons}
        
        for suggestion in suggestions.get('suggestions', []):
            lesson_id = suggestion.get('lesson_id')
            new_day = suggestion.get('new_day')
            new_slot = suggestion.get('new_slot')
            
            if lesson_id in lesson_map and new_day and new_slot:
                lesson = lesson_map[lesson_id]
                # Валидация
                if 1 <= new_day <= 6 and 1 <= new_slot <= 6:
                    lesson.day = new_day
                    lesson.slot = new_slot
        
        return improved

