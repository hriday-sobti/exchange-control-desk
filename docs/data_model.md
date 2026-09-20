# Dimensional Data Model: Exchange Control Desk

This document specifies the relational data model, table definitions, granularities, primary/foreign keys, and star-schema relationships implemented for **Exchange Control Desk**.

---

## 1. Grain Definition for Every Table

| Table Name | Entity Type | One Row Represents | Primary Key |
| :--- | :--- | :--- | :--- |
| `dim_users` | Dimension | A unique registered platform user account and their demographic/risk baseline. | `user_id` |
| `dim_assets` | Dimension | A unique tradable Virtual Digital Asset on the exchange. | `asset_id` |
| `dim_dates` | Dimension | A single calendar date with fiscal and temporal attributes. | `date_key` |
| `fact_transactions` | Fact | A discrete transaction event (Deposit, Withdrawal, or Trade) executed or attempted on the platform. | `transaction_id` |
| `fact_market_ticks` | Fact | An hourly/periodic market pricing and volume snapshot for an asset. | `tick_id` |
| `fact_anomalies` | Fact | A single detected statistical or rule-based exception identified on a transaction, user, or asset. | `anomaly_id` |
| `fact_incidents` | Fact | A prioritized, triaged operational incident ready for analyst review and action. | `incident_id` |
| `fact_data_quality_runs` | Fact | The execution result and score of an automated data quality audit run across a specific table and check. | `check_id` |

---

## 2. Star Schema Architecture

```text
                           +-------------------+
                           |     dim_dates     |
                           +-------------------+
                           | PK: date_key      |
                           |     calendar_date |
                           |     year, month   |
                           |     is_weekend    |
                           +-------------------+
                                     |
                                     | 1
                                     |
                                     | *
+-------------------+      +-----------------------+      +-------------------+
|     dim_users     |      |   fact_transactions   |      |    dim_assets     |
+-------------------+      +-----------------------+      +-------------------+
| PK: user_id       |1   * | PK: transaction_id    | *   1| PK: asset_id      |
|     signup_date   |------| FK: user_id           |------|     symbol        |
|     country       |      | FK: asset_id          |      |     name          |
|     user_segment  |      | FK: date_key          |      |     category      |
|     account_type  |      |     timestamp         |      |     is_stablecoin |
|     risk_tier     |      |     transaction_type  |      +-------------------+
+-------------------+      |     side              |                |
                           |     quantity          |                | 1
                           |     price             |                |
                           |     gross_value       |                | *
                           |     fee               |      +-------------------+
                           |     net_value         |      | fact_market_ticks |
                           |     status            |      +-------------------+
                           |     payment_method    |      | PK: tick_id       |
                           |     device_type       |      | FK: asset_id      |
                           +-----------------------+      | FK: date_key      |
                                     |                    |     timestamp     |
                                     | 1                  |     price         |
                                     |                    |     volume_24h    |
                                     | *                  |     high, low     |
                           +-----------------------+      |     volatility    |
                           |    fact_anomalies     |      +-------------------+
                           +-----------------------+
                           | PK: anomaly_id        |
                           | FK: transaction_id    |
                           | FK: user_id           |
                           |     anomaly_type      |
                           |     metric_name       |
                           |     observed_value    |
                           |     baseline_value    |
                           |     deviation_score   |
                           |     detector_method   |
                           |     explanation       |
                           +-----------------------+
                                     |
                                     | 1
                                     |
                                     | 1..*
                           +-----------------------+
                           |    fact_incidents     |
                           +-----------------------+
                           | PK: incident_id       |
                           | FK: anomaly_id        |
                           |     severity          |
                           |     likelihood        |
                           |     exposure_inr      |
                           |     priority_score    |
                           |     priority_band     |
                           |     rationale         |
                           |     recommendation    |
                           |     status            |
                           +-----------------------+
```

---

## 3. Referential Integrity & Cardinality Rules

1. Every row in `fact_transactions` **MUST** reference an existing `user_id` in `dim_users` and `asset_id` in `dim_assets`.
2. Every row in `fact_anomalies` links to its underlying `transaction_id` and `user_id`.
3. Relationships in the Power BI semantic model are strictly **1-to-many (Single Direction)** radiating from Dimensions to Facts, ensuring unambiguous DAX filter context and optimal tabular performance.
