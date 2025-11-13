"""
Genetic Operators для генетического алгоритма
Селекция, кроссовер, мутация
"""
import random
import logging
from typing import List, Tuple, Dict
from utils.chromosome import Chromosome, Lesson

logger = logging.getLogger(__name__)


class SelectionOperator:
    """Селекция"""
    
    @staticmethod
    def tournament_selection(population: List[Chromosome],
                           tournament_size: int = 5) -> Chromosome:
        """Турнирная селекция"""
        if len(population) < tournament_size:
            tournament_size = len(population)
        
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=lambda c: c.fitness)
    
    @staticmethod
    def elitism_selection(population: List[Chromosome],
                         elite_size: int = 10) -> List[Chromosome]:
        """Элитизм - топ elite_size"""
        sorted_pop = sorted(population, key=lambda c: c.fitness, reverse=True)
        return sorted_pop[:elite_size]


class CrossoverOperator:
    """Кроссовер"""
    
    @staticmethod
    def single_point_crossover(parent1: Chromosome,
                              parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Одноточечный кроссовер"""
        if len(parent1.lessons) == 0 or len(parent2.lessons) == 0:
            return parent1.copy(), parent2.copy()
        
        point = random.randint(1, min(len(parent1.lessons), len(parent2.lessons)) - 1)
        
        child1_lessons = parent1.lessons[:point] + parent2.lessons[point:]
        child2_lessons = parent2.lessons[:point] + parent1.lessons[point:]
        
        child1 = Chromosome([lesson.copy() for lesson in child1_lessons])
        child2 = Chromosome([lesson.copy() for lesson in child2_lessons])
        
        return child1, child2
    
    @staticmethod
    def uniform_crossover(parent1: Chromosome,
                         parent2: Chromosome,
                         crossover_rate: float = 0.5) -> Tuple[Chromosome, Chromosome]:
        """Однородный кроссовер"""
        if len(parent1.lessons) == 0 or len(parent2.lessons) == 0:
            return parent1.copy(), parent2.copy()
        
        # Создать маппинг по course_load_id
        p1_map = {}
        p2_map = {}
        
        for lesson in parent1.lessons:
            key = (lesson.course_load_id, lesson.week)
            if key not in p1_map:
                p1_map[key] = []
            p1_map[key].append(lesson)
        
        for lesson in parent2.lessons:
            key = (lesson.course_load_id, lesson.week)
            if key not in p2_map:
                p2_map[key] = []
            p2_map[key].append(lesson)
        
        child1_lessons = []
        child2_lessons = []
        
        all_keys = set(p1_map.keys()) | set(p2_map.keys())
        
        for key in all_keys:
            if random.random() < crossover_rate:
                # Взять от parent2 для child1, от parent1 для child2
                if key in p2_map:
                    child1_lessons.extend([l.copy() for l in p2_map[key]])
                if key in p1_map:
                    child2_lessons.extend([l.copy() for l in p1_map[key]])
            else:
                # Взять от parent1 для child1, от parent2 для child2
                if key in p1_map:
                    child1_lessons.extend([l.copy() for l in p1_map[key]])
                if key in p2_map:
                    child2_lessons.extend([l.copy() for l in p2_map[key]])
        
        return Chromosome(child1_lessons), Chromosome(child2_lessons)


class MutationOperator:
    """Мутация"""
    
    def __init__(self, classrooms: List[Dict]):
        self.classrooms = classrooms
    
    def mutate(self, chromosome: Chromosome, 
              mutation_rate: float = 0.1) -> Chromosome:
        """Мутация - изменить день/слот случайных занятий"""
        mutated = chromosome.copy()
        
        for lesson in mutated.lessons:
            if random.random() < mutation_rate:
                # Изменить день/слот
                lesson.day = random.randint(1, 6)
                lesson.slot = random.randint(1, 6)
                
                # Опционально: изменить аудиторию
                if self.classrooms and random.random() < 0.3:
                    classroom = random.choice(self.classrooms)
                    lesson.classroom_id = classroom.get('id', 0)
        
        return mutated
    
    def smart_mutate(self, chromosome: Chromosome,
                    teacher_preferences: Dict,
                    mutation_rate: float = 0.1) -> Chromosome:
        """Умная мутация - переместить в предпочтительные слоты"""
        mutated = chromosome.copy()
        
        for lesson in mutated.lessons:
            if random.random() < mutation_rate:
                teacher_id = lesson.teacher_id
                
                if teacher_id in teacher_preferences:
                    prefs = teacher_preferences[teacher_id].get('preferences', [])
                    preferred_slots = [
                        (p['day_of_week'], p['time_slot'])
                        for p in prefs
                        if p.get('is_preferred', False)
                    ]
                    
                    if preferred_slots:
                        # Переместить в предпочтительный слот
                        new_day, new_slot = random.choice(preferred_slots)
                        lesson.day = new_day
                        lesson.slot = new_slot
                    else:
                        # Обычная мутация
                        lesson.day = random.randint(1, 6)
                        lesson.slot = random.randint(1, 6)
                else:
                    # Обычная мутация
                    lesson.day = random.randint(1, 6)
                    lesson.slot = random.randint(1, 6)
        
        return mutated

