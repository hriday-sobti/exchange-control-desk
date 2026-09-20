-- ==============================================================================
-- ANALYTICAL & OPERATIONAL VIEWS
-- Provides aggregated, performant business representations for reporting and BI.
-- ==============================================================================

-- 1. Daily Platform Executive Summary
CREATE OR REPLACE VIEW vw_daily_platform_metrics AS
SELECT
    d.calendar_date,
    t.date_key,
    COUNT(t.transaction_id) AS total_transactions,
    COUNT(DISTINCT t.user_id) AS active_users,
    SUM(t.gross_value) AS total_gtv_inr,
    SUM(CASE WHEN t.status = 'COMPLETED' THEN t.fee ELSE 0 END) AS total_fee_revenue_inr,
    AVG(t.gross_value) AS avg_transaction_value_inr,
    ROUND(CAST(SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) AS NUMERIC) / NULLIF(COUNT(t.transaction_id), 0) * 100.0, 2) AS success_rate_pct,
    ROUND(CAST(SUM(CASE WHEN t.status = 'FAILED' THEN 1 ELSE 0 END) AS NUMERIC) / NULLIF(COUNT(t.transaction_id), 0) * 100.0, 2) AS failure_rate_pct
FROM fact_transactions t
JOIN dim_dates d ON t.date_key = d.date_key
GROUP BY d.calendar_date, t.date_key;


-- 2. Asset Liquidity & Volume Distribution
CREATE OR REPLACE VIEW vw_asset_volume_summary AS
SELECT
    t.asset_id,
    COALESCE(a.name, t.asset_id) AS asset_name,
    COALESCE(a.category, 'Unknown') AS category,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.gross_value) AS total_volume_inr,
    ROUND(SUM(t.gross_value) * 100.0 / NULLIF(SUM(SUM(t.gross_value)) OVER (), 0), 2) AS platform_volume_share_pct,
    AVG(t.price) AS avg_execution_price_inr
FROM fact_transactions t
LEFT JOIN dim_assets a ON t.asset_id = a.asset_id
WHERE t.status = 'COMPLETED'
GROUP BY t.asset_id, a.name, a.category;


-- 3. Operational Incident & Anomaly Triage Queue
CREATE OR REPLACE VIEW vw_incident_triage_queue AS
SELECT
    i.incident_id,
    i.created_at,
    i.priority_band,
    i.priority_score,
    i.severity,
    i.likelihood,
    i.exposure_inr,
    i.status AS incident_status,
    a.anomaly_type,
    a.detector_method,
    a.explanation,
    i.recommendation,
    u.user_id,
    u.user_segment,
    u.risk_tier,
    u.country
FROM fact_incidents i
JOIN fact_anomalies a ON i.anomaly_id = a.anomaly_id
JOIN dim_users u ON i.user_id = u.user_id;


-- 4. User Risk & Activity Profiling
CREATE OR REPLACE VIEW vw_user_risk_profile AS
SELECT
    u.user_id,
    u.user_segment,
    u.risk_tier,
    COUNT(t.transaction_id) AS lifetime_transactions,
    SUM(t.gross_value) AS lifetime_volume_inr,
    COUNT(CASE WHEN t.status = 'FAILED' THEN 1 END) AS failed_tx_count,
    ROUND(CAST(COUNT(CASE WHEN t.status = 'FAILED' THEN 1 END) AS NUMERIC) / NULLIF(COUNT(t.transaction_id), 0) * 100.0, 2) AS user_failure_rate_pct,
    COUNT(DISTINCT a.anomaly_id) AS total_anomalies_flagged
FROM dim_users u
LEFT JOIN fact_transactions t ON u.user_id = t.user_id
LEFT JOIN fact_anomalies a ON u.user_id = a.user_id
GROUP BY u.user_id, u.user_segment, u.risk_tier;
