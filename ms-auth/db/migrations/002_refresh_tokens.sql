-- ============================================
-- REFRESH TOKENS AND PASSWORD RESET
-- Version: 002
-- ============================================

-- ============ REFRESH_TOKENS TABLE ============

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    token VARCHAR(255) UNIQUE NOT NULL,
    token_family VARCHAR(100),
    
    -- Срок действия
    expires_at TIMESTAMP NOT NULL,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    used_at TIMESTAMP,
    revoked_at TIMESTAMP,
    
    -- Информация о клиенте
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_id VARCHAR(100),
    
    -- Статус
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT valid_token_expiry CHECK (expires_at > created_at)
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_family ON refresh_tokens(token_family);

-- ============ PASSWORD_RESET_TOKENS TABLE ============

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    token VARCHAR(255) UNIQUE NOT NULL,
    
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    used_at TIMESTAMP,
    
    ip_address VARCHAR(45),
    
    CONSTRAINT valid_reset_expiry CHECK (expires_at > created_at)
);

CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token) WHERE used_at IS NULL;

-- ============ COMMENTS ============

COMMENT ON TABLE refresh_tokens IS 'Refresh токены для обновления access токенов';
COMMENT ON TABLE password_reset_tokens IS 'Токены для сброса пароля';

COMMENT ON COLUMN refresh_tokens.token_family IS 'Семейство токенов для защиты от rotation attacks';
COMMENT ON COLUMN refresh_tokens.used_at IS 'Время использования токена';
COMMENT ON COLUMN refresh_tokens.revoked_at IS 'Время отзыва токена';

