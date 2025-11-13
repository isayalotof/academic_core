-- Миграция: Разрешить NULL для teacher_id и group_id в course_loads
-- Дата: 2024
-- 
-- Проблема: teacher_id и group_id имеют NOT NULL constraint и foreign key,
-- но при парсинге Excel может не быть ID (только имя)
--
-- Решение: разрешить NULL для teacher_id и group_id, чтобы можно было сохранять
-- нагрузки с именами без ID (ID можно будет найти позже)

-- Удалить foreign key constraints
ALTER TABLE course_loads DROP CONSTRAINT IF EXISTS course_loads_teacher_id_fkey;
ALTER TABLE course_loads DROP CONSTRAINT IF EXISTS course_loads_group_id_fkey;

-- Изменить колонки, чтобы разрешить NULL
ALTER TABLE course_loads ALTER COLUMN teacher_id DROP NOT NULL;
ALTER TABLE course_loads ALTER COLUMN group_id DROP NOT NULL;

-- Добавить foreign key constraints обратно (теперь с поддержкой NULL)
ALTER TABLE course_loads ADD CONSTRAINT course_loads_teacher_id_fkey 
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT;
    
ALTER TABLE course_loads ADD CONSTRAINT course_loads_group_id_fkey 
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE RESTRICT;

-- Комментарии
COMMENT ON COLUMN course_loads.teacher_id IS 
    'ID преподавателя (может быть NULL, если преподаватель еще не создан в системе, но есть teacher_name)';
    
COMMENT ON COLUMN course_loads.group_id IS 
    'ID группы (может быть NULL, если группа еще не создана в системе, но есть group_name)';

