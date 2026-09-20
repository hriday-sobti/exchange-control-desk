-- ==============================================================================
-- STAGING TABLES DDL
-- Raw landing zone for untransformed batch feeds prior to quality checks.
-- ==============================================================================

CREATE TABLE IF NOT EXISTS stg_raw_transactions (
    raw_tx_id VARCHAR(64),
    raw_user_id VARCHAR(64),
    raw_asset_id VARCHAR(32),
    raw_timestamp VARCHAR(64),
    raw_type VARCHAR(32),
    raw_side VARCHAR(16),
    raw_quantity VARCHAR(64),
    raw_price VARCHAR(64),
    raw_gross_value VARCHAR(64),
    raw_fee VARCHAR(64),
    raw_status VARCHAR(32),
    raw_payment_method VARCHAR(32),
    raw_device_type VARCHAR(32),
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stg_raw_market_ticks (
    raw_market VARCHAR(32),
    raw_last_price VARCHAR(64),
    raw_high VARCHAR(64),
    raw_low VARCHAR(64),
    raw_volume VARCHAR(64),
    raw_change_24h VARCHAR(32),
    raw_timestamp VARCHAR(64),
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
