# Business Requirements Document (BRD)

**Project:** Exchange Control Desk  
**Subtitle:** Transaction, Market & Risk Analytics for a VDA Platform  
**Version:** 1.0  
**Date:** 2026-09-20  

---

## 1. Executive Problem Statement
Virtual Digital Asset (VDA) exchanges operate in high-throughput, volatile environments subject to operational risks, payment gateway drop-offs, rapid fraud schemes, and stringent FIU-IND compliance obligations under PMLA. Operations, risk, and analytics teams currently face fragmented visibility across separate tools, leading to noisy alerts, delayed fraud interventions, untracked data quality degradation, and unaligned executive reporting.

**Exchange Control Desk** provides an integrated operational analytics desk unifying market liquidity, exchange transaction flows, data quality assurance, statistical anomaly detection, and risk-prioritized incident triage into a single auditable system.

---

## 2. Core Business Requirements

### BR-01: Centralized Exchange Activity Visibility
- **Business Problem:** Leadership and operations lack a consolidated single-pane-of-glass view of daily transactional throughput, gross transaction value (GTV), active trading cohorts, and platform fee revenues.
- **Requirement:** Provide real-time and historical aggregations of total volume, transactions, GTV, and net revenue sliced by asset, transaction type, and payment rail.
- **Primary Stakeholders:** Executive Leadership, Head of Operations, Finance.
- **Key KPIs:** Total Transactions, Total GTV (INR), Active Users (DAU/MAU), Fee Revenue (INR).
- **Acceptance Criteria:** Daily metrics reflect 100% of completed transactions with sub-second analytical query response.

### BR-02: Market Intelligence & Platform Divergence Monitoring
- **Business Problem:** Platform management cannot readily identify when internal volume surges or liquidity dry-ups are organic reflections of global crypto market trends vs. idiosyncratic platform anomalies.
- **Requirement:** Integrate public market benchmarks (prices, global volume, volatility) and track platform-to-market divergence metrics for all supported assets.
- **Primary Stakeholders:** Product Management, Trading Desk, Risk Operations.
- **Key KPIs:** Platform Market Share, Price Divergence %, Volume Volatility Ratio.
- **Acceptance Criteria:** Market data updates via live API or cached benchmark feeds; divergence flags trigger when platform volume deviates by $>3\sigma$ from global market correlation.

### BR-03: Statistical Anomaly Detection in User & Transaction Behavior
- **Business Problem:** Static rule-based alerts either miss sophisticated fraud/structuring or overwhelm analysts with thousands of false positives.
- **Requirement:** Implement a multi-tier detection engine combining domain rules (velocity limits, repeated failures, rapid pass-throughs) with user-specific rolling 30-day statistical baselines (Z-score and IQR).
- **Primary Stakeholders:** Risk Operations, AML/CFT Analysts, Security Operations.
- **Key KPIs:** Anomaly Volume, False Positive Rate, Detection Precision, Detection Recall.
- **Acceptance Criteria:** Every anomaly must produce a human-readable mathematical explanation and reference ground-truth baseline values.

### BR-04: Risk-Based Incident Prioritization & Investigation Queue
- **Business Problem:** Analysts suffer from alert fatigue when presented with flat, unranked alert feeds, risking delayed review of high-exposure threats.
- **Requirement:** Automatically aggregate and score anomalies into prioritized operational incidents using a composite function of Typology Severity, Detection Likelihood, and Financial Exposure ($S \times L \times \ln(1 + \text{Exposure})$), categorizing into P1 (Critical), P2 (High), P3 (Medium), and P4 (Low) triage bands.
- **Primary Stakeholders:** Risk Operations Lead, Fraud Investigators, Support Leads.
- **Key KPIs:** Open P1/P2 Count, Mean Time to Triage, Total Financial Exposure at Risk.
- **Acceptance Criteria:** Actionable queue output with recommended investigation steps and direct user/transaction links.

### BR-05: Automated Data Quality & Pipeline Integrity Monitoring
- **Business Problem:** Corrupted, missing, or delayed transactional records silently distort financial KPIs and lead to compliance reporting errors.
- **Requirement:** Build an automated data quality engine assessing 6 core dimensions: Completeness, Validity, Consistency, Uniqueness, Timeliness, and Referential Integrity, calculating a weighted Data Quality Score (0–100%).
- **Primary Stakeholders:** Data Engineering, Head of Analytics, Compliance.
- **Key KPIs:** Data Quality Score (%), Critical Validation Failure Rate, Quarantined Records.
- **Acceptance Criteria:** Pipeline automatically quarantines invalid records before fact table loading and outputs an auditable run-level DQ report.

### BR-06: Operational Root-Cause Investigation Support
- **Business Problem:** Front-line support and risk teams spend hours tracing the root cause of transaction drops or failed fiat settlements.
- **Requirement:** Classify transactional anomalies and failures into diagnostic categories (Behavioral, Transactional, Market, Data Quality, Process/System) with supporting contextual metrics.
- **Primary Stakeholders:** Operations Support, Product Ops, Engineering.
- **Key KPIs:** Failure Rate by Gateway, Error Typology Breakdown.
- **Acceptance Criteria:** Categorization logic traceable in analytical SQL views.

### BR-07: Executive & Operational Business Intelligence Reporting
- **Business Problem:** Disconnected dashboards across departments lead to conflicting KPI figures in leadership meetings.
- **Requirement:** Deliver a 5-page Power BI reporting suite (Executive Overview, Market & Platform, Transaction & User Behavior, Anomaly & Incident Desk, Data Quality) powered by a single star-schema semantic model.
- **Primary Stakeholders:** C-Suite, Department Heads, Operational Leads.
- **Key KPIs:** Standardized across all 5 pages.
- **Acceptance Criteria:** Reports refresh seamlessly with drill-through capability from high-level KPIs to individual incident queue records.

### BR-08: Cross-Functional Ad-Hoc Analytics Support
- **Business Problem:** Analytics teams are bogged down by repetitive ad-hoc requests for user segmentation and cohort retention.
- **Requirement:** Provide pre-computed analytical views and behavioral user segmentation (Retail Casual, Active Trader, High-Net-Worth / Institutional) in relational storage.
- **Primary Stakeholders:** Marketing, Product Growth, Finance.
- **Key KPIs:** Cohort Volume Share, Segment Transition Velocity.
- **Acceptance Criteria:** Standardized SQL views documented in data dictionary.

### BR-09: End-to-End Reproducibility & Audit Trail
- **Business Problem:** Complex analytics models often fail outside the developer's local machine, preventing independent audit and validation.
- **Requirement:** Full pipeline must execute deterministically from a single CLI command with clear logging and zero reliance on unversioned external state.
- **Primary Stakeholders:** Technical Reviewers, Auditors, Internal Engineering.
- **Key KPIs:** Pipeline Execution Time, Unit Test Pass Rate (100%).
- **Acceptance Criteria:** End-to-end pipeline executes cleanly and all unit/integration tests pass.

### BR-10: Cross-System KPI Reconciliation Traceability
- **Business Problem:** Discrepancies between Python analytical notebooks, database tables, and Power BI dashboards undermine decision-maker trust.
- **Requirement:** Automated reconciliation verification comparing KPIs across Python, SQL views, and Power BI measures, enforcing a zero-tolerance ($0.00\%$ discrepancy) rule for deterministic counts and values.
- **Primary Stakeholders:** Internal Audit, Finance, Analytics Lead.
- **Key KPIs:** Discrepancy % (must be $0.00\%$).
- **Acceptance Criteria:** Automated reconciliation report published to `outputs/reconciliation/` verifying consistency.
