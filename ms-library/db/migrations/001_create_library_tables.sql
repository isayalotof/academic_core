-- Library: Библиотека

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200),
    isbn VARCHAR(50) UNIQUE,
    category VARCHAR(100),
    total_copies INTEGER DEFAULT 1 CHECK (total_copies >= 0),
    available_copies INTEGER DEFAULT 1 CHECK (available_copies >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_reservations (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    user_name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'reserved' CHECK (status IN ('reserved', 'borrowed', 'returned')),
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    returned_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_reservations_book_id ON book_reservations(book_id);
CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON book_reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON book_reservations(status);

-- Триггер для обновления available_copies
CREATE OR REPLACE FUNCTION update_book_available_copies()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'borrowed' THEN
        UPDATE books SET available_copies = available_copies - 1 WHERE id = NEW.book_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' AND OLD.status != 'returned' AND NEW.status = 'returned' THEN
        UPDATE books SET available_copies = available_copies + 1 WHERE id = NEW.book_id;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_available_copies
    AFTER INSERT OR UPDATE ON book_reservations
    FOR EACH ROW EXECUTE FUNCTION update_book_available_copies();

