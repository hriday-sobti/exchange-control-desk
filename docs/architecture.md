# Architecture Overview: Exchange Control Desk

This document details the end-to-end multi-tier architecture, data lifecycle boundaries, and component interactions.

---

## 1. Multi-Tier Architecture Diagram

```text
+---------------------------------------------------------------------------------------+
|                                TIER 1: INGESTION LAYER                                |
|  - Live CoinDCX Market API (995 active ticker pairs) + Resilient Offline Benchmark    |
|  - Synthetic Exchange Engine (10,000 users, 101,487 transactions, 3 cohorts)         |
|  - Anomaly Injection Engine (1,430 ground-truth anomalies labeled across 6 typologies)|
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                           TIER 2: DATA QUALITY & GOVERNANCE                           |
|  - Automated 6-Dimension Assertions: Completeness, Validity, Consistency,             |
|    Uniqueness, Referential Integrity, Timeliness                                      |
|  - Automated Quarantine Pipeline & 100.0/100 Composite Scorecard                      |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                       TIER 3: RELATIONAL WAREHOUSE & SQL ENGINE                       |
|  - ANSI PostgreSQL DDL + Embedded DuckDB (Zero external infrastructure required)     |
|  - Pure Star Schema: dim_users, dim_assets, dim_dates, fact_transactions,             |
|    fact_market_ticks, fact_anomalies, fact_incidents                                  |
|  - Advanced SQL Transformations: Rolling 24h windows, Consecutive Failure Islands    |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                    TIER 4: FEATURE ENGINEERING & ANOMALY ENGINE                       |
|  - Rolling 30-day expanding user baselines & Z-scores                                 |
|  - 60-minute sliding window transaction velocity counters                             |
|  - Non-parametric IQR upper fences on transaction fees                               |
|  - Causal natural-language explanation generation for every flagged exception         |
|  - Synthetic ground-truth evaluation (Precision, Recall, F1)                          |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                       TIER 5: INCIDENT PRIORITIZATION & QUEUE                         |
|  - Priority Score = Severity * Likelihood * ln(1 + Exposure)                          |
|  - Triage Bands: P1 Critical (<15m SLA), P2 High (<2h SLA), P3 Medium, P4 Low        |
|  - Prescriptive operational recommendations attached to each incident                 |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                     TIER 6: BI SEMANTIC LAYER & RECONCILIATION                        |
|  - 5-Page Power BI Report Suite specifications & Enterprise Dark Navy Theme          |
|  - Complete DAX measures library (Executive, Risk, DQ, Time Intelligence)             |
|  - Cross-system Zero-Tolerance KPI Reconciliation (Python == SQL == Power BI)         |
+---------------------------------------------------------------------------------------+
```
