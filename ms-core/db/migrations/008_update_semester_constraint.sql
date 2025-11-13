-- Миграция: Обновление constraint valid_semester для поддержки семестров 1-12
-- Дата: 2024
-- 
-- Проблема: constraint valid_semester ограничивал семестр значениями 1 или 2,
-- но система должна поддерживать семестры 1-12 (для групп на разных курсах)
--
-- Решение: обновить constraint для поддержки семестров 1-12

-- Удалить старый constraint
ALTER TABLE course_loads DROP CONSTRAINT IF EXISTS valid_semester;

-- Добавить новый constraint с поддержкой семестров 1-12
ALTER TABLE course_loads ADD CONSTRAINT valid_semester 
    CHECK (semester >= 1 AND semester <= 12);

-- Комментарий
COMMENT ON CONSTRAINT valid_semester ON course_loads IS 
    'Семестр обучения группы (1-12). 1-2 - первый курс, 3-4 - второй курс, и т.д.';

