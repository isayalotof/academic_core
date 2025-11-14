-- ============================================
-- MIGRATION 006: ADD course_load_id AND MAKE semester/academic_year NULLABLE
-- ============================================
-- Добавляет колонку course_load_id для связи с учебной нагрузкой
-- Делает semester и academic_year nullable для совместимости с ms-agent

-- Добавить course_load_id
ALTER TABLE schedules 
ADD COLUMN IF NOT EXISTS course_load_id INTEGER;

-- Сделать semester и academic_year nullable (для совместимости с ms-agent)
ALTER TABLE schedules 
ALTER COLUMN semester DROP NOT NULL;

ALTER TABLE schedules 
ALTER COLUMN academic_year DROP NOT NULL;

-- Индекс для быстрого поиска по course_load_id
CREATE INDEX IF NOT EXISTS idx_schedules_course_load ON schedules(course_load_id) 
WHERE course_load_id IS NOT NULL;

-- Комментарии
COMMENT ON COLUMN schedules.course_load_id IS 'ID учебной нагрузки (course_load) из ms-core';
COMMENT ON COLUMN schedules.semester IS 'Номер семестра (1 или 2). Может быть NULL для временных расписаний.';
COMMENT ON COLUMN schedules.academic_year IS 'Учебный год (например, "2024/2025"). Может быть NULL для временных расписаний.';

