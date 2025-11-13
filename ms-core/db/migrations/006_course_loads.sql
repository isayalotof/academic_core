-- Учебная нагрузка
-- Импортируется из Excel и используется ms-agent для генерации расписания

CREATE TABLE IF NOT EXISTS course_loads (
    id SERIAL PRIMARY KEY,
    
    -- Дисциплина
    discipline_id INTEGER REFERENCES disciplines(id) ON DELETE SET NULL,
    discipline_name VARCHAR(200) NOT NULL,     -- Денормализация для производительности
    discipline_code VARCHAR(50),
    
    -- Преподаватель
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE RESTRICT,
    teacher_name VARCHAR(200) NOT NULL,        -- Денормализация
    teacher_priority INTEGER NOT NULL,         -- Копия из teachers для быстрого доступа
    
    -- Группа
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE RESTRICT,
    group_name VARCHAR(100) NOT NULL,          -- Денормализация
    group_size INTEGER,                        -- Копия из groups
    
    -- Параметры занятия
    lesson_type VARCHAR(50) NOT NULL,          -- "Лекция", "Практика", "Лабораторная"
    hours_per_semester INTEGER NOT NULL,       -- Часов в семестре
    weeks_count INTEGER DEFAULT 16,            -- Количество недель
    lessons_per_week INTEGER NOT NULL,         -- Пар в неделю (вычисляется АВТОМАТИЧЕСКИ)
    
    -- Семестр
    semester INTEGER NOT NULL,                 -- 1 или 2
    academic_year VARCHAR(20) NOT NULL,        -- "2024/2025"
    
    -- Требования к аудитории (опционально)
    required_classroom_type VARCHAR(50),       -- 'LECTURE', 'COMPUTER_LAB', etc
    min_classroom_capacity INTEGER,
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    
    -- Откуда загружено
    source VARCHAR(20) DEFAULT 'manual',       -- 'manual', 'excel', 'import'
    import_batch_id VARCHAR(100),              -- ID батча импорта
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    
    CONSTRAINT valid_lesson_type CHECK (
        lesson_type IN ('Лекция', 'Практика', 'Лабораторная', 'Семинар')
    ),
    CONSTRAINT valid_semester CHECK (semester IN (1, 2))
);

-- Индексы
CREATE INDEX idx_course_loads_teacher ON course_loads(teacher_id);
CREATE INDEX idx_course_loads_group ON course_loads(group_id);
CREATE INDEX idx_course_loads_semester ON course_loads(semester, academic_year);
CREATE INDEX idx_course_loads_active ON course_loads(is_active) WHERE is_active = true;
CREATE INDEX idx_course_loads_batch ON course_loads(import_batch_id);
CREATE INDEX idx_course_loads_discipline ON course_loads(discipline_id);
CREATE INDEX idx_course_loads_teacher_semester ON course_loads(teacher_id, semester, academic_year);
CREATE INDEX idx_course_loads_group_semester ON course_loads(group_id, semester, academic_year);

-- ⭐ ТРИГГЕР ДЛЯ АВТОМАТИЧЕСКОГО РАСЧЁТА lessons_per_week
-- Формула: часов в семестр / 32 (округление вверх)
CREATE OR REPLACE FUNCTION calculate_lessons_per_week()
RETURNS TRIGGER AS $$
BEGIN
    -- Формула: hours_per_semester / 32
    -- Пример: 64 часа / 32 = 2 пары в неделю
    NEW.lessons_per_week := CEIL(NEW.hours_per_semester::DECIMAL / 32);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_lessons
    BEFORE INSERT OR UPDATE OF hours_per_semester, weeks_count ON course_loads
    FOR EACH ROW
    EXECUTE FUNCTION calculate_lessons_per_week();

-- Триггер для updated_at
CREATE OR REPLACE FUNCTION update_course_loads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER course_loads_updated_at_trigger
    BEFORE UPDATE ON course_loads
    FOR EACH ROW
    EXECUTE FUNCTION update_course_loads_updated_at();

-- Комментарии
COMMENT ON TABLE course_loads IS 'Учебная нагрузка - используется для генерации расписания';
COMMENT ON COLUMN course_loads.lessons_per_week IS 'Количество пар в неделю (вычисляется автоматически из hours_per_semester)';
COMMENT ON COLUMN course_loads.teacher_priority IS 'Копия приоритета из teachers для быстрого доступа';
COMMENT ON COLUMN course_loads.source IS 'Источник данных: manual=ручной ввод, excel=импорт из Excel';
COMMENT ON TRIGGER trigger_calculate_lessons ON course_loads IS 'Автоматический расчёт количества пар в неделю';

