-- Таблица студентов

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    
    -- Основная информация
    full_name VARCHAR(200) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_name VARCHAR(100),
    
    -- Студенческий билет
    student_number VARCHAR(50) UNIQUE NOT NULL, -- "11904124"
    
    -- Группа
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE RESTRICT,
    
    -- Контакты
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    
    -- Связь с пользователем
    user_id INTEGER UNIQUE,                     -- Ссылка на users (ms-auth)
    
    -- Статус
    status VARCHAR(20) DEFAULT 'active',        -- 'active', 'academic_leave', 'expelled', 'graduated'
    enrollment_date DATE,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_status CHECK (
        status IN ('active', 'academic_leave', 'expelled', 'graduated')
    )
);

-- Индексы
CREATE INDEX idx_students_name ON students(full_name);
CREATE INDEX idx_students_number ON students(student_number);
CREATE INDEX idx_students_group ON students(group_id);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_user ON students(user_id);
CREATE INDEX idx_students_status ON students(status);

-- Полнотекстовый поиск
CREATE INDEX idx_students_search ON students USING gin(to_tsvector('russian',
    coalesce(full_name, '') || ' ' || 
    coalesce(student_number, '') || ' ' || 
    coalesce(email, '')
));

-- Триггер для updated_at
CREATE OR REPLACE FUNCTION update_students_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER students_updated_at_trigger
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_students_updated_at();

-- ⭐ ТРИГГЕР ДЛЯ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ РАЗМЕРА ГРУППЫ
CREATE OR REPLACE FUNCTION update_group_size()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE groups 
        SET size = (
            SELECT COUNT(*) 
            FROM students 
            WHERE group_id = NEW.group_id AND status = 'active'
        )
        WHERE id = NEW.group_id;
    END IF;
    
    IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
        UPDATE groups 
        SET size = (
            SELECT COUNT(*) 
            FROM students 
            WHERE group_id = OLD.group_id AND status = 'active'
        )
        WHERE id = OLD.group_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_group_size
    AFTER INSERT OR UPDATE OR DELETE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_group_size();

-- Комментарии
COMMENT ON TABLE students IS 'Студенты университета';
COMMENT ON COLUMN students.status IS 'Статус: active=обучается, academic_leave=академический отпуск, expelled=отчислен, graduated=выпускник';
COMMENT ON TRIGGER trigger_update_group_size ON students IS 'Автоматическое обновление размера группы при изменении студентов';

