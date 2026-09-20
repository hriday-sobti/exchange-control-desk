-- ==============================================================================
-- OPERATIONAL SQL ANALYTICS & TRANSFORMATIONS
-- Demonstrating advanced SQL: CTEs, Window Functions, Rolling 24H Windows,
-- User Cohorting, Funnel Drop-offs, and Exception Queries.
-- ==============================================================================

-- 1. Rolling 24-Hour Transaction Volume & Velocity per User
-- Uses Window functions with physical and logical framing
WITH user_chronological_tx AS (
    SELECT
        t.transaction_id,
        t.user_id,
        t.timestamp,
        t.gross_value,
        t.status,
        -- Prior transaction timestamp for latency calculations
        LAG(t.timestamp) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.timestamp
        ) AS prev_tx_timestamp,
        -- Running 24-hour volume per user
        SUM(t.gross_value) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.timestamp 
            RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW
        ) AS user_rolling_24h_volume_inr,
        -- Rolling count of transactions in last 24 hours
        COUNT(t.transaction_id) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.timestamp 
            RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW
        ) AS user_rolling_24h_tx_count
    FROM fact_transactions t
)
SELECT
    transaction_id,
    user_id,
    timestamp,
    gross_value,
    status,
    prev_tx_timestamp,
    user_rolling_24h_volume_inr,
    user_rolling_24h_tx_count
FROM user_chronological_tx
LIMIT 100;


-- 2. Consecutive Failure Sequences (Brute Force / Gateway Outage Detection)
-- Uses ROW_NUMBER difference technique (Islands and Gaps) to group consecutive failures
WITH failure_islands AS (
    SELECT
        t.transaction_id,
        t.user_id,
        t.timestamp,
        t.status,
        ROW_NUMBER() OVER (PARTITION BY t.user_id ORDER BY t.timestamp) AS overall_seq,
        ROW_NUMBER() OVER (PARTITION BY t.user_id, t.status ORDER BY t.timestamp) AS status_seq
    FROM fact_transactions t
),
grouped_failures AS (
    SELECT
        user_id,
        (overall_seq - status_seq) AS run_id,
        MIN(timestamp) AS run_start,
        MAX(timestamp) AS run_end,
        COUNT(*) AS consecutive_failed_count
    FROM failure_islands
    WHERE status = 'FAILED'
    GROUP BY user_id, (overall_seq - status_seq)
)
SELECT
    user_id,
    run_start,
    run_end,
    consecutive_failed_count
FROM grouped_failures
WHERE consecutive_failed_count >= 3
ORDER BY consecutive_failed_count DESC, run_end DESC;


-- 3. Rapid Deposit-to-Withdrawal Pass-Through Detection (Layering / Mules)
-- Identifies accounts depositing fiat and immediately withdrawing crypto within 15 minutes
WITH sequential_flows AS (
    SELECT
        t.transaction_id AS wth_tx_id,
        t.user_id,
        t.timestamp AS wth_time,
        t.gross_value AS wth_amount,
        t.asset_id AS wth_asset,
        LAG(t.transaction_type) OVER (PARTITION BY t.user_id ORDER BY t.timestamp) AS prev_type,
        LAG(t.gross_value) OVER (PARTITION BY t.user_id ORDER BY t.timestamp) AS prev_deposit_amount,
        LAG(t.timestamp) OVER (PARTITION BY t.user_id ORDER BY t.timestamp) AS prev_deposit_time
    FROM fact_transactions t
    WHERE t.status = 'COMPLETED'
)
SELECT
    user_id,
    wth_tx_id,
    prev_deposit_time,
    wth_time,
    prev_deposit_amount,
    wth_amount,
    wth_asset,
    -- Time delta in minutes
    EXTRACT(EPOCH FROM (wth_time - prev_deposit_time)) / 60.0 AS elapsed_minutes
FROM sequential_flows
WHERE prev_type = 'DEPOSIT'
  AND prev_type != 'TRADE'
  AND (EXTRACT(EPOCH FROM (wth_time - prev_deposit_time)) / 60.0) <= 15.0
  AND wth_amount >= (prev_deposit_amount * 0.85);


-- 4. User Behavioral Segmentation by Quantile Distribution
-- Cohorts users by trading frequency and gross spend quantiles
WITH user_aggregates AS (
    SELECT
        t.user_id,
        COUNT(t.transaction_id) AS tx_count,
        SUM(t.gross_value) AS total_gtv,
        AVG(t.gross_value) AS avg_ticket_size,
        NTILE(4) OVER (ORDER BY COUNT(t.transaction_id)) AS freq_quartile,
        NTILE(4) OVER (ORDER BY SUM(t.gross_value)) AS gtv_quartile
    FROM fact_transactions t
    WHERE t.status = 'COMPLETED'
    GROUP BY t.user_id
)
SELECT
    user_id,
    tx_count,
    total_gtv,
    avg_ticket_size,
    freq_quartile,
    gtv_quartile,
    CASE 
        WHEN gtv_quartile = 4 AND freq_quartile >= 3 THEN 'High-Value Active'
        WHEN gtv_quartile = 4 AND freq_quartile < 3 THEN 'High-Value Low-Freq (Whale)'
        WHEN gtv_quartile < 4 AND freq_quartile >= 3 THEN 'Retail High-Velocity'
        ELSE 'Casual Retail'
    END AS behavioral_segment
FROM user_aggregates;
