-- История генераций расписания
-- Отслеживание работы агента

CREATE TABLE IF NOT EXISTS generation_history (
    id SERIAL PRIMARY KEY,
    
    -- Идентификация
    job_id VARCHAR(100) UNIQUE NOT NULL,       -- UUID для отслеживания
    
    -- Этап
    stage INTEGER NOT NULL CHECK (stage IN (1, 2)),
    stage_name VARCHAR(50),                    -- "temporal" или "classroom"
    
    -- Статус
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'stopped')),
    
    -- Итерация
    current_iteration INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 100,
    
    -- Скоры
    initial_score INTEGER,
    current_score INTEGER,
    best_score INTEGER,
    
    -- Метрики (детальные данные в JSON)
    metrics JSONB DEFAULT '{}',
    
    -- Reasoning и действия
    last_reasoning TEXT,
    total_actions INTEGER DEFAULT 0,
    
    -- Время
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Пользователь
    created_by INTEGER,
    
    -- Результат
    error_message TEXT
);

-- Индексы
CREATE INDEX idx_generation_history_job_id ON generation_history(job_id);
CREATE INDEX idx_generation_history_status ON generation_history(status);
CREATE INDEX idx_generation_history_created ON generation_history(started_at DESC);
CREATE INDEX idx_generation_history_stage ON generation_history(stage);
CREATE INDEX idx_generation_history_user ON generation_history(created_by);

-- Комментарии
COMMENT ON TABLE generation_history IS 'История генераций расписания агентом';
COMMENT ON COLUMN generation_history.stage IS '1=Оптимизация времени, 2=Подбор аудиторий';
COMMENT ON COLUMN generation_history.metrics IS 'Детальные метрики в JSON формате';

