-- Events: Мероприятия кампуса

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    max_participants INTEGER,
    registered_count INTEGER DEFAULT 0,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_registrations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    user_name VARCHAR(200),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);
CREATE INDEX IF NOT EXISTS idx_registrations_event_id ON event_registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_registrations_user_id ON event_registrations(user_id);

-- Триггер для обновления registered_count
CREATE OR REPLACE FUNCTION update_event_registered_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE events SET registered_count = registered_count + 1 WHERE id = NEW.event_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE events SET registered_count = registered_count - 1 WHERE id = OLD.event_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_registered_count
    AFTER INSERT OR DELETE ON event_registrations
    FOR EACH ROW EXECUTE FUNCTION update_event_registered_count();

