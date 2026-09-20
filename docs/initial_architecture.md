# Initial Architecture: Exchange Control Desk

This document outlines the end-to-end technical and data architecture for **Exchange Control Desk**, describing data flows, stage boundaries, and analytical tiers.

---

## 1. High-Level Architecture Diagram

```text
       +-------------------------------------------------------------+
       |                     EXTERNAL DATA SOURCES                   |
       |  - CoinDCX Public Ticker API (https://api.coindcx.com/)      |
       |  - CoinGecko Historical Benchmarks                          |
       |  - Offline Real Reference Cache (Verified Fallback)          |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                   DATA GENERATION & INGESTION               |
       |  - Live / Fallback Market Ingestion (`python/ingestion/`)   |
       |  - Realistic Synthetic Exchange Generator (`data/synthetic`)|
       |  - Controlled Anomaly Ground-Truth Injection Framework      |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               DATA QUALITY & VALIDATION ENGINE              |
       |  - 6 Dimensions: Completeness, Validity, Consistency,        |
       |    Uniqueness, Timeliness, Referential Integrity            |
       |  - Automated Rejection / Quarantine Pipeline                |
       |  - Automated DQ Report & Score (`outputs/quality/`)         |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                RELATIONAL STORAGE LAYER                     |
       |  - PostgreSQL / DuckDB Embedded Analytical Engine           |
       |  - Staging Tables (`stg_transactions`, `stg_users`, etc.)   |
       |  - Clean Star Schema:                                       |
       |    * Fact: `fact_transactions`, `fact_market_ticks`        |
       |    * Dim:  `dim_users`, `dim_assets`, `dim_dates`           |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                 SQL ANALYTICS & TRANSFORMATIONS             |
       |  - Rolling 24H Volume & User Activity Aggregations (CTEs)   |
       |  - Funnel & Success / Failure Rate SQL Models               |
       |  - Analytical Views (`sql/views/analytical_views.sql`)      |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             PYTHON ANALYTICS & ANOMALY ENGINE               |
       |  - Feature Engineering (Rolling User Means, Velocities)     |
       |  - Statistical Anomaly Detection (Z-score, IQR, Typologies) |
       |  - Synthetic Ground Truth Evaluation (Precision, Recall)    |
       |  - Incident Prioritization & Ranking (`outputs/incidents/`) |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                BI SEMANTIC LAYER & REPORTING                |
       |  - Power BI Semantic Model & DAX Measures                   |
       |  - 5 Operational Report Pages (Executive, Market, Trans,    |
       |    Incidents, Data Quality)                                 |
       |  - Cross-System Zero-Tolerance KPI Reconciliation           |
       |  - Executive Decision Summary (`outputs/executive/`)        |
       +-------------------------------------------------------------+
```

---

## 2. Storage & Execution Strategy

1. **Analytical Engine Flexibility:** The project natively supports standard PostgreSQL via SQL scripts (`sql/schema/create_tables.sql`) and simultaneously provides high-performance embedded DuckDB execution (`python/common/db.py`) to guarantee that any reviewer can clone and run the full pipeline in seconds without requiring root Docker or external database setups.
2. **Deterministic Reproducibility:** Fixed random seeds (`seed: 42`) ensure identical synthetic cohorts, transaction distributions, and injected anomaly ground truth across runs.
3. **Data Quality Gate:** Invalid records failing schema validation are quarantined prior to populating analytical fact tables, preventing corruption of downstream KPIs.
