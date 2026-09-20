# Non-Functional Requirements (NFR)

This document formalizes performance, security, data integrity, auditability, and operational constraints for **Exchange Control Desk**.

---

## 1. Performance & Scalability (NFR-PERF)
* **NFR-PERF-01 (Throughput):** The feature engineering and anomaly detection pipeline must achieve a minimum processing throughput of $1,000\text{ transactions/second}$ on standard commodity hardware.
* **NFR-PERF-02 (Query Latency):** Analytical views and KPI queries on tables containing $\le 500,000$ records must return results within $<2.0\text{ seconds}$.
* **NFR-PERF-03 (Memory Optimization):** Pipeline executions on standard developer datasets (100,000 transactions) must operate within $\le 2\text{ GB}$ of resident memory.

---

## 2. Data Integrity & Governance (NFR-DATA)
* **NFR-DATA-01 (Zero-Tolerance Reconciliation):** Core operational KPIs (Total Transactions, GTV, Active Users, Fee Revenue) must reconcile across Python, SQL views, and Power BI measures with $0.00\%$ discrepancy.
* **NFR-DATA-02 (Data Quality Gate):** Automated DQ audits must assess 6 dimensions (Completeness, Validity, Consistency, Uniqueness, Timeliness, Referential Integrity) prior to analytical fact table loading.
* **NFR-DATA-03 (Immutability):** Raw ingested market snapshots and synthetic transaction logs must be stored in immutable Parquet format.

---

## 3. Security & Compliance (NFR-SEC)
* **NFR-SEC-01 (Credential Protection):** No secrets, passwords, or API keys may be committed to version control. Configuration must load via `.env` templates.
* **NFR-SEC-02 (PII Minimization):** User identifiers must use synthetic pseudonymous keys (`USR_XXXXX`) without real personally identifiable information.
* **NFR-SEC-03 (Audit Trail):** Every detected anomaly and triaged incident must retain an immutable audit record with timestamps, mathematical deviations, and plain-English causal justifications.

---

## 4. Portability & Reproducibility (NFR-OPS)
* **NFR-OPS-01 (Zero External Dependency Run):** The repository must execute deterministically using embedded DuckDB without requiring root Docker or external database setups.
* **NFR-OPS-02 (Deterministic Seeds):** Fixed random seeds (`seed: 42`) must guarantee reproducible anomaly injections and evaluations across machines.
