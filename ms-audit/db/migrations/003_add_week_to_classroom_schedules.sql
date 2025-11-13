-- Добавить поле week (номер недели в семестре) в таблицу classroom_schedules

ALTER TABLE classroom_schedules
ADD COLUMN IF NOT EXISTS week INTEGER CHECK (week IS NULL OR (week BETWEEN 1 AND 16));

-- Обновить уникальное ограничение, чтобы учитывать неделю
-- Аудитория может быть занята в одно время в разные недели
-- Если week IS NULL, то это старая запись без недели (для обратной совместимости)
ALTER TABLE classroom_schedules
DROP CONSTRAINT IF EXISTS unique_classroom_time;

-- Уникальное ограничение: если week IS NULL, то уникальность по (classroom_id, day_of_week, time_slot)
-- Если week указан, то уникальность по (classroom_id, day_of_week, time_slot, week)
-- Используем частичный индекс для NULL значений
CREATE UNIQUE INDEX IF NOT EXISTS unique_classroom_time_with_week 
ON classroom_schedules(classroom_id, day_of_week, time_slot, week) 
WHERE week IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS unique_classroom_time_without_week 
ON classroom_schedules(classroom_id, day_of_week, time_slot) 
WHERE week IS NULL;

-- Создать индекс для быстрого поиска по неделе
CREATE INDEX IF NOT EXISTS idx_classroom_schedules_week 
ON classroom_schedules(week);

-- Комментарий к полю
COMMENT ON COLUMN classroom_schedules.week IS 'Номер недели в семестре (1-16), NULL для старых записей';

