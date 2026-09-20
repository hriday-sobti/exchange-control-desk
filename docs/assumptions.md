# Project Assumptions & Constraints: Exchange Control Desk

This document enumerates the foundational assumptions, analytical boundaries, and operating constraints adopted in **Exchange Control Desk**.

---

## 1. Domain & Operational Assumptions

1. **Analytical Prototype Scope:** The platform is built as an operational risk and analytics control desk for an internal operations/analytics team. It is not an authorized regulatory submission engine for FIU-IND nor a legally binding STR generator.
2. **Synthetic Exchange Population:** Because proprietary transaction ledgers of licensed exchanges are strictly confidential under banking secrecy and PMLA regulations, user account records and transaction volumes are modeled synthetically.
3. **Realistic Behavioral Cohorts:** The synthetic generator models realistic distributions:
   - 80% retail users with modest transaction frequency and normal values.
   - 15% active swing traders with elevated velocity and medium balances.
   - 5% high-net-worth / institutional accounts with high transaction sizes.
   - Realistic failure rate baseline (~3.5% across banking on-ramp and off-ramp rails).
4. **Market Data Coupling:** Real public tickers from CoinDCX API (and CoinGecko reference benchmarks) anchor synthetic trading prices to genuine market reality (e.g., BTC/INR ~ ₹6,500,000 - ₹8,500,000 range).

---

## 2. Technical & Architectural Constraints
1. **Environment Reproducibility:** To ensure reliable execution across developer and production environments without external infrastructure overhead, the database layer utilizes standard SQL ANSI DDL/DML, executable in both PostgreSQL and embedded DuckDB.
2. **Auditability & Explainability:** Black-box ML models are excluded from primary incident generation. Every flagged anomaly must produce an unambiguous causal narrative detailing the baseline, threshold, and deviation observed.
3. **Zero-Tolerance KPI Reconciliation:** Core financial KPIs (Total Transactions, Gross Transaction Value, Active Users, Fee Revenue) must reconcile across Python, SQL views, and Power BI DAX calculations with zero unaccounted discrepancy.
4. **Safe Configuration Defaults:** All statistical thresholds (Z-score limits, velocity window lengths, IQR multipliers) are externalized in `config/project_config.yaml` rather than hardcoded.
