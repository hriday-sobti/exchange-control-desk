# Business Rules: Exchange Control Desk

This document enumerates the core operational business rules governing transaction processing, threshold triggers, incident lifecycle states, and escalation pathways.

---

## 1. Transaction & Ledger Rules
* **BR-RULE-01 (Balance Equation):** For every trade, gross transaction value must satisfy $\text{gross\_value} \approx \text{quantity} \times \text{price}$ within an operational rounding tolerance of $\pm 1.0\%$.
* **BR-RULE-02 (Fee Deductions):** Platform fee must be non-negative ($\ge ₹0.00$). Maker/taker fees on trades are assessed at 0.15% for retail accounts and 0.08% for institutional accounts.
* **BR-RULE-03 (Terminal States):** Transactions reaching `COMPLETED`, `FAILED`, or `CANCELLED` status are immutable and cannot transition to any other state.

---

## 2. Risk & Anomaly Rules
* **BR-RULE-04 (Rolling Baseline Anomaly):** A transaction whose value exceeds the user's rolling 30-day expanding historical mean by $\ge 3.0\sigma$ is flagged as a `BASELINE_SPIKE`.
* **BR-RULE-05 (Velocity Burst):** Any user executing $\ge 5$ transactions within a 60-minute sliding window triggers a `VELOCITY_BURST` exception.
* **BR-RULE-06 (Rapid Pass-Through):** A withdrawal requested within $\le 15$ minutes of a fiat deposit with no intermediate trades triggers a `RAPID_PASS_THROUGH` exception.
* **BR-RULE-07 (Gateway Failure Burst):** An account suffering $\ge 2$ consecutive failed transactions within 30 minutes triggers a `REPEATED_FAILURES` exception.
* **BR-RULE-08 (Abnormal Fee Fence):** Any fee exceeding the asset's non-parametric upper fence ($Q_3 + 1.5 \times \text{IQR}$) triggers an `ABNORMAL_FEE` exception.

---

## 3. Incident Lifecycle & SLA Rules
* **BR-RULE-09 (P1 Critical Escalation):** Any incident with $\text{Priority Score} \ge 150.0$ or a high-severity typology with exposure $\ge ₹500,000$ is designated **P1 Critical**. Mandatory automated 24h withdrawal hold and $<15$-minute triage SLA.
* **BR-RULE-10 (P2 High Escalation):** Incidents with score $80.0 \le \text{Score} < 150.0$ are designated **P2 High** and assigned to senior fraud investigators with a $<2$-hour triage SLA.
* **BR-RULE-11 (Zero Contamination Gate):** Transactions failing any critical data quality validation check (completeness, validity, referential integrity) are quarantined and blocked from populating downstream analytical fact tables.
