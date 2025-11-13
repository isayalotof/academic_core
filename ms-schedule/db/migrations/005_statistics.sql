-- ============================================
-- MIGRATION 005: SCHEDULE STATISTICS
-- ============================================
-- Статистика использования расписания

CREATE TABLE IF NOT EXISTS schedule_statistics (
    id SERIAL PRIMARY KEY,
    
    -- Период
    date DATE NOT NULL,
    semester INTEGER,
    academic_year VARCHAR(20),
    
    -- Метрики
    total_lessons INTEGER DEFAULT 0,
    total_hours INTEGER DEFAULT 0,
    
    -- По типам занятий
    lecture_count INTEGER DEFAULT 0,
    practice_count INTEGER DEFAULT 0,
    lab_count INTEGER DEFAULT 0,
    other_count INTEGER DEFAULT 0,
    
    -- По дням недели (JSON для гибкости)
    lessons_per_day JSONB DEFAULT '{}',       -- {"1": 120, "2": 115, ...}
    lessons_per_time_slot JSONB DEFAULT '{}', -- {"1": 100, "2": 105, ...}
    
    -- Загрузка
    teacher_utilization JSONB DEFAULT '{}',   -- {teacher_id: percentage}
    classroom_utilization JSONB DEFAULT '{}', -- {classroom_id: percentage}
    group_utilization JSONB DEFAULT '{}',     -- {group_id: hours_per_week}
    
    -- Качество
    avg_fitness_score DECIMAL(10,2),
    conflicts_count INTEGER DEFAULT 0,
    preference_satisfaction DECIMAL(5,2),      -- %
    
    -- Метаданные
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- ============ ИНДЕКСЫ ============

CREATE UNIQUE INDEX idx_stats_date ON schedule_statistics(date, semester, academic_year);

CREATE INDEX idx_stats_semester ON schedule_statistics(semester, academic_year);

CREATE INDEX idx_stats_calculated ON schedule_statistics(calculated_at DESC);

-- GIN индексы для JSONB
CREATE INDEX idx_stats_teacher_util ON schedule_statistics USING gin(teacher_utilization);
CREATE INDEX idx_stats_classroom_util ON schedule_statistics USING gin(classroom_utilization);

-- ============ ФУНКЦИЯ ДЛЯ РАСЧЁТА СТАТИСТИКИ ============

CREATE OR REPLACE FUNCTION calculate_schedule_statistics(
    p_semester INTEGER,
    p_academic_year VARCHAR,
    p_date DATE DEFAULT CURRENT_DATE
) RETURNS INTEGER AS $$
DECLARE
    v_stats_id INTEGER;
    v_total_lessons INTEGER;
    v_total_hours INTEGER;
    v_lecture_count INTEGER;
    v_practice_count INTEGER;
    v_lab_count INTEGER;
    v_lessons_per_day JSONB;
    v_conflicts_count INTEGER;
BEGIN
    -- Подсчитать основные метрики
    SELECT 
        COUNT(*),
        COUNT(*) * 2,  -- Каждая пара = 2 академических часа
        COUNT(*) FILTER (WHERE lesson_type ILIKE '%лекц%'),
        COUNT(*) FILTER (WHERE lesson_type ILIKE '%практ%' OR lesson_type ILIKE '%семинар%'),
        COUNT(*) FILTER (WHERE lesson_type ILIKE '%лаб%')
    INTO 
        v_total_lessons,
        v_total_hours,
        v_lecture_count,
        v_practice_count,
        v_lab_count
    FROM schedules
    WHERE 
        semester = p_semester
        AND academic_year = p_academic_year
        AND is_active = true;
    
    -- Подсчитать занятия по дням недели
    SELECT jsonb_object_agg(day_of_week::text, lesson_count)
    INTO v_lessons_per_day
    FROM (
        SELECT 
            day_of_week,
            COUNT(*) as lesson_count
        FROM schedules
        WHERE 
            semester = p_semester
            AND academic_year = p_academic_year
            AND is_active = true
        GROUP BY day_of_week
    ) day_stats;
    
    -- Подсчитать активные конфликты
    SELECT COUNT(*)
    INTO v_conflicts_count
    FROM schedule_conflicts
    WHERE 
        semester = p_semester
        AND academic_year = p_academic_year
        AND status = 'active';
    
    -- Вставить или обновить статистику
    INSERT INTO schedule_statistics (
        date,
        semester,
        academic_year,
        total_lessons,
        total_hours,
        lecture_count,
        practice_count,
        lab_count,
        lessons_per_day,
        conflicts_count
    ) VALUES (
        p_date,
        p_semester,
        p_academic_year,
        v_total_lessons,
        v_total_hours,
        v_lecture_count,
        v_practice_count,
        v_lab_count,
        v_lessons_per_day,
        v_conflicts_count
    )
    ON CONFLICT (date, semester, academic_year)
    DO UPDATE SET
        total_lessons = EXCLUDED.total_lessons,
        total_hours = EXCLUDED.total_hours,
        lecture_count = EXCLUDED.lecture_count,
        practice_count = EXCLUDED.practice_count,
        lab_count = EXCLUDED.lab_count,
        lessons_per_day = EXCLUDED.lessons_per_day,
        conflicts_count = EXCLUDED.conflicts_count,
        calculated_at = NOW()
    RETURNING id INTO v_stats_id;
    
    RETURN v_stats_id;
END;
$$ LANGUAGE plpgsql;

-- ============ ПРЕДСТАВЛЕНИЕ ДЛЯ БЫСТРОГО ДОСТУПА К СТАТИСТИКЕ ============

CREATE OR REPLACE VIEW v_current_semester_stats AS
SELECT 
    s.semester,
    s.academic_year,
    COUNT(DISTINCT s.teacher_id) as total_teachers,
    COUNT(DISTINCT s.group_id) as total_groups,
    COUNT(DISTINCT s.classroom_id) as total_classrooms,
    COUNT(*) as total_lessons,
    COUNT(*) * 2 as total_hours,
    COUNT(*) FILTER (WHERE s.lesson_type ILIKE '%лекц%') as lectures,
    COUNT(*) FILTER (WHERE s.lesson_type ILIKE '%практ%') as practices,
    COUNT(*) FILTER (WHERE s.lesson_type ILIKE '%лаб%') as labs,
    ROUND(AVG(CASE 
        WHEN s.classroom_id IS NOT NULL THEN 100.0 
        ELSE 0.0 
    END), 2) as classroom_assignment_rate,
    (SELECT COUNT(*) FROM schedule_conflicts c 
     WHERE c.semester = s.semester 
       AND c.academic_year = s.academic_year 
       AND c.status = 'active') as active_conflicts
FROM schedules s
WHERE s.is_active = true
GROUP BY s.semester, s.academic_year;

-- ============ КОММЕНТАРИИ ============

COMMENT ON TABLE schedule_statistics IS 'Агрегированная статистика расписания';
COMMENT ON COLUMN schedule_statistics.lessons_per_day IS 'JSON: количество занятий по дням недели';
COMMENT ON COLUMN schedule_statistics.teacher_utilization IS 'JSON: процент загрузки преподавателей';
COMMENT ON FUNCTION calculate_schedule_statistics IS 'Рассчитать статистику за день/семестр';
COMMENT ON VIEW v_current_semester_stats IS 'Представление с текущей статистикой по всем семестрам';

