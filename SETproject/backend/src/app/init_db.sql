-- Initial database schema for ProjectSET backend
-- Run this script to create the initial database structure

-- Games table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    ps_id INTEGER UNIQUE,
    sku VARCHAR(255),
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

-- Indexes for games table
CREATE INDEX IF NOT EXISTS idx_games_ps_id ON games(ps_id);
CREATE INDEX IF NOT EXISTS idx_games_sku ON games(sku);
CREATE INDEX IF NOT EXISTS idx_games_title_id ON games(title_id);
CREATE INDEX IF NOT EXISTS idx_games_concept_id ON games(concept_id);
CREATE INDEX IF NOT EXISTS idx_games_name ON games(name);

-- Indexes for price_entries table
CREATE INDEX IF NOT EXISTS idx_price_entries_game_id ON price_entries(game_id);
CREATE INDEX IF NOT EXISTS idx_price_entries_region ON price_entries(region);
CREATE INDEX IF NOT EXISTS idx_price_entries_collected_at ON price_entries(collected_at);

-- Unique constraint to prevent duplicate price entries
CREATE UNIQUE INDEX IF NOT EXISTS uq_price_entry 
ON price_entries(game_id, region, collected_at);
