-- ============================================
-- MIGRATION 003: SCHEDULE SNAPSHOTS
-- ============================================
-- Снимки расписания для backup и сравнения

CREATE TABLE IF NOT EXISTS schedule_snapshots (
    id SERIAL PRIMARY KEY,
    
    -- Идентификация
    name VARCHAR(200) NOT NULL,                -- "Расписание осень 2024", "Backup 01.09.2024"
    description TEXT,
    
    -- Семестр
    semester INTEGER NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    
    -- Данные (полный снимок)
    snapshot_data JSONB NOT NULL,             -- Полное расписание в JSON
    
    -- Статистика
    total_lessons INTEGER DEFAULT 0,
    total_teachers INTEGER DEFAULT 0,
    total_groups INTEGER DEFAULT 0,
    total_classrooms INTEGER DEFAULT 0,
    
    -- Метрики качества
    fitness_score INTEGER,
    conflicts_count INTEGER DEFAULT 0,
    
    -- Тип снимка
    snapshot_type VARCHAR(20) DEFAULT 'manual', -- 'manual', 'auto', 'generation', 'backup'
    generation_id INTEGER,                      -- Если из ms-agent
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    created_by_name VARCHAR(200),
    
    -- Размер снимка (для мониторинга)
    data_size_bytes BIGINT
);

-- ============ ИНДЕКСЫ ============

CREATE INDEX idx_snapshots_semester ON schedule_snapshots(semester, academic_year);

CREATE INDEX idx_snapshots_created ON schedule_snapshots(created_at DESC);

CREATE INDEX idx_snapshots_type ON schedule_snapshots(snapshot_type);

CREATE INDEX idx_snapshots_name ON schedule_snapshots(name);

-- GIN индекс для поиска внутри JSON
CREATE INDEX idx_snapshots_data ON schedule_snapshots USING gin(snapshot_data);

-- ============ ФУНКЦИЯ ДЛЯ ВЫЧИСЛЕНИЯ РАЗМЕРА ============

CREATE OR REPLACE FUNCTION calculate_snapshot_size()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_size_bytes = length(NEW.snapshot_data::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER snapshot_size_trigger
    BEFORE INSERT OR UPDATE ON schedule_snapshots
    FOR EACH ROW
    EXECUTE FUNCTION calculate_snapshot_size();

-- ============ ФУНКЦИЯ ДЛЯ СОЗДАНИЯ АВТОМАТИЧЕСКОГО СНИМКА ============

CREATE OR REPLACE FUNCTION create_auto_snapshot(
    p_semester INTEGER,
    p_academic_year VARCHAR,
    p_snapshot_type VARCHAR DEFAULT 'auto'
) RETURNS INTEGER AS $$
DECLARE
    v_snapshot_id INTEGER;
    v_snapshot_data JSONB;
    v_total_lessons INTEGER;
    v_total_teachers INTEGER;
    v_total_groups INTEGER;
BEGIN
    -- Собрать все активные занятия в JSON
    SELECT 
        jsonb_agg(
            jsonb_build_object(
                'id', s.id,
                'day_of_week', s.day_of_week,
                'time_slot', s.time_slot,
                'week_type', s.week_type,
                'discipline_name', s.discipline_name,
                'teacher_id', s.teacher_id,
                'teacher_name', s.teacher_name,
                'group_id', s.group_id,
                'group_name', s.group_name,
                'classroom_id', s.classroom_id,
                'classroom_name', s.classroom_name,
                'lesson_type', s.lesson_type,
                'notes', s.notes
            )
        ),
        COUNT(*),
        COUNT(DISTINCT teacher_id),
        COUNT(DISTINCT group_id)
    INTO v_snapshot_data, v_total_lessons, v_total_teachers, v_total_groups
    FROM schedules s
    WHERE 
        s.semester = p_semester 
        AND s.academic_year = p_academic_year
        AND s.is_active = true;
    
    -- Вставить снимок
    INSERT INTO schedule_snapshots (
        name,
        description,
        semester,
        academic_year,
        snapshot_data,
        total_lessons,
        total_teachers,
        total_groups,
        snapshot_type
    ) VALUES (
        'Auto snapshot ' || to_char(NOW(), 'YYYY-MM-DD HH24:MI'),
        'Automatic snapshot before changes',
        p_semester,
        p_academic_year,
        v_snapshot_data,
        v_total_lessons,
        v_total_teachers,
        v_total_groups,
        p_snapshot_type
    ) RETURNING id INTO v_snapshot_id;
    
    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;

-- ============ КОММЕНТАРИИ ============

COMMENT ON TABLE schedule_snapshots IS 'Снимки расписания для backup и восстановления';
COMMENT ON COLUMN schedule_snapshots.snapshot_data IS 'Полный снимок расписания в JSON формате';
COMMENT ON COLUMN schedule_snapshots.snapshot_type IS 'manual=вручную, auto=автоматический, generation=из агента, backup=перед изменениями';
COMMENT ON FUNCTION create_auto_snapshot IS 'Создать автоматический снимок расписания';

