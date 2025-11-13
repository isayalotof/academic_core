-- ============================================
-- ADDITIONAL INDEXES FOR PERFORMANCE
-- Version: 002
-- ============================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_classrooms_search ON classrooms(building_id, classroom_type, capacity) WHERE is_active = true;

-- Full-text search on classroom name
CREATE INDEX IF NOT EXISTS idx_classrooms_name_trgm ON classrooms USING gin(name gin_trgm_ops);

-- Enable pg_trgm extension for fuzzy search (if not already enabled)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Index for schedule availability queries
CREATE INDEX IF NOT EXISTS idx_schedules_availability ON classroom_schedules(day_of_week, time_slot, status);

-- Partial index for reserved slots
CREATE INDEX IF NOT EXISTS idx_schedules_reserved ON classroom_schedules(classroom_id, day_of_week, time_slot) 
    WHERE status = 'reserved';

