-- LMS: Курсы, модули, материалы, прогресс

-- Курсы
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    code VARCHAR(50) UNIQUE,
    teacher_id INTEGER,
    teacher_name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    enrolled_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Модули курса
CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Материалы модуля
CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('file', 'link', 'text', 'video')),
    content TEXT,
    file_path VARCHAR(500),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Записи студентов на курсы
CREATE TABLE IF NOT EXISTS course_enrollments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_id, student_id)
);

-- Прогресс студента
CREATE TABLE IF NOT EXISTS student_progress (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    progress_percentage FLOAT DEFAULT 0.0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id, module_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_modules_course_id ON modules(course_id);
CREATE INDEX IF NOT EXISTS idx_materials_module_id ON materials(module_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON course_enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_student_id ON student_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_course_id ON student_progress(course_id);

-- Триггер для обновления enrolled_count
CREATE OR REPLACE FUNCTION update_course_enrolled_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE courses SET enrolled_count = enrolled_count + 1 WHERE id = NEW.course_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE courses SET enrolled_count = enrolled_count - 1 WHERE id = OLD.course_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_enrolled_count
    AFTER INSERT OR DELETE ON course_enrollments
    FOR EACH ROW EXECUTE FUNCTION update_course_enrolled_count();

