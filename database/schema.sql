DROP TABLE IF EXISTS menu_items;

CREATE TABLE IF NOT EXISTS menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL, -- e.g., 'pizza', 'pasta', 'wine', 'beer'
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    properties JSONB -- For extra attributes like wine region, beer type, etc.
);

-- Add an index on the category for faster filtering
CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category);

-- Add an index on price
CREATE INDEX IF NOT EXISTS idx_menu_items_price ON menu_items(price);