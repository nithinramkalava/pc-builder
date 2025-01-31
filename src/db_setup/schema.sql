-- schema.sql
-- Save this file in the db_setup directory

-- Drop existing tables if they exist
DROP TABLE IF EXISTS cpu_motherboard_compatibility;
DROP TABLE IF EXISTS case_motherboard_compatibility;
DROP TABLE IF EXISTS memory_motherboard_compatibility;
DROP TABLE IF EXISTS cpu_cooler;
DROP TABLE IF EXISTS power_supply;
DROP TABLE IF EXISTS case_enclosure;
DROP TABLE IF EXISTS video_card;
DROP TABLE IF EXISTS storage;
DROP TABLE IF EXISTS memory;
DROP TABLE IF EXISTS motherboard;
DROP TABLE IF EXISTS cpu;

-- Create tables with UNIQUE constraint on name
CREATE TABLE IF NOT EXISTS cpu (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    core_count INTEGER,
    core_clock DECIMAL(4,2),
    boost_clock DECIMAL(4,2),
    tdp INTEGER,
    graphics VARCHAR(255),
    smt BOOLEAN
);

CREATE TABLE IF NOT EXISTS motherboard (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    socket VARCHAR(50),
    form_factor VARCHAR(50),
    max_memory INTEGER,
    memory_slots INTEGER,
    color VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS memory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    speed VARCHAR(50),
    modules VARCHAR(50),
    price_per_gb DECIMAL(10,2),
    color VARCHAR(50),
    first_word_latency DECIMAL(5,2),
    cas_latency DECIMAL(4,2)
);

CREATE TABLE IF NOT EXISTS storage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    capacity DECIMAL(10,2),
    price_per_gb DECIMAL(10,3),
    type VARCHAR(50),
    cache DECIMAL(10,2),
    form_factor VARCHAR(50),
    interface VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS video_card (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    chipset VARCHAR(100),
    memory DECIMAL(5,2),
    core_clock DECIMAL(6,2),
    boost_clock DECIMAL(6,2),
    color VARCHAR(50),
    length DECIMAL(6,2)
);

CREATE TABLE IF NOT EXISTS case_enclosure (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    type VARCHAR(50),
    color VARCHAR(50),
    psu DECIMAL(6,2),
    side_panel VARCHAR(50),
    external_volume DECIMAL(10,2),
    internal_35_bays INTEGER
);

CREATE TABLE IF NOT EXISTS power_supply (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    type VARCHAR(50),
    efficiency VARCHAR(50),
    wattage INTEGER,
    modular VARCHAR(50),
    color VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS cpu_cooler (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10,2),
    rpm VARCHAR(100),
    noise_level VARCHAR(50),
    color VARCHAR(50),
    size DECIMAL(5,2)
);

-- Compatibility tables
CREATE TABLE IF NOT EXISTS cpu_motherboard_compatibility (
    id SERIAL PRIMARY KEY,
    cpu_id INTEGER REFERENCES cpu(id),
    motherboard_id INTEGER REFERENCES motherboard(id),
    UNIQUE(cpu_id, motherboard_id)
);

CREATE TABLE IF NOT EXISTS case_motherboard_compatibility (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES case_enclosure(id),
    motherboard_id INTEGER REFERENCES motherboard(id),
    UNIQUE(case_id, motherboard_id)
);

CREATE TABLE IF NOT EXISTS memory_motherboard_compatibility (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER REFERENCES memory(id),
    motherboard_id INTEGER REFERENCES motherboard(id),
    UNIQUE(memory_id, motherboard_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_cpu_name ON cpu(name);
CREATE INDEX idx_motherboard_name ON motherboard(name);
CREATE INDEX idx_memory_name ON memory(name);
CREATE INDEX idx_storage_name ON storage(name);
CREATE INDEX idx_video_card_name ON video_card(name);
CREATE INDEX idx_case_name ON case_enclosure(name);
CREATE INDEX idx_power_supply_name ON power_supply(name);
CREATE INDEX idx_cpu_cooler_name ON cpu_cooler(name);