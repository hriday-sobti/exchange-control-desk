# Data Dictionary: Exchange Control Desk

This document defines all entities, columns, data types, nullability, constraints, and business meanings across staging, dimensional, fact, and analytical tables.

---

## 1. Dimension: `dim_users`
- **user_id** (`VARCHAR(32)`, PK, NOT NULL): Unique alphanumeric identifier for the registered user (e.g., `USR_00001`).
- **signup_date** (`DATE`, NOT NULL): Registration date of the user account.
- **country** (`VARCHAR(3)`, NOT NULL): ISO-3166 alpha-3 country code (e.g., `IND`, `ARE`, `SGP`).
- **user_segment** (`VARCHAR(20)`, NOT NULL): Analytical behavioral tier (`Retail Casual`, `Active Trader`, `Institutional / HNW`).
- **account_type** (`VARCHAR(15)`, NOT NULL): Account verification level (`Individual_Tier1`, `Individual_Tier2_KYC`, `Corporate`).
- **risk_tier** (`VARCHAR(10)`, NOT NULL): Initial onboarded risk rating (`Low`, `Medium`, `High`).

---

## 2. Dimension: `dim_assets`
- **asset_id** (`VARCHAR(16)`, PK, NOT NULL): Canonical asset identifier (e.g., `BTC`, `ETH`, `USDT`, `SOL`, `POL`, `XRP`).
- **symbol** (`VARCHAR(16)`, NOT NULL): Asset ticker symbol.
- **name** (`VARCHAR(64)`, NOT NULL): Full asset name (e.g., `Bitcoin`, `Ethereum`, `Tether USD`).
- **category** (`VARCHAR(32)`, NOT NULL): Fundamental sector (`Layer 1`, `Layer 2`, `Stablecoin`, `DeFi`, `Payment`).
- **is_stablecoin** (`BOOLEAN`, NOT NULL): Flag indicating whether asset is pegged to fiat currency (`TRUE`, `FALSE`).

---

## 3. Fact: `fact_transactions`
- **transaction_id** (`VARCHAR(36)`, PK, NOT NULL): Unique UUID for the transaction event.
- **user_id** (`VARCHAR(32)`, FK, NOT NULL): Reference to `dim_users.user_id`.
- **asset_id** (`VARCHAR(16)`, FK, NOT NULL): Reference to `dim_assets.asset_id`.
- **date_key** (`INTEGER`, FK, NOT NULL): Surrogate date key in `YYYYMMDD` format.
- **timestamp** (`TIMESTAMP WITH TIME ZONE`, NOT NULL): UTC ISO-8601 execution timestamp.
- **transaction_type** (`VARCHAR(15)`, NOT NULL): Operation type (`DEPOSIT`, `WITHDRAWAL`, `TRADE`).
- **side** (`VARCHAR(4)`, NULLABLE): Order side for trades (`BUY`, `SELL`, or NULL for deposits/withdrawals).
- **quantity** (`NUMERIC(24, 8)`, NOT NULL): Asset quantity traded or transferred ($>0$).
- **price** (`NUMERIC(18, 4)`, NOT NULL): Unit execution price in base fiat currency (INR) ($\ge 0$).
- **gross_value** (`NUMERIC(18, 2)`, NOT NULL): Gross nominal value before fee deduction ($= \text{quantity} \times \text{price}$).
- **fee** (`NUMERIC(18, 2)`, NOT NULL): Platform fee assessed in INR ($\ge 0$).
- **net_value** (`NUMERIC(18, 2)`, NOT NULL): Net value credited/debited after fee adjustment.
- **status** (`VARCHAR(15)`, NOT NULL): Lifecycle state (`COMPLETED`, `FAILED`, `CANCELLED`).
- **payment_method** (`VARCHAR(20)`, NOT NULL): Payment or transfer rail (`IMPS`, `UPI`, `NEFT`, `ON_CHAIN_TRANSFER`, `INTERNAL_MATCH`).
- **device_type** (`VARCHAR(10)`, NOT NULL): Client device (`MOBILE_APP`, `WEB_PORTAL`, `API_KEY`).

---

## 4. Fact: `fact_anomalies`
- **anomaly_id** (`VARCHAR(36)`, PK, NOT NULL): Unique identifier for detected exception.
- **transaction_id** (`VARCHAR(36)`, FK, NULLABLE): Associated transaction identifier.
- **user_id** (`VARCHAR(32)`, FK, NOT NULL): Target user identifier.
- **timestamp** (`TIMESTAMP WITH TIME ZONE`, NOT NULL): Anomaly detection timestamp.
- **anomaly_type** (`VARCHAR(40)`, NOT NULL): Typology code (`VELOCITY_BURST`, `BASELINE_SPIKE`, `REPEATED_FAILURES`, `RAPID_PASS_THROUGH`, `ABNORMAL_FEE`, `ASSET_SPIKE`).
- **metric_name** (`VARCHAR(32)`, NOT NULL): The mathematical variable assessed (e.g., `rolling_zscore`, `tx_per_hour`).
- **observed_value** (`NUMERIC(18, 4)`, NOT NULL): The actual measured value.
- **baseline_value** (`NUMERIC(18, 4)`, NOT NULL): The expected baseline or threshold value.
- **deviation_score** (`NUMERIC(10, 2)`, NOT NULL): Standardized deviation magnitude (e.g., Z-score or multiplier).
- **detector_method** (`VARCHAR(30)`, NOT NULL): Methodology used (`Z_SCORE`, `IQR_FENCE`, `TIME_WINDOW_RULE`, `STATE_MACHINE`).
- **explanation** (`TEXT`, NOT NULL): Plain-English causal narrative explaining why this record was flagged.

---

## 5. Fact: `fact_incidents`
- **incident_id** (`VARCHAR(36)`, PK, NOT NULL): Unique identifier for the operational incident.
- **anomaly_id** (`VARCHAR(36)`, FK, NOT NULL): Primary triggering anomaly.
- **created_at** (`TIMESTAMP WITH TIME ZONE`, NOT NULL): Incident triage timestamp.
- **severity** (`INTEGER`, NOT NULL): Qualitative risk scale (1 to 5).
- **likelihood** (`INTEGER`, NOT NULL): Detection confidence score (1 to 5).
- **exposure_inr** (`NUMERIC(18, 2)`, NOT NULL): Estimated financial capital at risk in INR.
- **priority_score** (`NUMERIC(10, 2)`, NOT NULL): Composite score ($S \times L \times \ln(1 + \text{Exposure})$).
- **priority_band** (`VARCHAR(4)`, NOT NULL): Operational priority (`P1`, `P2`, `P3`, `P4`).
- **rationale** (`TEXT`, NOT NULL): Operational justification for priority classification.
- **recommendation** (`TEXT`, NOT NULL): Prescriptive next steps for operational investigator.
- **status** (`VARCHAR(15)`, NOT NULL): Triage status (`OPEN`, `IN_REVIEW`, `RESOLVED`, `FALSE_POSITIVE`).
