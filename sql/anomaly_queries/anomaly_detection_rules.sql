-- ==============================================================================
-- OPERATIONAL ANOMALY DETECTION QUERIES (SQL PROTOTYPES)
-- Demonstrates pure SQL detection logic for core risk typologies.
-- ==============================================================================

-- 1. SQL Anomaly Detection: Transaction Velocity Bursts (>5 tx in 60 minutes)
WITH windowed_tx AS (
    SELECT
        t.transaction_id,
        t.user_id,
        t.timestamp,
        t.gross_value,
        COUNT(t.transaction_id) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.timestamp 
            RANGE BETWEEN INTERVAL 1 HOUR PRECEDING AND CURRENT ROW
        ) AS tx_count_prior_hour
    FROM fact_transactions t
)
SELECT
    transaction_id,
    user_id,
    timestamp,
    gross_value,
    tx_count_prior_hour,
    'VELOCITY_BURST' AS anomaly_type,
    'User executed ' || tx_count_prior_hour || ' transactions in 60m window (Threshold: 5)' AS explanation
FROM windowed_tx
WHERE tx_count_prior_hour >= 5;


-- 2. SQL Anomaly Detection: User Baseline Spikes (>3.0x expanding user mean)
WITH expanding_baselines AS (
    SELECT
        t.transaction_id,
        t.user_id,
        t.timestamp,
        t.gross_value,
        AVG(t.gross_value) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.timestamp 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_mean_gross
    FROM fact_transactions t
)
SELECT
    transaction_id,
    user_id,
    timestamp,
    gross_value,
    ROUND(prior_mean_gross, 2) AS prior_baseline_mean,
    ROUND(gross_value / NULLIF(prior_mean_gross, 0), 2) AS spike_multiplier,
    'BASELINE_SPIKE' AS anomaly_type,
    'Transaction value ₹' || ROUND(gross_value, 2) || ' is ' || ROUND(gross_value / NULLIF(prior_mean_gross, 0), 1) || 'x prior mean baseline' AS explanation
FROM expanding_baselines
WHERE prior_mean_gross IS NOT NULL 
  AND gross_value >= (prior_mean_gross * 3.0)
  AND gross_value >= 10000.0;
