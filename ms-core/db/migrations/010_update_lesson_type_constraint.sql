-- Миграция: Обновление constraint valid_lesson_type для поддержки любых типов занятий
-- Дата: 2024
-- 
-- Проблема: constraint valid_lesson_type разрешал только 4 типа:
-- 'Лекция', 'Практика', 'Лабораторная', 'Семинар'
-- Но в Excel файлах могут быть любые типы: 'Практические занятия', 'Консультация', 
-- 'Контрольная работа', 'Экзамен', и т.д.
--
-- Решение: сделать constraint более гибким - проверять только что lesson_type не пустой
-- Это позволит загружать любые типы занятий из Excel файлов без необходимости
-- постоянно обновлять список разрешенных значений

-- Удалить старый constraint
ALTER TABLE course_loads DROP CONSTRAINT IF EXISTS valid_lesson_type;

-- Добавить новый constraint - проверка только на непустое значение
-- Это позволит загружать любые типы занятий из Excel
ALTER TABLE course_loads ADD CONSTRAINT valid_lesson_type CHECK (
    lesson_type IS NOT NULL AND 
    LENGTH(TRIM(lesson_type)) > 0
);

-- Комментарий
COMMENT ON CONSTRAINT valid_lesson_type ON course_loads IS 
    'Тип занятия. Может быть любым непустым значением из Excel файла (Лекция, Практика, Практические занятия, Консультация, Контрольная работа и т.д.)';

