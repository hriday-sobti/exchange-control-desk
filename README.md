# EXCHANGE CONTROL DESK
### Transaction, Market & Risk Analytics for a VDA Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL / DuckDB](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20DuckDB-orange.svg)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/BI-Power%20BI%20Semantic%20Model-yellow.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)](tests/)
[![Data Quality](https://img.shields.io/badge/Data%20Quality-100%2F100-success.svg)](outputs/quality/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. What I Built

I built **Exchange Control Desk** to answer a practical operational challenge: **If you were analyzing an expanding Virtual Digital Asset (VDA) exchange, how would you bring live market activity, transactional throughput, automated data quality, anomaly detection, and incident prioritization into one unified, auditable analytical workflow?**

This project is an end-to-end operational analytics desk conceived, researched, designed, tested, and documented to mirror how a Data / Risk Analyst operates within a regulated financial technology platform (modeled on Indian VDA operational standards like CoinDCX and FIU-IND compliance guidelines).

```text
================================================================================
EXCHANGE CONTROL DESK FACT SHEET (MEASURED RUN)
================================================================================
Active Users Modeled:             10,000 Accounts (Retail, Active, Corporate)
Transactions Processed:           101,487 Events (Trades, Deposits, Withdrawals)
Gross Transaction Value (GTV):    ₹3,184,592,938.83 (~₹318.46 Crores INR)
Net Platform Fee Revenue:         ₹3,467,719.86 (~₹34.68 Lakhs INR)
Live Market Pairs Ingested:       995 Ticker Pairs from CoinDCX Public API
Data Quality Score:               100.00 / 100.00 (10 Assertions across 6 Dimensions)
Synthetic Ground Truth Recall:    71.76% Overall (100% on Layering / Rapid Drain)
Total Incidents Triaged:          7,600 Records (Score = Severity * Likelihood * ln(1+E))
High-Priority Exposure (P1/P2):   ₹1,883,501,452.48 (~₹188.35 Crores INR)
Cross-System Reconciliation:      PASSED (0.00% Discrepancy: Python == SQL == BI)
Full Pipeline Execution Time:     77.03 Seconds (1,621.2 tx/s Processing Throughput)
================================================================================
```

---

## 2. Business Problem & Regulatory Context

Operating a cryptocurrency and VDA exchange in India requires strict adherence to the **Prevention of Money Laundering Act, 2002 (PMLA)** and registration as a **Reporting Entity (RE)** with the **Financial Intelligence Unit - India (FIU-IND)**. Under updated Section 5.2 FIU-IND guidelines, exchanges must maintain continuous transaction monitoring to detect:
- Unusual velocity spikes in trading or withdrawals.
- Value deviations from established customer economic baselines.
- Rapid fiat-to-crypto layering (depositing fiat and immediately withdrawing unhosted crypto).
- Consecutive payment gateway failures indicating potential brute-force or system faults.
**Exchange Control Desk** was designed as an internal decision-support prototype to allow operations and risk analysts to investigate transactional anomalies and triage operational incidents before regulatory escalation.
---

## 3. End-to-End System Architecture

```text
       +-------------------------------------------------------------+
       |                     EXTERNAL DATA SOURCES                   |
       |  - CoinDCX Public Ticker API (995 Live Market Pairs)         |
       |  - Verified Offline Fallback Cache                          |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                   DATA GENERATION & INGESTION               |
       |  - Live / Fallback Ingestion (`python/ingestion/`)          |
       |  - 10k Users, 100k+ Transactions (`data/synthetic/`)        |
       |  - 1,430 Controlled Ground-Truth Injected Anomalies         |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               DATA QUALITY & VALIDATION ENGINE              |
       |  - 6 Dimensions: Completeness, Validity, Consistency,        |
       |    Uniqueness, Timeliness, Referential Integrity            |
       |  - Automated Rejection / Quarantine Pipeline                |
       |  - Automated Scorecard: 100.0/100 (`outputs/quality/`)      |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                RELATIONAL STORAGE LAYER                     |
       |  - Embedded DuckDB + ANSI PostgreSQL Schemas                |
       |  - Pure Star Schema (`dim_users`, `dim_assets`,             |
       |    `dim_dates`, `fact_transactions`, `fact_anomalies`)       |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                 SQL TRANSFORMATIONS & VIEWS                 |
       |  - Rolling 24H Volume Windows, User Velocity                |
       |  - Consecutive Failure Islands & Gaps Technique             |
       |  - Analytical Views (`sql/views/analytical_views.sql`)      |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             FEATURE ENGINEERING & ANOMALY ENGINE            |
       |  - Rolling 30-Day Expanding User Baselines (Z-Scores)       |
       |  - IQR Upper Fences on Transaction Fees                     |
       |  - Plain-English Natural Language Explanations              |
       |  - Evaluation vs Ground Truth (Precision & Recall)          |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                INCIDENT PRIORITIZATION QUEUE                |
       |  - Priority Score = Severity * Likelihood * ln(1 + Exposure)|
       |  - Actionable Triage Bands: P1, P2, P3, P4                  |
       |  - Prescriptive Operational Recommendations                 |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                BI SEMANTIC LAYER & REPORTING                |
       |  - 5-Page Power BI Suite Specifications & Theme             |
       |  - Comprehensive DAX Measures Library                       |
       |  - Zero-Tolerance Reconciliation Audit (0.00% Discrepancy)  |
       |  - Executive Decision Summary (`outputs/executive/`)        |
       +-------------------------------------------------------------+
```

---

## 4. Star-Schema Dimensional Data Model

Every table in the database has a strictly documented granularity:
- **`dim_users`:** One row per registered customer account with demographic and initialized risk baselines.
- **`dim_assets`:** One row per supported tradable Virtual Digital Asset.
- **`dim_dates`:** One row per calendar day with fiscal and temporal flags.
- **`fact_transactions`:** One row per discrete deposit, withdrawal, or trade event.
- **`fact_market_ticks`:** One row per market pricing and volume snapshot.
- **`fact_anomalies`:** One row per detected mathematical exception with plain-English explanation.
- **`fact_incidents`:** One row per prioritized operational incident in the triage queue.

---

## 5. Explainable Anomaly Detection & Incident Prioritization

Rather than deploying black-box machine learning models that compliance investigators cannot explain or audit, the system uses explainable statistical baselines:
1. **User Baseline Z-Score:** Computes deviation from the customer's rolling 30-day expanding historical mean. Flags transactions with $Z \ge 3.0$.
2. **Rolling Velocity Counter:** Tracks transactions within a 60-minute sliding window per user. Flags bursts exceeding 5 tx/hour.
3. **Rapid Pass-Through Layering:** Detects fiat deposits immediately followed by crypto withdrawals within 15 minutes with zero intermediate trading.
4. **IQR Fee Fence:** Uses the non-parametric interquartile range ($Q_3 + 1.5 \times \text{IQR}$) to isolate anomalous fees without distortion from skewed distributions.
5. **Repeated Failures Window:** Monitors rolling 30-minute windows for consecutive failed transactions to catch gateway drops and brute-force attempts.

### Incident Prioritization Formula
Incidents are triaged using a non-linear composite risk formulation:
$$\text{Priority Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure}_{\text{INR}})$$

* **P1 (Critical):** Immediate automated 24h withdrawal hold; Risk Ops Lead notified ($<15$m SLA).
* **P2 (High Priority):** Assigned to Senior Fraud Investigator ($<2$h SLA).
* **P3 / P4 (Medium/Low):** Batch gateway reconciliation review and automated monitoring.

---

## 6. Zero-Tolerance KPI Reconciliation

To ensure decision-makers can trust the analytics, the system performs an automated cross-system audit verifying that metrics computed in Python, SQL views, and Power BI DAX match identically:

| KPI Name | Python Value | PostgreSQL / SQL Value | Power BI DAX Target | Difference | Tolerance | Audit Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Transactions** | 101,487 | 101,487 | 101,487 | 0 | 0 | **PASSED** |
| **Total GTV (INR)** | ₹3,184,592,938.83 | ₹3,184,592,938.83 | ₹3,184,592,938.83 | 0.0 | 0.01 | **PASSED** |
| **Active Users** | 10,000 | 10,000 | 10,000 | 0 | 0 | **PASSED** |
| **Completed Transactions** | 97,949 | 97,949 | 97,949 | 0 | 0 | **PASSED** |
| **Fee Revenue (INR)** | ₹3,467,719.86 | ₹3,467,719.86 | ₹3,467,719.86 | 0.0 | 0.01 | **PASSED** |
| **Success Rate (%)** | 96.51% | 96.51% | 96.51% | 0.0 | 0.01 | **PASSED** |

---

## 7. How to Run & Reproduce

### Prerequisites
- Python 3.10+
- (Optional) PostgreSQL / Docker (Embedded DuckDB runs out-of-the-box with zero setup)

### Setup & Execution
```bash
# 1. Clone the repository
git clone https://github.com/your-username/exchange-control-desk.git
cd exchange-control-desk

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated test suite (12 tests)
python -m pytest tests/

# 4. Execute the complete end-to-end pipeline (Ingestion -> DQ -> DB -> Anomaly -> Reports)
python -m scripts.run_pipeline

# 5. Run performance benchmarks
python -m scripts.benchmark
```

All generated analytical tables, reports, charts, and queues are published automatically to `outputs/` and `powerbi/exports/`.

---

## 8. Repository Structure

```text
exchange-control-desk/
├── README.md                      # Executive Project Case Study
├── LICENSE                        # MIT License
├── pyproject.toml                 # Project metadata & pytest configuration
├── requirements.txt               # Core Python dependencies
├── .env.example                   # Environment configuration template
├── docker-compose.yml             # Optional PostgreSQL Docker environment
│
├── config/
│   └── project_config.yaml        # Externalized pipeline & threshold parameters
│
├── data/                          # Data directory (gitignored large files)
│   ├── raw/                       # Cached market and reference data
│   ├── synthetic/                 # Generated users, transactions, ground truth
│   └── processed/                 # DuckDB database and processed artifacts
│
├── python/
│   ├── ingestion/                 # CoinDCX API fetcher & synthetic generator
│   ├── validation/                # 6-dimension automated data quality engine
│   ├── feature_engineering/       # Rolling baselines, velocity, and IQR fences
│   ├── anomaly_detection/         # Explainable rules & synthetic evaluator
│   ├── incidents/                 # Risk scoring & prioritization engine
│   ├── reporting/                 # Market intelligence, executive reporting & reconciliation
│   └── common/                    # Database connectors, config, and logging
│
├── sql/
│   ├── schema/create_tables.sql   # Relational DDL for PostgreSQL / DuckDB
│   ├── views/analytical_views.sql # Analytical reporting views
│   ├── transformations/           # Rolling 24h, failure islands & gaps queries
│   └── kpis/                      # Core executive KPI reconciliation queries
│
├── requirements/                  # Formal BRD, FRD, and Stakeholder Matrix
├── docs/                          # Comprehensive technical documentation & audit trails
│   ├── research_log.md            # Primary sources consulted
│   ├── job_alignment.md           # JD alignment matrix
│   ├── vda_regulatory_context.md  # Indian VDA & FIU-IND regulatory study
│   ├── data_model.md              # Star schema specifications & grains
│   ├── data_dictionary.md         # Full column-level definitions
│   ├── kpi_dictionary.md          # Mathematical KPI formulas
│   ├── anomaly_methodology.md     # Anomaly typologies & ground truth specs
│   ├── incident_prioritization.md # Scoring logic & operational SLAs
│   ├── interview_guide.md         # Technical architecture & operational defense
│   ├── performance.md             # Benchmark execution metrics
│   └── final_project_audit.md     # Master verification checklist
│
├── powerbi/                       # Power BI Semantic Model & Report Artifacts
│   ├── measures/measures.dax      # Complete DAX measures library
│   ├── theme/theme.json           # Dark navy enterprise color theme
│   └── exports/                   # Clean star-schema CSV exports for Power BI
│
├── tests/                         # Unit, integration, and failure test suites
├── outputs/                       # Final analytical outputs, charts, and queues
└── scripts/                       # Executable runners (`run_pipeline.py`, `benchmark.py`)
```

---

## 9. Key Learnings & Engineering Takeaways

1. **Domain Context Prevents Misleading Alerts:** In financial transactions, population-wide static thresholds produce massive false positive rates because legitimate high-net-worth users naturally transact in multi-lakh amounts. Grounding detection in **individual rolling baselines** dramatically improved detection precision while preserving recall on true anomalies.
2. **Actionability Over Volume:** Triaging 7,600 anomalies into a prioritized queue via $S \times L \times \ln(1+E)$ demonstrated that analytics must bridge directly into operational workflow. An operations team cannot review 7,000 unranked alerts; they can readily resolve 627 P1 alerts within a 15-minute SLA.
3. **Data Quality Feeds Trust:** Building automated assertions across 6 dimensions ensured that corrupted feeds never reach the analytical warehouse, guaranteeing that management decisions are grounded in verified data.
