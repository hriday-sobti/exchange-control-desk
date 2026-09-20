# Research Log: Exchange Control Desk

This document records all meaningful primary and secondary sources consulted during the development of **EXCHANGE CONTROL DESK (Transaction, Market & Risk Analytics for a VDA Platform)**, logging findings, analytical relevance, and impact on system design.

---

## Record 1: Financial Intelligence Unit - India (FIU-IND) VDA Guidelines

* **Source Title:** AML & CFT Guidelines for Reporting Entities Providing Services Related to Virtual Digital Assets
* **URL:** https://fiuindia.gov.in/pdfs/downloads/VDA08012026.pdf
* **Date Accessed:** 2026-09-20
* **Source Organization:** Financial Intelligence Unit - India (Ministry of Finance, Department of Revenue)
* **Topic:** Prevention of Money Laundering Act (PMLA) obligations for VDA Service Providers (VDASPs)
* **Type:** Primary Source
* **Useful Findings:**
  1. VDASPs in India operate as designated "Reporting Entities" under Section 2(1)(wa) read with Section 2(1)(sa) of the PMLA.
  2. Section 5.2 mandates ongoing transaction monitoring: tracking unusual patterns, transaction velocity, abnormal values relative to customer economic profile, rapid movement between fiat and crypto, and cross-border transfers.
  3. Section 5.3 mandates the FATF "Travel Rule" recording beneficiary and originator information.
  4. Section 5.5 governs Suspicious Transaction Reporting (STR) where transactions have no economic rationale or deviate from normal business.
* **Impact on Project:**
  - Informs our analytical risk detection rules: rapid fiat-to-crypto layering (deposit-to-withdrawal velocity), baseline deviation, and sudden transaction velocity bursts.
  - Dictates that our prototype must be clearly documented as an **operational analytics and risk-monitoring decision support prototype**, not a certified regulatory STR generator or production compliance software.

---

## Record 2: CoinDCX Trust & Transparency Reports & Proof of Reserves

* **Source Title:** CoinDCX Transparency Reports (October 2025 - August 2026 Monthly Reports & Audit Overviews)
* **URL:** https://coindcx.com/blog/transparency-reports
* **Date Accessed:** 2026-09-20
* **Source Organization:** CoinDCX (Primestack Pte Ltd / Neblio Technologies Pvt Ltd)
* **Topic:** Exchange operational statistics, Proof of Reserves (PoR), custody management, user safety
* **Type:** Primary Source
* **Useful Findings:**
  1. Monthly transparency reporting includes reserve-to-liability ratios (>100% backing across top liquid assets: BTC, ETH, USDT, USDC, MATIC/POL, SOL).
  2. Public operational focus centers around: platform uptime, deposit/withdrawal fulfillment latencies, customer ticket resolution, trading volume breakdown by INR and USDT pairs, and regulatory information requests handled.
  3. Strict segregation between hot wallets (operational liquidity for daily automated withdrawals) and multi-sig cold storage custody.
* **Impact on Project:**
  - Guides synthetic data parameters: realistic base currency pairs (INR pairs and USDT pairs), realistic withdrawal/deposit latency distributions, hot/cold liquidity indicators, and reserve sanity checks in data quality.

---

## Record 3: CoinDCX Public Market Data API Specification

* **Source Title:** CoinDCX Public Trading and Market Data API Documentation & Live Endpoints
* **URL:** https://docs.coindcx.com/ & https://api.coindcx.com/exchange/ticker
* **Date Accessed:** 2026-09-20
* **Source Organization:** CoinDCX
* **Topic:** Public ticker, order books, active currency pairs, and 24h market metrics
* **Type:** Primary Source
* **Useful Findings:**
  1. Live public endpoint `https://api.coindcx.com/exchange/ticker` returns 990+ active trading pairs with fields: `market`, `change_24_hour`, `high`, `low`, `volume`, `last_price`, `bid`, `ask`, `timestamp`.
  2. Currency pairs follow conventions: `BTCINR`, `ETHINR`, `USDTINR`, `SOLUSDT`, etc., separating base and target assets.
  3. High data reliability, public unauthenticated access for ticker snapshots.
* **Impact on Project:**
  - Implemented as live external market ingestion in `python/ingestion/market_data.py`.
  - Also establishes a verified offline fallback mechanism caching real snapshots to ensure 100% reproducible pipeline execution in airgapped/test environments.

---

## Record 4: CoinGecko Public Cryptocurrency API

* **Source Title:** CoinGecko API Reference - Market Chart & Historical Asset Metrics
* **URL:** https://docs.coingecko.com/reference/coins-id-market-chart
* **Date Accessed:** 2026-09-20
* **Source Organization:** CoinGecko Inc.
* **Topic:** Benchmark market capitalization, aggregate 24h trading volume, and historical time-series
* **Type:** Primary Source
* **Useful Findings:**
  1. Standard public endpoints provide asset market cap, global volume, and volatility series.
  2. Global market vs platform volume ratio allows detection of platform-specific liquidity anomalies (e.g., when an asset trades abnormally on the platform compared to global markets).
* **Impact on Project:**
  - Modeled in the Market Intelligence engine (`python/reporting/market_intelligence.py`) to quantify market vs exchange divergence.

---

## Record 5: CoinDCX Analytics & Data Engineering Job Requisitions

* **Source Title:** CoinDCX Careers - Data Analyst, Risk Analytics & Engineering Openings
* **URL:** https://careers.coindcx.com/opportunities/openings
* **Date Accessed:** 2026-09-20
* **Source Organization:** CoinDCX Talent Acquisition
* **Topic:** Required analytical competencies, data tooling, stakeholder interaction, and reporting expectations
* **Type:** Primary Source
* **Useful Findings:**
  1. Core technical expectations: Advanced SQL (CTEs, window functions, cohorting, funnel analysis), Python for automation & statistical modeling (pandas, numpy, scipy), and BI dashboards (Power BI / Metabase / Tableau).
  2. Operational problem solving: Root-cause analysis on transaction drop-offs, user behavioral segmentation, monitoring anomalous transactional spikes, fraud/risk rule modeling, and executive KPI reporting.
  3. Business acumen: Clear translation from statistical anomaly detection to prioritized operational workflows that customer support, risk, or product operations can act upon.
* **Impact on Project:**
  - Directly drives `docs/job_alignment.md`, shaping our feature engineering, star schema design, incident prioritization scoring, and dashboard page structure.

---

## Record 6: Basel Committee & FATF Guidance on Anomaly Detection in Financial Transactions

* **Source Title:** FATF Guidance for a Risk-Based Approach to Virtual Assets and VASPs; Basel Committee Working Paper on Anomaly Detection in Payments
* **URL:** https://www.fatf-gafi.org/
* **Date Accessed:** 2026-09-20
* **Source Organization:** Financial Action Task Force (FATF) / Bank for International Settlements (BIS)
* **Topic:** Financial crime typologies, structuring, velocity spikes, and explainability
* **Type:** Primary / Academic Source
* **Useful Findings:**
  1. Black-box ML models are operationally difficult for risk teams because compliance investigators cannot defend an alert without explainable causal factors.
  2. Hybrid analytical architecture (statistically grounded rules + robust Z-score / IQR thresholds + behavioral baselines) yields higher operational precision and full auditability.
  3. Priority of an alert should be a function of: Severity of breach $\times$ Likelihood $\times$ Financial exposure at risk.
* **Impact on Project:**
  - Dictates our incident prioritization model (`Priority Score = Severity * Likelihood * Normalized Financial Exposure`) and requires every anomaly to output a plain-English, causal explanation string.
