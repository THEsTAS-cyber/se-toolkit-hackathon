-- Database initialization script
-- Games table with PSPricing support
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    ps_id INTEGER UNIQUE,
    sku VARCHAR(255),
    sku_suffix VARCHAR(100),
    title_id VARCHAR(100),
    concept_id INTEGER,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    cover_url VARCHAR(1000),
    platforms TEXT[] NOT NULL DEFAULT '{}',
    content_type VARCHAR(100),
    top_category VARCHAR(100),
    audio_languages TEXT[] NOT NULL DEFAULT '{}',
    subtitle_languages TEXT[] NOT NULL DEFAULT '{}',
    release_date TIMESTAMP WITH TIME ZONE,
    store_url VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMP WITH TIME ZONE,
    last_synced_at TIMESTAMP WITH TIME ZONE
);

-- Price entries table
CREATE TABLE IF NOT EXISTS price_entries (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    region VARCHAR(10) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    current_price DOUBLE PRECISION,
    original_price DOUBLE PRECISION,
    discount_percent INTEGER,
    ps_plus_price DOUBLE PRECISION,
    collection VARCHAR(100),
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_games_ps_id ON games(ps_id);
CREATE INDEX IF NOT EXISTS idx_games_sku ON games(sku);
CREATE INDEX IF NOT EXISTS idx_games_title_id ON games(title_id);
CREATE INDEX IF NOT EXISTS idx_games_concept_id ON games(concept_id);
CREATE INDEX IF NOT EXISTS idx_games_name ON games(name);
CREATE INDEX IF NOT EXISTS idx_price_entries_game_id ON price_entries(game_id);
CREATE INDEX IF NOT EXISTS idx_price_entries_region ON price_entries(region);
CREATE INDEX IF NOT EXISTS idx_price_entries_collected_at ON price_entries(collected_at);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- User favorites table
CREATE TABLE IF NOT EXISTS user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_game_favorite UNIQUE (user_id, game_id)
);

CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_game_id ON user_favorites(game_id);

