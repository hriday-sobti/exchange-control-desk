-- ==============================================================================
-- EXECUTIVE CORE KPIS QUERY
-- Reconciles core figures across the platform.
-- ==============================================================================

SELECT
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.gross_value) AS total_gtv,
    COUNT(DISTINCT t.user_id) AS total_active_users,
    SUM(CASE WHEN t.status = 'COMPLETED' THEN t.fee ELSE 0 END) AS total_fee_revenue,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS completed_transactions,
    COUNT(CASE WHEN t.status = 'FAILED' THEN 1 END) AS failed_transactions,
    ROUND(CAST(COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS NUMERIC) / NULLIF(COUNT(t.transaction_id), 0) * 100.0, 4) AS success_rate_pct,
    ROUND(CAST(COUNT(CASE WHEN t.status = 'FAILED' THEN 1 END) AS NUMERIC) / NULLIF(COUNT(t.transaction_id), 0) * 100.0, 4) AS failure_rate_pct,
    AVG(t.gross_value) AS avg_transaction_value
FROM fact_transactions t;
