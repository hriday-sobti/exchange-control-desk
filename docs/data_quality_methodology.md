# Data Quality Methodology: Exchange Control Desk

This document explains the mathematical and operational framework governing automated data quality validation in **Exchange Control Desk**.

---

## 1. The Six Evaluated Dimensions

1. **Completeness (Weight: 25%):** Ensures no critical business, temporal, or financial fields contain null or missing values.
   - Assertions: Non-null `transaction_id`, `user_id`, `asset_id`, `timestamp`, `gross_value`, `quantity`, `price`, `status`.
2. **Validity (Weight: 20%):** Validates that values adhere strictly to operational enums, formats, and non-negative constraints.
   - Assertions: `transaction_type` in (`DEPOSIT`, `WITHDRAWAL`, `TRADE`), `gross_value > 0`, `quantity > 0`, `fee >= 0`.
3. **Consistency (Weight: 20%):** Enforces cross-field mathematical balance equations.
   - Assertions: $|\text{gross\_value} - (\text{quantity} \times \text{price})| / \max(\text{gross\_value}, 10^{-4}) \le 1.0\%$.
4. **Uniqueness (Weight: 15%):** Asserts zero primary key collisions.
   - Assertions: No duplicated `transaction_id` records in transaction batches.
5. **Referential Integrity (Weight: 10%):** Verifies foreign keys match registered dimensional master records.
   - Assertions: Every transaction `user_id` exists in `dim_users`; every `asset_id` exists in `dim_assets`.
6. **Timeliness (Weight: 10%):** Identifies anomalous future timestamps or stale data feeds.
   - Assertions: Execution timestamp must not exceed UTC current time $+ 5\text{ minutes}$.

---

## 2. Automated Scoring & Quarantine Architecture

$$\text{Data Quality Score} = 100\% \times \sum_{d=1}^{6} w_{d} \times (1 - \text{Failure Rate}_{d})$$

Records failing any critical check are quarantined into an isolated dataset (`data/quarantined/`), shielding downstream fact tables, analytical views, and executive KPI reports from data contamination.
