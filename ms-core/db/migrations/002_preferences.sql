-- ⭐ ПРЕДПОЧТЕНИЯ ПРЕПОДАВАТЕЛЕЙ - KEY FEATURE!
-- Критично для LLM-агента и fitness-функции!

CREATE TABLE IF NOT EXISTS teacher_preferences (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    
    -- Временной слот
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),  -- 1=Пн, 6=Сб
    time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 1 AND 6),      -- Номер пары
    
    -- Предпочтение
    is_preferred BOOLEAN NOT NULL,             -- true = удобно, false = неудобно
    
    -- Дополнительная информация
    preference_strength VARCHAR(20),           -- 'strong', 'medium', 'weak'
    reason TEXT,                               -- Причина (опционально)
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Уникальность: один слот - одно предпочтение
    CONSTRAINT unique_teacher_slot UNIQUE(teacher_id, day_of_week, time_slot)
);

-- Индексы
CREATE INDEX idx_preferences_teacher ON teacher_preferences(teacher_id);
CREATE INDEX idx_preferences_slot ON teacher_preferences(day_of_week, time_slot);
CREATE INDEX idx_preferences_preferred ON teacher_preferences(is_preferred) WHERE is_preferred = true;
CREATE INDEX idx_preferences_teacher_day ON teacher_preferences(teacher_id, day_of_week);

-- Триггер для updated_at
CREATE OR REPLACE FUNCTION update_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER preferences_updated_at_trigger
    BEFORE UPDATE ON teacher_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_preferences_updated_at();

-- Комментарии для документации
COMMENT ON TABLE teacher_preferences IS '⭐ Предпочтения преподавателей по временным слотам - ключевая фича для LLM-агента и fitness-функции!';
COMMENT ON COLUMN teacher_preferences.day_of_week IS '1=Понедельник, 2=Вторник, 3=Среда, 4=Четверг, 5=Пятница, 6=Суббота';
COMMENT ON COLUMN teacher_preferences.time_slot IS 'Номер пары (1-6)';
COMMENT ON COLUMN teacher_preferences.is_preferred IS 'true = удобное время для преподавателя, false = неудобное время';
COMMENT ON COLUMN teacher_preferences.preference_strength IS 'Сила предпочтения: strong=обязательно учитывать, medium=желательно, weak=по возможности';

-- Пример использования (для документации):
-- INSERT INTO teacher_preferences (teacher_id, day_of_week, time_slot, is_preferred, preference_strength)
-- VALUES 
--     (1, 2, 2, true, 'strong'),   -- Вторник, 2 пара - удобно (обязательно)
--     (1, 2, 3, true, 'medium'),   -- Вторник, 3 пара - удобно (желательно)
--     (1, 6, 5, false, 'strong');  -- Суббота, 5 пара - неудобно (критично избегать)

