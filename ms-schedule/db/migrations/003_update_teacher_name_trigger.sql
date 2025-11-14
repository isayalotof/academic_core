-- ============================================
-- MIGRATION 003: TRIGGER TO UPDATE TEACHER_NAME IN SCHEDULES
-- ============================================
-- Автоматическое обновление teacher_name в расписании при изменении full_name преподавателя

-- Создаем функцию для обновления teacher_name в расписании
CREATE OR REPLACE FUNCTION update_schedules_teacher_name()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновляем teacher_name в таблице schedules, если изменилось full_name преподавателя
    IF OLD.full_name IS DISTINCT FROM NEW.full_name THEN
        UPDATE schedules
        SET teacher_name = NEW.full_name,
            updated_at = NOW()
        WHERE teacher_id = NEW.id;
        
        RAISE NOTICE 'Updated teacher_name in schedules for teacher_id=%, new_name=%', NEW.id, NEW.full_name;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создаем триггер на таблице teachers
CREATE TRIGGER trigger_update_schedules_teacher_name
    AFTER UPDATE OF full_name ON teachers
    FOR EACH ROW
    WHEN (OLD.full_name IS DISTINCT FROM NEW.full_name)
    EXECUTE FUNCTION update_schedules_teacher_name();

-- Комментарий
COMMENT ON FUNCTION update_schedules_teacher_name() IS 'Автоматически обновляет teacher_name в таблице schedules при изменении full_name преподавателя';

