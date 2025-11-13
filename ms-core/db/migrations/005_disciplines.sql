-- Справочник дисциплин

CREATE TABLE IF NOT EXISTS disciplines (
    id SERIAL PRIMARY KEY,
    
    -- Основная информация
    name VARCHAR(200) NOT NULL,
    short_name VARCHAR(100),
    code VARCHAR(50) UNIQUE,                   -- "Б1.О.12"
    
    -- Параметры
    department VARCHAR(200),                   -- Кафедра
    credit_units INTEGER,                      -- Зачётные единицы
    
    -- Тип
    discipline_type VARCHAR(50),               -- 'core', 'elective', 'optional'
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_discipline_type CHECK (
        discipline_type IN ('core', 'elective', 'optional') OR discipline_type IS NULL
    )
);

-- Индексы
CREATE INDEX idx_disciplines_name ON disciplines(name);
CREATE INDEX idx_disciplines_code ON disciplines(code);
CREATE INDEX idx_disciplines_active ON disciplines(is_active) WHERE is_active = true;
CREATE INDEX idx_disciplines_department ON disciplines(department);
CREATE INDEX idx_disciplines_type ON disciplines(discipline_type);

-- Полнотекстовый поиск
CREATE INDEX idx_disciplines_search ON disciplines USING gin(to_tsvector('russian',
    coalesce(name, '') || ' ' || 
    coalesce(short_name, '') || ' ' || 
    coalesce(code, '')
));

-- Триггер для updated_at
CREATE OR REPLACE FUNCTION update_disciplines_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER disciplines_updated_at_trigger
    BEFORE UPDATE ON disciplines
    FOR EACH ROW
    EXECUTE FUNCTION update_disciplines_updated_at();

-- Комментарии
COMMENT ON TABLE disciplines IS 'Справочник дисциплин';
COMMENT ON COLUMN disciplines.code IS 'Код дисциплины по учебному плану (например: Б1.О.12)';
COMMENT ON COLUMN disciplines.discipline_type IS 'Тип: core=базовая, elective=по выбору, optional=факультатив';

