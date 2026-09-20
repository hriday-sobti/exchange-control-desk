# Technical Interview Guide & Defense: Exchange Control Desk

This document prepares the developer to defend every architectural decision, mathematical formula, SQL transformation, anomaly detection rule, and BI measure implemented in **Exchange Control Desk**.

---

## 1. Business & Domain Questions

### Q1: What concrete business problem does Exchange Control Desk solve?
**Defense:** In a Virtual Digital Asset (VDA) exchange operating under Indian FIU-IND / PMLA regulations, operations, risk, and analytics teams face fragmented visibility. Payment gateway drop-offs, potential money-laundering structuring (e.g. rapid fiat-crypto layering), and data quality corruption happen simultaneously. Exchange Control Desk provides an integrated operations room: unifying live market data, transaction flows, a 6-dimension automated data quality engine, explainable statistical anomaly detection, and a prioritized investigation queue that routes critical alerts to analysts within SLAs.

### Q2: Is this a production AML compliance engine?
**Defense:** Absolutely not, and the documentation explicitly clarifies this boundary. It is an **operational risk and analytics decision-support prototype**. It identifies mathematical, behavioral, and transactional pattern exceptions to assist operational analysts in triaging potential fraud, system bugs, or unusual activity before escalation. It never claims to replace certified compliance officers or file regulatory STRs.

---

## 2. Data Engineering & Modeling Questions

### Q3: Why use synthetic data instead of real exchange transaction logs?
**Defense:** Real transactional ledgers of licensed exchanges are strictly confidential under banking secrecy, PMLA, and privacy laws. However, rather than generating simplistic uniform random data, I modeled realistic behavioral distributions: 80% retail casuals, 15% active swing traders, and 5% high-net-worth/corporate users with distinct mean spends and activity frequencies. Furthermore, the synthetic stream was anchored to real live market pricing from CoinDCX's public API and injected with 1,400+ controlled ground-truth anomaly scenarios to evaluate detection rigor honestly.

### Q4: Explain the grain of the transaction fact table.
**Defense:** In `fact_transactions`, one row represents a **single discrete transactional event (Deposit, Withdrawal, or Trade execution) attempted or completed on the platform**. It links via surrogate and natural foreign keys to `dim_users` (`user_id`), `dim_assets` (`asset_id`), and `dim_dates` (`date_key`), ensuring a pure star schema with 1-to-many single-direction relationships.

---

## 3. SQL Analytics & Transformations

### Q5: Where did you apply window functions, and why?
**Defense:** I used window functions extensively in `sql/transformations/operational_analytics.sql`:
1. `SUM(...) OVER (PARTITION BY user_id ORDER BY timestamp RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW)` to calculate rolling 24-hour transaction volume per user without self-joins.
2. `LAG(timestamp)` and `LAG(transaction_type)` to compute time delta between successive transactions for rapid pass-through detection.
3. The **Islands and Gaps technique** using `ROW_NUMBER() OVER (...) - ROW_NUMBER() OVER (PARTITION BY status ...)` to isolate runs of consecutive failed transactions for brute-force or gateway outage detection.

---

## 4. Anomaly Detection & Mathematical Statistics

### Q6: Why did you choose Rolling Z-scores and IQR instead of deep learning or black-box ML?
**Defense:** Three fundamental reasons:
1. **Explainability & Regulatory Auditability:** Compliance analysts and supervisors cannot act on opaque neural network embeddings. Every alert in our system generates an explicit natural-language causal narrative (e.g., *"Transaction value ₹48,281 is 14.1σ above user's 30-day baseline"*).
2. **Heavy-Tailed Distributions:** For fee distributions, which are highly skewed, the non-parametric Interquartile Range (IQR) fence ($Q_3 + 1.5 \times \text{IQR}$) was chosen because standard deviation is excessively distorted by extreme outliers.
3. **Execution Speed:** Vectorized cumulative aggregations compute in milliseconds across 100k transactions without GPU dependencies.

### Q7: How does your incident prioritization formula work?
**Defense:** We rank incidents using a non-linear composite formulation:
$$\text{Priority Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure}_{\text{INR}})$$
- **Severity (1–5):** Intrinsic risk of the anomaly typology (e.g., rapid pass-through = 5; fee discrepancy = 2).
- **Likelihood (1–5):** Statistical magnitude of deviation.
- **$\ln(1 + \text{Exposure})$:** Logarithmic damping of monetary exposure to ensure multi-lakh rupee breaches elevate the priority without letting a single billionaire edge-case distort the entire triage queue.
- Incidents are triaged into actionable bands: P1 (Critical, $<15$m SLA), P2 (High, $<2$h SLA), P3 (Medium), and P4 (Low).

---

## 5. BI & Semantic Reconciliation

### Q8: What is cross-system reconciliation, and how did you enforce it?
**Defense:** A common failure in enterprise analytics is discrepancies between analyst Python scripts, database SQL tables, and Power BI dashboards. In `python/reporting/reconciliation.py`, I built an automated zero-tolerance audit that extracts total transactions, GTV, active user count, and fee revenue across all three tiers simultaneously. The audit verifies $0.00\%$ discrepancy within a strict $\pm 0.01$ rupee rounding tolerance, proving absolute end-to-end data integrity.
