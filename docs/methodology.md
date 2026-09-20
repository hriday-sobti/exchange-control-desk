# System Methodology: Exchange Control Desk

This document outlines the end-to-end analytical methodology connecting data ingestion, quality validation, feature extraction, anomaly detection, incident triage, and executive reporting.

---

## 1. End-to-End Analytical Lifecycle

1. **Acquisition & Market Benchmarking:** Ingest live 24h ticker pairs from CoinDCX's public API to anchor asset pricing to genuine exchange conditions.
2. **Behavioral Generation:** Synthesize a multi-segment customer population (Retail, Active, Institutional) and transaction streams with realistic diurnal rhythms and baseline failure distributions.
3. **Controlled Ground-Truth Injection:** Inject 1.5% labeled anomaly typologies to evaluate detector precision and recall objectively.
4. **Data Quality Gate:** Apply 10 automated assertions across 6 dimensions. Quarantine failing records to prevent downstream KPI distortion.
5. **Relational Staging & SQL Transformations:** Load clean data into a star schema (PostgreSQL / DuckDB). Compute rolling 24h volumes and consecutive failure runs using window functions and CTEs.
6. **Feature Engineering:** Calculate user rolling expanding baselines, time deltas, velocity counts, and fee quartile fences.
7. **Explainable Anomaly Detection:** Flag statistical and rule-based deviations. Output human-readable causal narratives explaining baseline vs. observed values.
8. **Synthetic Benchmark Evaluation:** Compute confusion matrices, Precision, Recall, and F1 scores against ground truth.
9. **Incident Prioritization Engine:** Score anomalies via $\text{Priority Score} = S \times L \times \ln(1+E)$ and sort into actionable P1–P4 operational queues.
10. **Market Intelligence & User Cohorting:** Quantify platform vs. market volume share and price spreads; segment user behavior into volume/frequency tiers.
11. **BI Semantic Model & DAX:** Build star-schema Power BI models with production DAX measures.
12. **Cross-System KPI Reconciliation:** Assert $0.00\%$ discrepancy across Python, SQL views, and Power BI measures.
