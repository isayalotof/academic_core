-- ============================================
-- MIGRATION 001: SCHEDULES TABLE
-- ============================================
-- Основная таблица расписания

CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    
    -- Временной слот
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),  -- 1=Пн, 6=Сб
    time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 1 AND 6),      -- Номер пары
    week_type VARCHAR(10) DEFAULT 'both',      -- 'odd', 'even', 'both' (числитель/знаменатель)
    
    -- Дисциплина
    discipline_id INTEGER,                     -- Ссылка на дисциплины (опционально)
    discipline_name VARCHAR(200) NOT NULL,
    discipline_code VARCHAR(50),
    
    -- Преподаватель
    teacher_id INTEGER NOT NULL,
    teacher_name VARCHAR(200) NOT NULL,
    
    -- Группа
    group_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    group_size INTEGER,
    
    -- Аудитория
    classroom_id INTEGER,
    classroom_name VARCHAR(50),
    building_name VARCHAR(100),
    
    -- Тип занятия
    lesson_type VARCHAR(50) NOT NULL,          -- "Лекция", "Практика", "Лабораторная"
    
    -- Семестр
    semester INTEGER NOT NULL,
    academic_year VARCHAR(20) NOT NULL,        -- "2024/2025"
    
    -- Время (опционально, для точности)
    start_time TIME,                           -- 09:00
    end_time TIME,                             -- 10:30
    
    -- Статус
    is_active BOOLEAN DEFAULT true,            -- Текущее активное расписание
    status VARCHAR(20) DEFAULT 'scheduled',    -- 'scheduled', 'completed', 'cancelled'
    
    -- Связь с генерацией
    generation_id INTEGER,                     -- ID генерации из ms-agent
    
    -- Примечания
    notes TEXT,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER
);

-- ============ ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ ============

-- Основные индексы для быстрого поиска
CREATE INDEX idx_schedules_teacher ON schedules(teacher_id, is_active) WHERE is_active = true;
CREATE INDEX idx_schedules_group ON schedules(group_id, is_active) WHERE is_active = true;
CREATE INDEX idx_schedules_classroom ON schedules(classroom_id, is_active) WHERE classroom_id IS NOT NULL AND is_active = true;

-- Индексы для временных запросов
CREATE INDEX idx_schedules_time ON schedules(day_of_week, time_slot, week_type, is_active) WHERE is_active = true;
CREATE INDEX idx_schedules_active ON schedules(is_active) WHERE is_active = true;

-- Индекс для семестра
CREATE INDEX idx_schedules_semester ON schedules(semester, academic_year, is_active);

-- Индекс для генерации
CREATE INDEX idx_schedules_generation ON schedules(generation_id) WHERE generation_id IS NOT NULL;

-- Составной индекс для сложных запросов
CREATE INDEX idx_schedules_full_slot ON schedules(
    day_of_week, 
    time_slot, 
    week_type, 
    semester, 
    academic_year, 
    is_active
) WHERE is_active = true;

-- ============ ПОЛНОТЕКСТОВЫЙ ПОИСК ============

-- Индекс для поиска по тексту (русский язык)
CREATE INDEX idx_schedules_search ON schedules 
USING gin(
    to_tsvector('russian', 
        coalesce(discipline_name, '') || ' ' || 
        coalesce(teacher_name, '') || ' ' || 
        coalesce(group_name, '')
    )
);

-- ============ ФУНКЦИЯ ДЛЯ АВТООБНОВЛЕНИЯ updated_at ============

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_schedules_updated_at 
    BEFORE UPDATE ON schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============ КОММЕНТАРИИ ============

COMMENT ON TABLE schedules IS 'Основная таблица расписания занятий университета';
COMMENT ON COLUMN schedules.day_of_week IS '1=Понедельник, 2=Вторник, ..., 6=Суббота';
COMMENT ON COLUMN schedules.time_slot IS 'Номер пары (1-6)';
COMMENT ON COLUMN schedules.week_type IS 'odd=числитель, even=знаменатель, both=каждую неделю';
COMMENT ON COLUMN schedules.is_active IS 'Текущее активное расписание (только одно на семестр)';
COMMENT ON COLUMN schedules.generation_id IS 'ID генерации из ms-agent (если создано агентом)';

