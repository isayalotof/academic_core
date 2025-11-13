-- Миграция: Добавление колонки source_file для отслеживания источника данных
-- Дата: 2024

-- Добавление колонки source_file для отслеживания источника данных
ALTER TABLE course_loads ADD COLUMN IF NOT EXISTS source_file TEXT DEFAULT '';

-- Добавление индекса для быстрого поиска по учебному году
CREATE INDEX IF NOT EXISTS idx_course_loads_academic_year 
ON course_loads(academic_year);

-- Добавление индекса для поиска по группе и семестру
CREATE INDEX IF NOT EXISTS idx_course_loads_group_semester 
ON course_loads(group_name, semester);

-- Комментарий к колонке
COMMENT ON COLUMN course_loads.source_file IS 'Имя файла, из которого была загружена нагрузка';

