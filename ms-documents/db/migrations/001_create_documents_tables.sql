-- Documents: Заказ документов и справок

CREATE TABLE IF NOT EXISTS document_requests (
    id SERIAL PRIMARY KEY,
    document_type VARCHAR(100) NOT NULL,
    purpose TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'ready', 'completed')),
    requested_by INTEGER NOT NULL,
    requested_by_name VARCHAR(200),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    file_path VARCHAR(500),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_requests_requested_by ON document_requests(requested_by);
CREATE INDEX IF NOT EXISTS idx_requests_status ON document_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_document_type ON document_requests(document_type);

