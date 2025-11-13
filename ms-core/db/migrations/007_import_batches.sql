-- Батчи импорта учебной нагрузки из Excel

CREATE TABLE IF NOT EXISTS import_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,     -- UUID батча
    
    -- Параметры импорта
    filename VARCHAR(255),
    file_size INTEGER,
    semester INTEGER,
    academic_year VARCHAR(20),
    
    -- Результаты
    total_rows INTEGER DEFAULT 0,
    successful_rows INTEGER DEFAULT 0,
    failed_rows INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,          -- Массив ошибок
    
    -- Статус
    status VARCHAR(20) DEFAULT 'processing',   -- 'processing', 'completed', 'failed'
    
    -- Метаданные
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    imported_by INTEGER,
    imported_by_name VARCHAR(200),
    
    CONSTRAINT valid_import_status CHECK (
        status IN ('processing', 'completed', 'failed')
    )
);

-- Индексы
CREATE INDEX idx_import_batches_batch_id ON import_batches(batch_id);
CREATE INDEX idx_import_batches_status ON import_batches(status);
CREATE INDEX idx_import_batches_started ON import_batches(started_at DESC);
CREATE INDEX idx_import_batches_semester ON import_batches(semester, academic_year);

-- Комментарии
COMMENT ON TABLE import_batches IS 'История импорта учебной нагрузки из Excel файлов';
COMMENT ON COLUMN import_batches.batch_id IS 'Уникальный идентификатор батча импорта (UUID)';
COMMENT ON COLUMN import_batches.errors IS 'JSONB массив ошибок при импорте';
COMMENT ON COLUMN import_batches.status IS 'Статус: processing=обработка, completed=завершён, failed=ошибка';

