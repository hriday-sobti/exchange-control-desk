# Power BI Dashboard Specification & User Guide

**Report Title:** VDA Exchange Control Desk  
**Version:** 1.0  
**Semantic Model:** Star-Schema with 1-to-many single-direction relationships  

---

## 1. Five-Page Report Architecture

### Page 1: Executive Overview
- **Business Question:** What is the high-level health, transactional throughput, and risk exposure of the platform?
- **KPI Cards (Top Band):**
  1. `[Total GTV]` (Formatted in INR Crores: `₹#,##0.0,, " Cr"`)
  2. `[Total Transactions]` (Formatted as Integer with thousands separator)
  3. `[Total Active Users]` (Distinct User Count)
  4. `[Success Rate %]` (Target: $>96.0\%$; Conditional formatting green $\ge 95\%$, red $<95\%$)
  5. `[Total Fee Revenue]` (Formatted in INR Lakhs / Crores)
  6. `[Open P1 Incidents]` (Prominent red alert card)
- **Visual 1 (Main Trend):** Daily GTV & Transaction Volume Combo Chart (Bars: Transactions, Line: GTV in INR).
- **Visual 2 (Risk Exposure):** Open Incidents by Priority Band (Donut chart showing P1, P2, P3, P4).
- **Visual 3 (Asset Breakdown):** Top 5 Assets by GTV Share (Horizontal bar chart).

### Page 2: Market & Platform Liquidity
- **Business Question:** Are platform trading volumes aligned with broader crypto market movements or experiencing idiosyncratic liquidity divergence?
- **Visual 1 (Market Trend):** Benchmark Price Trends across BTC, ETH, SOL (Line chart with slicer).
- **Visual 2 (Volume Share):** Platform Volume Share vs Global Market Benchmark (Clustered column).
- **Visual 3 (Divergence Matrix):** Table showing Asset, Platform Avg Price, Market Benchmark Price, Divergence %, and Liquidity Flag.

### Page 3: Transaction & User Behavior
- **Business Question:** How are different customer segments utilizing the exchange across deposit, trading, and withdrawal rails?
- **Visual 1 (Flow Funnel):** Transaction Distribution by Type (Trade vs Deposit vs Withdrawal).
- **Visual 2 (Cohort Analysis):** GTV and User Count by Behavioral Segment (`Retail Casual`, `Active Trader`, `Institutional / HNW`).
- **Visual 3 (Gateway Health):** Success & Failure Rates by Payment Rail (UPI, IMPS, NEFT, On-Chain).

### Page 4: Anomaly / Incident Control Desk (Centerpiece)
- **Business Question:** Which operational exceptions and potential money laundering / fraud risks require immediate analyst intervention?
- **Top Summary:** Open P1 Count, Open P2 Count, Total Financial Exposure at Risk.
- **Visual 1 (Typology Breakdown):** Anomalies Flagged by Typology (`RAPID_PASS_THROUGH`, `BASELINE_SPIKE`, `VELOCITY_BURST`, `REPEATED_FAILURES`, `ABNORMAL_FEE`).
- **Visual 2 (Operational Queue Grid):** Interactive Triage Table with columns:
  - `Incident ID`
  - `Priority Band` (Color badge: P1 Red, P2 Orange, P3 Yellow, P4 Slate)
  - `Priority Score`
  - `User ID`
  - `Anomaly Typology`
  - `Financial Exposure (INR)`
  - `Explanation`
  - `Recommended Action`
- **Slicers:** Date Range, Priority Band, User Segment, Typology.

### Page 5: Data Quality & Governance Desk
- **Business Question:** Can leadership and regulatory bodies trust the data integrity of our analytical tables?
- **Top KPI:** Overall Data Quality Score (0–100.0) Gauge visual.
- **Visual 1 (Dimension Scorecards):** Dimension Scores across Completeness, Validity, Consistency, Uniqueness, Referential Integrity, Timeliness.
- **Visual 2 (Check Level Audit Table):** Full run-level breakdown of all 10+ automated audit assertions, records checked, failure counts, and severity.

---

## 2. Power BI Desktop Import Instructions

1. Open Power BI Desktop.
2. Select **Get Data -> DuckDB / PostgreSQL** (or import the prepared analytical export CSV files from `powerbi/exports/`).
3. Model Relationships:
   - Connect `dim_dates[date_key]` $\rightarrow$ `fact_transactions[date_key]` (1 to Many, Single).
   - Connect `dim_users[user_id]` $\rightarrow$ `fact_transactions[user_id]` (1 to Many, Single).
   - Connect `dim_assets[asset_id]` $\rightarrow$ `fact_transactions[asset_id]` (1 to Many, Single).
   - Connect `fact_anomalies[anomaly_id]` $\rightarrow$ `fact_incidents[anomaly_id]` (1 to 1).
4. Copy the DAX measures from `powerbi/measures/measures.dax`.
5. Apply the enterprise theme from `powerbi/theme/theme.json`.
