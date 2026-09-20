# Functional Requirements Document (FRD)

**Project:** Exchange Control Desk  
**Version:** 1.0  
**Date:** 2026-09-20  

---

## 1. Functional Modules & Specifications

### FR-01: Ingestion Engine (`python/ingestion/`)
- **FR-01.1 Live Market Data Ingestion:** System must connect via HTTPS to public ticker endpoints (CoinDCX `https://api.coindcx.com/exchange/ticker`) to ingest real-time market snapshots including `market`, `last_price`, `high`, `low`, `volume`, and `timestamp`.
- **FR-01.2 Deterministic Offline Fallback:** If external network access is unavailable or throttled, ingestion must seamlessly load verified cached benchmark snapshots from `data/raw/market/` without failing the pipeline.
- **FR-01.3 Synthetic Exchange Data Generation:** System must generate synthetic user accounts, asset masters, and transaction streams reflecting realistic retail and institutional behavioral distributions with parameterized volume scales (`dev`, `medium`, `stress`).

### FR-02: Data Quality & Validation Engine (`python/validation/`)
- **FR-02.1 Multi-Dimensional Validation:** Perform automated record-level assertions across 6 dimensions:
  1. *Completeness:* Null checks on mandatory fields (`transaction_id`, `user_id`, `asset_id`, `timestamp`, `gross_value`).
  2. *Validity:* Enum checks on `transaction_type` (DEPOSIT, WITHDRAWAL, TRADE), `side` (BUY, SELL), `status` (COMPLETED, FAILED, CANCELLED), and non-negative numeric constraints.
  3. *Consistency:* Cross-field relationship verification: `gross_value ≈ quantity * price` within $\pm 1.0\%$ tolerance; `net_value = gross_value - fee` (or `+ fee`).
  4. *Uniqueness:* Zero duplicate primary keys (`transaction_id`).
  5. *Timeliness:* Identification of stale timestamps or future-dated records.
  6. *Referential Integrity:* Orphan checks confirming that transaction foreign keys reference valid `dim_users` and `dim_assets`.
- **FR-02.2 Quarantine Pipeline:** Records failing critical checks must be split into quarantined datasets and excluded from clean analytical loading.
- **FR-02.3 Data Quality Scoring:** Compute an automated, weighted Data Quality Score (0–100%) stored in `outputs/quality/data_quality_report.json`.

### FR-03: Relational & Analytical SQL Layer (`sql/`)
- **FR-03.1 Schema DDL:** Provide ANSI-compliant DDL scripts establishing staging tables, dimensions, and facts with primary, foreign key, and check constraints.
- **FR-03.2 SQL Transformations:** Implement production SQL models computing rolling 24-hour volumes, user transaction frequency, and failure rate funnels utilizing Common Table Expressions (CTEs) and window functions (`ROW_NUMBER`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM() OVER ()`).
- **FR-03.3 Analytical Views:** Maintain pre-aggregated views: `vw_daily_platform_metrics`, `vw_user_risk_summary`, `vw_asset_liquidity_summary`.

### FR-04: Feature Engineering & Analytics (`python/feature_engineering/`)
- **FR-04.1 User-Level Features:** Compute user rolling 30-day transaction volume, historical mean transaction value $\mu_u$, standard deviation $\sigma_u$, cumulative failure rate, and deposit/withdrawal ratio.
- **FR-04.2 Transaction-Level Features:** Compute user baseline deviation Z-score, transaction velocity ($N$ tx in prior 60 minutes), time delta since prior transaction ($\Delta t$), and fee ratio.
- **FR-04.3 Asset-Level Features:** Compute rolling 24h platform volume, price volatility, and platform-to-global volume share.

### FR-05: Anomaly Detection & Evaluation Engine (`python/anomaly_detection/`)
- **FR-05.1 Typology Detection:** Implement detectors for:
  1. High transaction velocity bursts ($>5$ tx in 60 min).
  2. Abnormal transaction values ($Z > 3.0$ against user rolling baseline).
  3. Repeated consecutive failures ($>3$ failed tx within 30 min).
  4. Rapid deposit-to-withdrawal pass-through ($\Delta t \le 15 \text{ min}$ with zero intermediate trading).
  5. Excessive fee anomalies (IQR outlier fence).
  6. Asset volume spikes ($>3\sigma$ above asset baseline).
- **FR-05.2 Human-Readable Explanations:** Every flagged anomaly must emit a descriptive explanation string citing observed value, threshold, and baseline.
- **FR-05.3 Evaluation vs. Ground Truth:** Evaluate detector performance against injected ground-truth scenarios, outputting confusion matrix metrics: True Positives, False Positives, False Negatives, Precision, Recall, and F1-Score in `outputs/anomalies/anomaly_evaluation.csv`.

### FR-06: Incident Prioritization & Investigation Queue (`python/incidents/`)
- **FR-06.1 Risk Scoring:** Compute composite score: $\text{Priority Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure})$.
- **FR-06.2 Priority Banding:** Assign bands: P1 (Critical), P2 (High), P3 (Medium), P4 (Low).
- **FR-06.3 Prescriptive Next Steps:** Assign actionable recommendations for each incident (e.g., "Place temporary 24h withdrawal hold; verify recent device IP; trigger enhanced KYC").
- **FR-06.4 Investigation Queue:** Export sorted triage queue to `outputs/incidents/investigation_queue.csv`.

### FR-07: Business Intelligence & Reconciliation (`powerbi/`, `python/reporting/`)
- **FR-07.1 Star-Schema Semantic Model:** Export clean dimensional tables optimized for Power BI import with 1-to-many single-direction relationships.
- **FR-07.2 DAX Measures Library:** Provide standard measures for GTV, Active Users, Success Rate, DQ Score, Open P1/P2 Incidents, and Period-over-Period growth.
- **FR-07.3 Automated KPI Reconciliation:** Script `python/reporting/reconciliation.py` must compute key metrics across Python, SQL views, and DAX equivalents, ensuring zero-tolerance reconciliation.
