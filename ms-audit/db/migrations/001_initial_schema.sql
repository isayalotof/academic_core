-- ============================================
-- INITIAL SCHEMA: Buildings and Classrooms
-- Version: 001
-- ============================================

-- ============ BUILDINGS TABLE ============

CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(20),
    code VARCHAR(20) UNIQUE NOT NULL,
    
    address TEXT,
    campus VARCHAR(100),
    
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    
    total_floors INTEGER,
    has_elevator BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for buildings
CREATE INDEX IF NOT EXISTS idx_buildings_code ON buildings(code);
CREATE INDEX IF NOT EXISTS idx_buildings_campus ON buildings(campus);

-- ============ CLASSROOMS TABLE ============

CREATE TABLE IF NOT EXISTS classrooms (
    id SERIAL PRIMARY KEY,
    
    -- Идентификация
    name VARCHAR(50) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    
    -- Привязка к зданию
    building_id INTEGER NOT NULL REFERENCES buildings(id) ON DELETE RESTRICT,
    floor INTEGER NOT NULL,
    wing VARCHAR(50),
    
    -- Характеристики
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    actual_area DECIMAL(6,2),
    
    -- Тип аудитории
    classroom_type VARCHAR(50) NOT NULL,
    
    -- Оборудование
    has_projector BOOLEAN DEFAULT false,
    has_whiteboard BOOLEAN DEFAULT false,
    has_blackboard BOOLEAN DEFAULT false,
    has_markers BOOLEAN DEFAULT false,
    has_chalk BOOLEAN DEFAULT false,
    has_computers BOOLEAN DEFAULT false,
    computers_count INTEGER DEFAULT 0,
    has_audio_system BOOLEAN DEFAULT false,
    has_video_recording BOOLEAN DEFAULT false,
    has_air_conditioning BOOLEAN DEFAULT false,
    
    -- Особенности
    is_accessible BOOLEAN DEFAULT true,
    has_windows BOOLEAN DEFAULT true,
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    
    -- Примечания
    description TEXT,
    notes TEXT,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER
);

-- Indexes for classrooms
CREATE INDEX IF NOT EXISTS idx_classrooms_building ON classrooms(building_id);
CREATE INDEX IF NOT EXISTS idx_classrooms_type ON classrooms(classroom_type);
CREATE INDEX IF NOT EXISTS idx_classrooms_capacity ON classrooms(capacity);
CREATE INDEX IF NOT EXISTS idx_classrooms_active ON classrooms(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_classrooms_code ON classrooms(code);
CREATE INDEX IF NOT EXISTS idx_classrooms_equipment ON classrooms(has_projector, has_computers, has_whiteboard) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_classrooms_floor ON classrooms(building_id, floor);

-- ============ CLASSROOM SCHEDULES TABLE ============

CREATE TABLE IF NOT EXISTS classroom_schedules (
    id SERIAL PRIMARY KEY,
    classroom_id INTEGER NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    
    -- Временной слот
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),
    time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 1 AND 6),
    
    -- Связь с основным расписанием
    schedule_id INTEGER,
    
    -- Информация о занятии (денормализация)
    discipline_name VARCHAR(200),
    teacher_name VARCHAR(200),
    group_name VARCHAR(100),
    lesson_type VARCHAR(50),
    
    -- Статус
    status VARCHAR(20) DEFAULT 'occupied',
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- UNIQUE: аудитория не может быть занята дважды в одно время
    CONSTRAINT unique_classroom_time UNIQUE(classroom_id, day_of_week, time_slot)
);

-- Indexes for classroom_schedules
CREATE INDEX IF NOT EXISTS idx_classroom_schedules_classroom ON classroom_schedules(classroom_id);
CREATE INDEX IF NOT EXISTS idx_classroom_schedules_time ON classroom_schedules(day_of_week, time_slot);
CREATE INDEX IF NOT EXISTS idx_classroom_schedules_status ON classroom_schedules(status);
CREATE INDEX IF NOT EXISTS idx_classroom_schedules_schedule_id ON classroom_schedules(schedule_id);

-- ============ CLASSROOM DISTANCES TABLE ============

CREATE TABLE IF NOT EXISTS classroom_distances (
    id SERIAL PRIMARY KEY,
    from_classroom_id INTEGER NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    to_classroom_id INTEGER NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    
    distance_meters INTEGER NOT NULL,
    walking_time_seconds INTEGER NOT NULL,
    
    requires_building_change BOOLEAN DEFAULT false,
    requires_floor_change BOOLEAN DEFAULT false,
    
    calculated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_classroom_pair UNIQUE(from_classroom_id, to_classroom_id),
    CONSTRAINT no_self_distance CHECK (from_classroom_id != to_classroom_id)
);

-- Indexes for classroom_distances
CREATE INDEX IF NOT EXISTS idx_distances_from ON classroom_distances(from_classroom_id);
CREATE INDEX IF NOT EXISTS idx_distances_to ON classroom_distances(to_classroom_id);

-- ============ TRIGGERS ============

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop triggers if they exist before creating
DROP TRIGGER IF EXISTS update_buildings_updated_at ON buildings;
CREATE TRIGGER update_buildings_updated_at BEFORE UPDATE ON buildings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_classrooms_updated_at ON classrooms;
CREATE TRIGGER update_classrooms_updated_at BEFORE UPDATE ON classrooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============ COMMENTS ============

COMMENT ON TABLE buildings IS 'Здания университета';
COMMENT ON TABLE classrooms IS 'Аудитории';
COMMENT ON TABLE classroom_schedules IS 'Расписание занятости аудиторий';
COMMENT ON TABLE classroom_distances IS 'Предрассчитанные расстояния между аудиториями';

COMMENT ON COLUMN classrooms.classroom_type IS 'Типы: LECTURE, SEMINAR, COMPUTER_LAB, etc';
COMMENT ON COLUMN classroom_schedules.day_of_week IS '1=Понедельник, 6=Суббота';
COMMENT ON COLUMN classroom_schedules.time_slot IS 'Номер пары (1-6)';

