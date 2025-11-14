-- ============================================
-- MIGRATION 002: SCHEDULE HISTORY
-- ============================================
-- История изменений расписания

CREATE TABLE IF NOT EXISTS schedule_history (
    id SERIAL PRIMARY KEY,
    
    -- Связь с расписанием
    schedule_id INTEGER,                       -- Может быть NULL если запись удалена
    
    -- Тип изменения
    change_type VARCHAR(20) NOT NULL,          -- 'created', 'updated', 'deleted', 'moved', 'replaced'
    
    -- Старые значения (для update/delete)
    old_values JSONB,
    
    -- Новые значения (для create/update)
    new_values JSONB,
    
    -- Контекст изменения
    change_reason VARCHAR(200),                -- "Оптимизация агентом", "Ручное изменение"
    generation_id INTEGER,                     -- Если изменение из ms-agent
    
    -- Кто изменил
    changed_by INTEGER,
    changed_by_name VARCHAR(200),
    
    -- Когда
    changed_at TIMESTAMP DEFAULT NOW(),
    
    -- Метаданные
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Индекс для FK (опциональный, т.к. schedule может быть удалён)
    CONSTRAINT fk_schedule_history_schedule 
        FOREIGN KEY (schedule_id) 
        REFERENCES schedules(id) 
        ON DELETE SET NULL
);

-- ============ ИНДЕКСЫ ============

CREATE INDEX idx_schedule_history_schedule ON schedule_history(schedule_id) 
    WHERE schedule_id IS NOT NULL;

CREATE INDEX idx_schedule_history_type ON schedule_history(change_type);

CREATE INDEX idx_schedule_history_date ON schedule_history(changed_at DESC);

CREATE INDEX idx_schedule_history_user ON schedule_history(changed_by) 
    WHERE changed_by IS NOT NULL;

CREATE INDEX idx_schedule_history_generation ON schedule_history(generation_id) 
    WHERE generation_id IS NOT NULL;

-- Индекс для поиска изменений за период
CREATE INDEX idx_schedule_history_period ON schedule_history(changed_at, change_type);

-- ============ ФУНКЦИЯ ДЛЯ АВТОМАТИЧЕСКОГО ЛОГИРОВАНИЯ ============

CREATE OR REPLACE FUNCTION log_schedule_change()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO schedule_history (
            schedule_id,
            change_type,
            old_values,
            changed_at
        ) VALUES (
            NULL,  -- schedule_id = NULL, т.к. запись уже удалена из schedules
            'deleted',
            to_jsonb(OLD),
            NOW()
        );
        RETURN OLD;
        
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO schedule_history (
            schedule_id,
            change_type,
            old_values,
            new_values,
            changed_by,
            changed_at
        ) VALUES (
            NEW.id,
            'updated',
            to_jsonb(OLD),
            to_jsonb(NEW),
            NEW.updated_by,
            NOW()
        );
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO schedule_history (
            schedule_id,
            change_type,
            new_values,
            changed_by,
            generation_id,
            changed_at
        ) VALUES (
            NEW.id,
            'created',
            to_jsonb(NEW),
            NEW.created_by,
            NEW.generation_id,
            NOW()
        );
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического логирования
CREATE TRIGGER schedule_change_log
    AFTER INSERT OR UPDATE OR DELETE ON schedules
    FOR EACH ROW
    EXECUTE FUNCTION log_schedule_change();

-- ============ КОММЕНТАРИИ ============

COMMENT ON TABLE schedule_history IS 'История всех изменений расписания (полный аудит)';
COMMENT ON COLUMN schedule_history.old_values IS 'JSON со старыми значениями (до изменения)';
COMMENT ON COLUMN schedule_history.new_values IS 'JSON с новыми значениями (после изменения)';
COMMENT ON COLUMN schedule_history.change_type IS 'created/updated/deleted/moved/replaced';

