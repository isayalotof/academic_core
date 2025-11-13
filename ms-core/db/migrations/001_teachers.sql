-- Таблица преподавателей
-- Приоритеты (1-4) вычисляются АВТОМАТИЧЕСКИ из employment_type

CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    
    -- Основная информация
    full_name VARCHAR(200) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_name VARCHAR(100),
    
    -- Контакты
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    
    -- Категория занятости (КРИТИЧНО ДЛЯ ПРИОРИТЕТОВ!)
    employment_type VARCHAR(50) NOT NULL,       -- 'external', 'graduate', 'internal', 'staff'
    priority INTEGER NOT NULL,                  -- 1-4 (вычисляется автоматически)
    
    -- Должность
    position VARCHAR(100),                      -- "Доцент", "Профессор", "Старший преподаватель"
    academic_degree VARCHAR(100),               -- "Кандидат наук", "Доктор наук"
    department VARCHAR(200),                    -- Кафедра
    
    -- Связь с пользователем
    user_id INTEGER UNIQUE,                     -- Ссылка на users (ms-auth)
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    hire_date DATE,
    termination_date DATE,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER,
    
    -- Constraints
    CONSTRAINT valid_employment_type CHECK (
        employment_type IN ('external', 'graduate', 'internal', 'staff')
    ),
    CONSTRAINT valid_priority CHECK (priority BETWEEN 1 AND 4)
);

-- Индексы
CREATE INDEX idx_teachers_name ON teachers(full_name);
CREATE INDEX idx_teachers_email ON teachers(email);
CREATE INDEX idx_teachers_priority ON teachers(priority);
CREATE INDEX idx_teachers_employment ON teachers(employment_type);
CREATE INDEX idx_teachers_active ON teachers(is_active) WHERE is_active = true;
CREATE INDEX idx_teachers_user ON teachers(user_id);
CREATE INDEX idx_teachers_department ON teachers(department);

-- Полнотекстовый поиск
CREATE INDEX idx_teachers_search ON teachers USING gin(to_tsvector('russian',
    coalesce(full_name, '') || ' ' || 
    coalesce(email, '') || ' ' || 
    coalesce(department, '')
));

-- ⭐ ТРИГГЕР ДЛЯ АВТОМАТИЧЕСКОГО РАСЧЁТА ПРИОРИТЕТА
-- Это ключевая логика для fitness-функции!
CREATE OR REPLACE FUNCTION calculate_teacher_priority()
RETURNS TRIGGER AS $$
BEGIN
    NEW.priority := CASE NEW.employment_type
        WHEN 'external' THEN 1    -- Внешний совместитель (ВЫСШИЙ ПРИОРИТЕТ)
        WHEN 'graduate' THEN 2    -- Магистрант-преподаватель
        WHEN 'internal' THEN 3    -- Внутренний совместитель
        WHEN 'staff' THEN 4       -- Штатный (низший приоритет)
        ELSE 4
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_priority
    BEFORE INSERT OR UPDATE OF employment_type ON teachers
    FOR EACH ROW
    EXECUTE FUNCTION calculate_teacher_priority();

-- Триггер для updated_at
CREATE OR REPLACE FUNCTION update_teachers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER teachers_updated_at_trigger
    BEFORE UPDATE ON teachers
    FOR EACH ROW
    EXECUTE FUNCTION update_teachers_updated_at();

-- Комментарии
COMMENT ON TABLE teachers IS 'Преподаватели университета';
COMMENT ON COLUMN teachers.employment_type IS 'Тип занятости: external=внешние совместители (приоритет 1), graduate=магистранты, internal=внутренние совместители, staff=штатные (приоритет 4)';
COMMENT ON COLUMN teachers.priority IS 'Приоритет для fitness-функции (1-4), вычисляется автоматически';
COMMENT ON TRIGGER trigger_calculate_priority ON teachers IS 'Автоматический расчёт приоритета из employment_type';


