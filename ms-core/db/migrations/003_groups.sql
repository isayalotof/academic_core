-- Таблица групп студентов

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    
    -- Основная информация
    name VARCHAR(100) NOT NULL UNIQUE,         -- "Б9124-09.03.03пикд", "М9124-09.04.01пикд"
    short_name VARCHAR(50),                    -- "Б9124", "М9124"
    
    -- Параметры
    year INTEGER NOT NULL,                     -- Год поступления (2024)
    semester INTEGER,                          -- Текущий семестр (1-8)
    size INTEGER DEFAULT 0,                    -- Количество студентов (автоматически)
    
    -- Образовательная программа
    program_code VARCHAR(50),                  -- "09.03.03"
    program_name VARCHAR(200),                 -- "Прикладная информатика"
    specialization VARCHAR(200),               -- "ПИвКД"
    level VARCHAR(20),                         -- 'bachelor', 'master', 'postgraduate'
    
    -- Куратор (опционально)
    curator_teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    enrollment_date DATE,
    graduation_date DATE,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_level CHECK (level IN ('bachelor', 'master', 'postgraduate'))
);

-- Индексы
CREATE INDEX idx_groups_name ON groups(name);
CREATE INDEX idx_groups_short_name ON groups(short_name);
CREATE INDEX idx_groups_year ON groups(year);
CREATE INDEX idx_groups_active ON groups(is_active) WHERE is_active = true;
CREATE INDEX idx_groups_level ON groups(level);
CREATE INDEX idx_groups_curator ON groups(curator_teacher_id);
CREATE INDEX idx_groups_year_semester ON groups(year, semester);

-- Триггер для updated_at
CREATE OR REPLACE FUNCTION update_groups_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER groups_updated_at_trigger
    BEFORE UPDATE ON groups
    FOR EACH ROW
    EXECUTE FUNCTION update_groups_updated_at();

-- Комментарии
COMMENT ON TABLE groups IS 'Учебные группы студентов';
COMMENT ON COLUMN groups.name IS 'Полное название группы (например: Б9124-09.03.03пикд)';
COMMENT ON COLUMN groups.size IS 'Количество активных студентов (обновляется автоматически триггером)';
COMMENT ON COLUMN groups.level IS 'Уровень образования: bachelor=бакалавриат, master=магистратура, postgraduate=аспирантура';

