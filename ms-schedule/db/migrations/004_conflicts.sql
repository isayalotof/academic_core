-- ============================================
-- MIGRATION 004: SCHEDULE CONFLICTS
-- ============================================
-- Таблица для отслеживания конфликтов расписания

CREATE TABLE IF NOT EXISTS schedule_conflicts (
    id SERIAL PRIMARY KEY,
    
    -- Временной слот где обнаружен конфликт
    day_of_week INTEGER NOT NULL,
    time_slot INTEGER NOT NULL,
    week_type VARCHAR(10),
    
    -- Тип конфликта
    conflict_type VARCHAR(20) NOT NULL,        -- 'teacher', 'group', 'classroom'
    
    -- Сущность с конфликтом
    entity_id INTEGER NOT NULL,                -- teacher_id / group_id / classroom_id
    entity_name VARCHAR(200),
    
    -- Пары в конфликте (массив ID)
    schedule_ids INTEGER[] NOT NULL,
    
    -- Семестр
    semester INTEGER NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    
    -- Статус
    status VARCHAR(20) DEFAULT 'active',       -- 'active', 'resolved', 'ignored'
    resolution TEXT,                           -- Описание решения
    
    -- Серьёзность
    severity VARCHAR(20) DEFAULT 'high',       -- 'low', 'medium', 'high', 'critical'
    
    -- Метаданные
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolved_by INTEGER,
    resolved_by_name VARCHAR(200)
);

-- ============ ИНДЕКСЫ ============

CREATE INDEX idx_conflicts_status ON schedule_conflicts(status);

CREATE INDEX idx_conflicts_type ON schedule_conflicts(conflict_type);

CREATE INDEX idx_conflicts_entity ON schedule_conflicts(entity_id, conflict_type);

CREATE INDEX idx_conflicts_semester ON schedule_conflicts(semester, academic_year);

CREATE INDEX idx_conflicts_severity ON schedule_conflicts(severity, status) 
    WHERE status = 'active';

-- Индекс для временных слотов
CREATE INDEX idx_conflicts_slot ON schedule_conflicts(day_of_week, time_slot, week_type);

-- GIN индекс для массива schedule_ids
CREATE INDEX idx_conflicts_schedule_ids ON schedule_conflicts USING gin(schedule_ids);

-- ============ ФУНКЦИЯ ДЛЯ ОБНАРУЖЕНИЯ КОНФЛИКТОВ ============

CREATE OR REPLACE FUNCTION detect_schedule_conflicts(
    p_semester INTEGER,
    p_academic_year VARCHAR
) RETURNS TABLE(
    conflict_type VARCHAR,
    entity_id INTEGER,
    entity_name VARCHAR,
    day_of_week INTEGER,
    time_slot INTEGER,
    week_type VARCHAR,
    schedule_ids INTEGER[],
    conflicts_count BIGINT
) AS $$
BEGIN
    -- Конфликты преподавателей
    RETURN QUERY
    SELECT 
        'teacher'::VARCHAR as conflict_type,
        s.teacher_id as entity_id,
        s.teacher_name as entity_name,
        s.day_of_week,
        s.time_slot,
        s.week_type,
        ARRAY_AGG(s.id) as schedule_ids,
        COUNT(*) as conflicts_count
    FROM schedules s
    WHERE 
        s.semester = p_semester
        AND s.academic_year = p_academic_year
        AND s.is_active = true
    GROUP BY 
        s.teacher_id, 
        s.teacher_name, 
        s.day_of_week, 
        s.time_slot, 
        s.week_type
    HAVING COUNT(*) > 1;
    
    -- Конфликты групп
    RETURN QUERY
    SELECT 
        'group'::VARCHAR,
        s.group_id,
        s.group_name,
        s.day_of_week,
        s.time_slot,
        s.week_type,
        ARRAY_AGG(s.id),
        COUNT(*)
    FROM schedules s
    WHERE 
        s.semester = p_semester
        AND s.academic_year = p_academic_year
        AND s.is_active = true
    GROUP BY 
        s.group_id, 
        s.group_name, 
        s.day_of_week, 
        s.time_slot, 
        s.week_type
    HAVING COUNT(*) > 1;
    
    -- Конфликты аудиторий
    RETURN QUERY
    SELECT 
        'classroom'::VARCHAR,
        s.classroom_id,
        s.classroom_name,
        s.day_of_week,
        s.time_slot,
        s.week_type,
        ARRAY_AGG(s.id),
        COUNT(*)
    FROM schedules s
    WHERE 
        s.semester = p_semester
        AND s.academic_year = p_academic_year
        AND s.is_active = true
        AND s.classroom_id IS NOT NULL
    GROUP BY 
        s.classroom_id, 
        s.classroom_name, 
        s.day_of_week, 
        s.time_slot, 
        s.week_type
    HAVING COUNT(*) > 1;
END;
$$ LANGUAGE plpgsql;

-- ============ ФУНКЦИЯ ДЛЯ АВТОМАТИЧЕСКОЙ ЗАПИСИ КОНФЛИКТОВ ============

CREATE OR REPLACE FUNCTION update_conflicts_table(
    p_semester INTEGER,
    p_academic_year VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    v_conflict RECORD;
    v_inserted_count INTEGER := 0;
BEGIN
    -- Удалить старые активные конфликты для этого семестра
    UPDATE schedule_conflicts
    SET status = 'resolved',
        resolution = 'Auto-resolved: no longer detected',
        resolved_at = NOW()
    WHERE 
        semester = p_semester
        AND academic_year = p_academic_year
        AND status = 'active';
    
    -- Вставить новые конфликты
    FOR v_conflict IN 
        SELECT * FROM detect_schedule_conflicts(p_semester, p_academic_year)
    LOOP
        INSERT INTO schedule_conflicts (
            conflict_type,
            entity_id,
            entity_name,
            day_of_week,
            time_slot,
            week_type,
            schedule_ids,
            semester,
            academic_year,
            severity
        ) VALUES (
            v_conflict.conflict_type,
            v_conflict.entity_id,
            v_conflict.entity_name,
            v_conflict.day_of_week,
            v_conflict.time_slot,
            v_conflict.week_type,
            v_conflict.schedule_ids,
            p_semester,
            p_academic_year,
            CASE 
                WHEN v_conflict.conflicts_count > 2 THEN 'critical'
                WHEN v_conflict.conflicts_count > 1 THEN 'high'
                ELSE 'medium'
            END
        );
        
        v_inserted_count := v_inserted_count + 1;
    END LOOP;
    
    RETURN v_inserted_count;
END;
$$ LANGUAGE plpgsql;

-- ============ КОММЕНТАРИИ ============

COMMENT ON TABLE schedule_conflicts IS 'Обнаруженные конфликты в расписании';
COMMENT ON COLUMN schedule_conflicts.conflict_type IS 'teacher=преподаватель в двух местах, group=группа в двух местах, classroom=аудитория занята';
COMMENT ON COLUMN schedule_conflicts.schedule_ids IS 'Массив ID занятий которые конфликтуют';
COMMENT ON FUNCTION detect_schedule_conflicts IS 'Обнаружить все конфликты в расписании';
COMMENT ON FUNCTION update_conflicts_table IS 'Обновить таблицу конфликтов (пересканировать)';
