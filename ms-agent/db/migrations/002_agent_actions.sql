-- Действия агента
-- Детальная история всех действий для анализа

CREATE TABLE IF NOT EXISTS agent_actions (
    id SERIAL PRIMARY KEY,
    generation_id INTEGER NOT NULL REFERENCES generation_history(id) ON DELETE CASCADE,
    
    -- Итерация
    iteration INTEGER NOT NULL,
    
    -- Действие
    action_type VARCHAR(50) NOT NULL,          -- 'swap', 'move', 'analyze', 'assign_classroom'
    action_params JSONB NOT NULL,              -- Параметры действия
    
    -- Результат
    success BOOLEAN NOT NULL,
    score_before INTEGER,
    score_after INTEGER,
    score_delta INTEGER,                       -- score_after - score_before
    
    -- Reasoning от LLM
    reasoning TEXT,                            -- Объяснение агента
    
    -- Время
    created_at TIMESTAMP DEFAULT NOW(),
    execution_time_ms INTEGER
);

-- Индексы
CREATE INDEX idx_agent_actions_generation ON agent_actions(generation_id);
CREATE INDEX idx_agent_actions_iteration ON agent_actions(generation_id, iteration);
CREATE INDEX idx_agent_actions_type ON agent_actions(action_type);
CREATE INDEX idx_agent_actions_success ON agent_actions(success);
CREATE INDEX idx_agent_actions_created ON agent_actions(created_at DESC);

-- Индекс для поиска успешных действий
CREATE INDEX idx_agent_actions_successful_delta 
    ON agent_actions(action_type, score_delta DESC) 
    WHERE success = true AND score_delta > 0;

-- Комментарии
COMMENT ON TABLE agent_actions IS 'Все действия агента для анализа и отладки';
COMMENT ON COLUMN agent_actions.reasoning IS 'Объяснение от LLM почему было выбрано это действие';
COMMENT ON COLUMN agent_actions.score_delta IS 'Изменение скора после действия';

