# Technical Architecture & Operations Defense Guide

This document provides a deep architectural and analytical defense of the engineering decisions, mathematical formulas, SQL models, anomaly rules, and BI measures implemented in **Exchange Control Desk**.

---

## 1. Business & Domain Architecture

### Q1: What concrete business problem does Exchange Control Desk solve?
**Architecture Context:** In a Virtual Digital Asset (VDA) exchange operating under Indian FIU-IND / PMLA regulations, operations, risk, and analytics teams face fragmented visibility. Payment gateway drop-offs, potential money-laundering structuring (e.g. rapid fiat-crypto layering), and data quality corruption happen simultaneously. Exchange Control Desk provides an integrated operations room: unifying live market data, transaction flows, a 6-dimension automated data quality engine, explainable statistical anomaly detection, and a prioritized investigation queue that routes critical alerts to analysts within SLAs.

### Q2: What is the boundary between this prototype and a regulatory compliance filing tool?
**Architecture Context:** The documentation strictly outlines that this system is an **operational risk and analytics decision-support prototype**. It identifies mathematical, behavioral, and transactional pattern exceptions to assist operational analysts in triaging potential fraud, system bugs, or unusual activity before escalation. It does not file official STRs or act as certified legal software.

---

## 2. Data Engineering & Dimensional Modeling

### Q3: Why use synthetic data instead of real exchange transaction logs?
**Architecture Context:** Real transactional ledgers of licensed exchanges are strictly confidential under banking secrecy, PMLA, and customer privacy regulations. To maintain realism, behavioral distributions were calibrated to exchange operating realities: 80% retail casuals, 15% active swing traders, and 5% high-net-worth/corporate users with distinct mean spends and activity frequencies. Furthermore, the synthetic stream is anchored to real live market pricing from CoinDCX's public API and injected with 1,400+ controlled ground-truth anomaly scenarios to evaluate detection rigor honestly.

### Q4: Explain the grain of the transaction fact table.
**Architecture Context:** In `fact_transactions`, one row represents a **single discrete transactional event (Deposit, Withdrawal, or Trade execution) attempted or completed on the platform**. It links via surrogate and natural foreign keys to `dim_users` (`user_id`), `dim_assets` (`asset_id`), and `dim_dates` (`date_key`), ensuring a pure star schema with 1-to-many single-direction relationships.

---

## 3. SQL Analytics & Transformations

### Q5: Where are window functions applied, and what operational problem do they solve?
**Architecture Context:** Window functions are used in `sql/transformations/operational_analytics.sql`:
1. `SUM(...) OVER (PARTITION BY user_id ORDER BY timestamp RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW)` calculates rolling 24-hour transaction volume per user without expensive self-joins.
2. `LAG(timestamp)` and `LAG(transaction_type)` compute time delta between successive transactions for rapid pass-through detection.
3. The **Islands and Gaps technique** using `ROW_NUMBER() OVER (...) - ROW_NUMBER() OVER (PARTITION BY status ...)` isolates runs of consecutive failed transactions for brute-force or gateway outage detection.

---

## 4. Anomaly Detection & Mathematical Statistics

### Q6: Why choose Rolling Expanding Z-scores and IQR instead of deep learning or black-box ML?
**Architecture Context:** Three fundamental reasons:
1. **Explainability & Regulatory Auditability:** Operations and compliance analysts cannot act on opaque neural network embeddings. Every alert in our system generates an explicit natural-language causal narrative (e.g., *"Transaction value ₹48,281 is 14.1σ above user's 30-day baseline"*).
2. **Heavy-Tailed Distributions:** For fee distributions, which are highly skewed, the non-parametric Interquartile Range (IQR) fence ($Q_3 + 1.5 \times \text{IQR}$) was chosen because standard deviation is excessively distorted by extreme outliers.
3. **Execution Speed:** Vectorized cumulative aggregations compute in milliseconds across 100k transactions without GPU dependencies.

### Q7: How does the incident prioritization formula operate?
**Architecture Context:** Incidents are scored using a non-linear composite formulation:
$$\text{Priority Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure}_{\text{INR}})$$
- **Severity (1–5):** Intrinsic risk of the anomaly typology (e.g., rapid pass-through = 5; fee discrepancy = 2).
- **Likelihood (1–5):** Statistical magnitude of deviation.
- **$\ln(1 + \text{Exposure})$:** Logarithmic damping of monetary exposure ensures multi-lakh rupee breaches elevate priority without letting an extreme outlier distort the entire triage queue.
- Incidents are triaged into actionable bands: P1 (Critical, $<15$m SLA), P2 (High, $<2$h SLA), P3 (Medium), and P4 (Low).

---

## 5. BI & Semantic Reconciliation

### Q8: What is cross-system reconciliation, and how is it enforced?
**Architecture Context:** A common operational issue in enterprise analytics is discrepancies between analyst Python scripts, warehouse SQL tables, and Power BI dashboards. In `python/reporting/reconciliation.py`, an automated zero-tolerance audit extracts total transactions, GTV, active user count, and fee revenue across all three tiers simultaneously. The audit verifies $0.00\%$ discrepancy within a strict $\pm 0.01$ rupee rounding tolerance, proving absolute end-to-end data integrity.
