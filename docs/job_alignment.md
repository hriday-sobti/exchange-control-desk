# Operational Role Competency Matrix: Exchange Control Desk

This document maps the core functional capabilities, technical competencies, and operational workflows of **Exchange Control Desk** to industry standards for Risk & Operational Data Analytics on a Virtual Digital Asset (VDA) exchange.

---

## Analytical & Engineering Capability Matrix

| Operational Competency | Industry / Domain Context | System Implementation | Verification Artifacts |
| :--- | :--- | :--- | :--- |
| **Advanced SQL & Relational Transformations** | Extracting operational KPIs, cohorting active users, calculating rolling metrics and funnel drop-offs across large transaction sets. | Implements a robust SQL transformation layer using CTEs, window functions (`ROW_NUMBER`, `DENSE_RANK`, `LAG`, `LEAD`, rolling 24h ranges), and conditional aggregations. | `sql/transformations/operational_analytics.sql`<br>`sql/views/analytical_views.sql`<br>`sql/kpis/executive_kpis.sql` |
| **Python Data Pipelines & Statistical Modeling** | Ingesting external APIs, validating ingestion pipelines, computing statistical baselines, and automating risk detection. | End-to-end modular Python architecture: live API fetchers, data cleaning, Z-score / IQR calculations, rolling user baselines, and evaluation engines. | `python/ingestion/`<br>`python/cleaning/`<br>`python/feature_engineering/`<br>`python/anomaly_detection/` |
| **Data Modeling & Dimensional Architecture** | Structuring complex transactional events into reliable analytical structures for scalable querying and BI reporting. | Production-grade Star Schema with clear grain definition for every fact and dimension (`fact_transactions`, `fact_market_ticks`, `dim_users`, `dim_assets`, `dim_dates`, `fact_anomalies`). | `sql/schema/create_tables.sql`<br>`docs/data_model.md`<br>`docs/data_model.png` |
| **Data Quality & Governance** | Ensuring financial records and operational feeds are complete, consistent, timely, and free of anomalies. | Automated 6-dimension data quality engine evaluating Completeness, Validity, Consistency, Uniqueness, Timeliness, and Referential Integrity with composite DQ scoring. | `python/validation/data_quality.py`<br>`outputs/quality/data_quality_report.json`<br>`docs/data_quality_methodology.md` |
| **Transaction Monitoring & Risk Analytics** | Identifying unusual activity, suspicious velocity spikes, rapid fiat-crypto layering, and abnormal fee or failure rates. | Multi-tier anomaly detection engine combining domain rules, Z-scores, rolling baselines, and IQR with ground-truth synthetic evaluation (Precision, Recall, F1). | `python/anomaly_detection/engine.py`<br>`python/anomaly_detection/evaluator.py`<br>`outputs/anomalies/anomaly_evaluation.csv` |
| **Incident Prioritization & Operational Queuing** | Helping operations and risk teams cut through noisy alerts to investigate highest-risk incidents first. | Prioritization engine ranking incidents via $\text{Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure})$ into actionable P1/P2/P3/P4 triage queues with recommended actions. | `python/incidents/prioritization.py`<br>`outputs/incidents/investigation_queue.csv`<br>`docs/incident_prioritization.md` |
| **Market Intelligence & Platform Divergence** | Evaluating whether platform trading patterns reflect broader market trends or represent idiosyncratic liquidity risks. | Market intelligence engine analyzing price momentum, volatility, and volume divergence between platform order books and external market benchmarks. | `python/reporting/market_intelligence.py`<br>`docs/market_intelligence.md` |
| **Business Intelligence & Executive Storytelling** | Communicating operational status, platform liquidity, risk exposures, and data integrity to leadership. | 5-Page Power BI architecture with comprehensive DAX measures, star-schema semantic model, and executive summary reports. | `powerbi/measures/measures.dax`<br>`docs/dashboard_guide.md`<br>`outputs/executive/executive_summary.md` |
| **Cross-System KPI Reconciliation** | Ensuring management dashboards, warehouse tables, and analytical scripts report identical numbers. | Automated reconciliation audit script comparing Python, SQL, and BI outputs against strict zero-tolerance thresholds. | `python/reporting/reconciliation.py`<br>`docs/dashboard_reconciliation.md` |
| **Reproducibility & Engineering Rigor** | Ensuring code is maintainable, tested, documented, and easily deployed across environments. | Full suite of 183 unit, integration, and failure tests; single CLI runner (`python -m scripts.run_pipeline`); configuration via YAML and `.env`. | `tests/`<br>`scripts/run_pipeline.py`<br>`config/project_config.yaml` |

---

## Analytical Maturity Tiers

1. **Descriptive:** What is happening on the platform? (GTV, Active Users, Transaction Velocity, Success Rates).
2. **Diagnostic:** Why did a transaction fail or spike? (Root-cause classification, fee deviation, rapid deposit-to-withdrawal sequence).
3. **Predictive / Detection:** Which behaviors diverge statistically from historic baselines? (Rolling 30-day expanding Z-scores, IQR outlier detection).
4. **Prescriptive:** What should the operational investigator do next? (Ranked investigation queue with concrete next steps: e.g., freeze withdrawal, inspect KYC, review liquidity balance).
