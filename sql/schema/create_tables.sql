-- ==============================================================================
-- EXCHANGE CONTROL DESK: PostgreSQL & ANSI SQL DDL
-- Subtitle: Transaction, Market & Risk Analytics for a VDA Platform
-- Target RDBMS: PostgreSQL 14+ / DuckDB Compatible
-- ==============================================================================

-- 1. DIMENSION TABLES

CREATE TABLE IF NOT EXISTS dim_dates (
    date_key INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(12) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(12) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_users (
    user_id VARCHAR(32) PRIMARY KEY,
    signup_date DATE NOT NULL,
    country VARCHAR(3) NOT NULL,
    user_segment VARCHAR(25) NOT NULL,
    account_type VARCHAR(25) NOT NULL,
    risk_tier VARCHAR(10) NOT NULL,
    base_spend_mean NUMERIC(18, 2) NOT NULL,
    base_spend_std NUMERIC(18, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_assets (
    asset_id VARCHAR(16) PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL,
    name VARCHAR(64) NOT NULL,
    category VARCHAR(32) NOT NULL,
    is_stablecoin BOOLEAN NOT NULL,
    base_price_inr NUMERIC(18, 4) NOT NULL,
    volatility NUMERIC(8, 4) NOT NULL
);

-- 2. FACT TABLES

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL REFERENCES dim_users(user_id),
    asset_id VARCHAR(16) NOT NULL,
    date_key INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    transaction_type VARCHAR(15) NOT NULL,
    side VARCHAR(4),
    quantity NUMERIC(24, 8) NOT NULL,
    price NUMERIC(18, 4) NOT NULL,
    gross_value NUMERIC(18, 2) NOT NULL,
    fee NUMERIC(18, 2) NOT NULL,
    net_value NUMERIC(18, 2) NOT NULL,
    status VARCHAR(15) NOT NULL,
    payment_method VARCHAR(25) NOT NULL,
    device_type VARCHAR(15) NOT NULL,
    is_injected_anomaly BOOLEAN DEFAULT FALSE,
    injected_typology VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS fact_market_ticks (
    market_symbol VARCHAR(20) NOT NULL,
    asset_id VARCHAR(16) NOT NULL,
    date_key INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price NUMERIC(18, 4) NOT NULL,
    high NUMERIC(18, 4) NOT NULL,
    low NUMERIC(18, 4) NOT NULL,
    volume_24h NUMERIC(24, 4) NOT NULL,
    change_24h_pct NUMERIC(8, 4) NOT NULL,
    bid NUMERIC(18, 4),
    ask NUMERIC(18, 4),
    PRIMARY KEY (market_symbol, timestamp)
);

CREATE TABLE IF NOT EXISTS fact_anomalies (
    anomaly_id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(36),
    user_id VARCHAR(32) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    anomaly_type VARCHAR(40) NOT NULL,
    metric_name VARCHAR(32) NOT NULL,
    observed_value NUMERIC(18, 4) NOT NULL,
    baseline_value NUMERIC(18, 4) NOT NULL,
    deviation_score NUMERIC(10, 2) NOT NULL,
    detector_method VARCHAR(30) NOT NULL,
    explanation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_incidents (
    incident_id VARCHAR(36) PRIMARY KEY,
    anomaly_id VARCHAR(36) NOT NULL,
    transaction_id VARCHAR(36),
    user_id VARCHAR(32) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    severity INTEGER NOT NULL,
    likelihood INTEGER NOT NULL,
    exposure_inr NUMERIC(18, 2) NOT NULL,
    priority_score NUMERIC(10, 2) NOT NULL,
    priority_band VARCHAR(4) NOT NULL,
    rationale TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    status VARCHAR(15) NOT NULL
);

-- INDEXES FOR OPERATIONAL PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_tx_user_ts ON fact_transactions(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_tx_asset_ts ON fact_transactions(asset_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_tx_status ON fact_transactions(status);
CREATE INDEX IF NOT EXISTS idx_incidents_priority ON fact_incidents(priority_band, status);
CREATE INDEX IF NOT EXISTS idx_anomalies_user_ts ON fact_anomalies(user_id, timestamp);
