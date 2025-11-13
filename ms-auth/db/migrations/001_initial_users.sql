-- ============================================
-- INITIAL SCHEMA: Users and Roles
-- Version: 001
-- ============================================

-- ============ ROLES TABLE ============

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    
    -- Права (JSONB для гибкости)
    permissions JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Базовые роли
INSERT INTO roles (name, code, description, permissions) VALUES
('Студент', 'STUDENT', 'Студент университета', '{"can_view_schedule": true, "can_report_issues": false}'),
('Преподаватель', 'TEACHER', 'Преподаватель', '{"can_view_schedule": true, "can_set_preferences": true, "can_report_issues": true}'),
('Сотрудник', 'STAFF', 'Сотрудник учебного отдела', '{"can_manage_classrooms": true, "can_generate_schedule": true, "can_manage_users": true, "can_view_all": true}'),
('Администратор', 'ADMIN', 'Системный администратор', '{"full_access": true}')
ON CONFLICT (code) DO NOTHING;

-- ============ USERS TABLE ============

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    
    -- Учётные данные
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Персональная информация
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    
    -- Роль по умолчанию
    primary_role VARCHAR(20) NOT NULL,
    
    -- Привязки к сущностям
    teacher_id INTEGER,
    staff_id INTEGER,
    student_group_id INTEGER,
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP,
    
    -- Безопасность
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(45),
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_primary_role CHECK (primary_role IN ('student', 'teacher', 'staff', 'admin'))
);

-- Индексы для users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_primary_role ON users(primary_role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_teacher_id ON users(teacher_id) WHERE teacher_id IS NOT NULL;

-- ============ USER_ROLES TABLE (Связь многие-ко-многим) ============

CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    
    granted_at TIMESTAMP DEFAULT NOW(),
    granted_by INTEGER REFERENCES users(id),
    
    CONSTRAINT unique_user_role UNIQUE(user_id, role_id)
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id);

-- ============ LOGIN HISTORY TABLE ============

CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    username VARCHAR(50),
    success BOOLEAN NOT NULL,
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    failure_reason VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_history_user ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_created ON login_history(created_at);
CREATE INDEX IF NOT EXISTS idx_login_history_success ON login_history(success, created_at);

-- ============ TRIGGERS ============

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============ COMMENTS ============

COMMENT ON TABLE users IS 'Пользователи системы';
COMMENT ON TABLE roles IS 'Роли и права';
COMMENT ON TABLE user_roles IS 'Связь пользователей и ролей';
COMMENT ON TABLE login_history IS 'История входов в систему';

COMMENT ON COLUMN users.primary_role IS 'Основная роль: student, teacher, staff, admin';
COMMENT ON COLUMN users.failed_login_attempts IS 'Счетчик неудачных попыток входа';
COMMENT ON COLUMN users.locked_until IS 'Время блокировки аккаунта';

