# Incident Prioritization & Operational Queue Methodology

This document defines the mathematical scoring mechanism, severity criteria, priority tiers, and prescriptive investigation actions used to triage anomalies in **Exchange Control Desk**.

---

## 1. Prioritization Mathematical Framework

To protect operational teams from alert fatigue and ensure immediate attention on catastrophic exposures, incidents are scored by the following non-linear composite formulation:

$$\text{Priority Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure}_{\text{INR}})$$

### Factor 1: Typology Severity ($S \in \{1, 2, 3, 4, 5\}$)
Reflects the intrinsic regulatory, financial, or system impact of the anomaly pattern:
- **5 (Critical):** `RAPID_PASS_THROUGH` (severe PMLA money-laundering/drain risk), unauthorized high-value withdrawal.
- **4 (High):** `BASELINE_SPIKE` on high-risk accounts, `VELOCITY_BURST` combined with device change.
- **3 (Medium):** `REPEATED_FAILURES` (potential brute force or gateway outage), `ASSET_SPIKE`.
- **2 (Low):** `ABNORMAL_FEE` (fee rate miscalculation or gas spike).
- **1 (Informational):** Minor temporal off-hours activity.

### Factor 2: Detection Likelihood ($L \in \{1, 2, 3, 4, 5\}$)
Reflects statistical confidence and magnitude of the breach:
- **5:** Extreme deviation ($Z \ge 5.0$, or $N_{\text{fails}} \ge 6$, or $\Delta t \le 3\text{m}$).
- **4:** High deviation ($4.0 \le Z < 5.0$, or $N_{\text{tx}} \ge 10$).
- **3:** Moderate deviation ($3.0 \le Z < 4.0$).
- **2:** Borderline breach ($Z \approx 3.0$).
- **1:** Weak signal / low historical sample size.

### Factor 3: Logarithmic Financial Exposure ($\ln(1 + \text{Exposure})$)
Damps extreme monetary variance while ensuring multi-million rupee breaches scale appropriately:
- For ₹10,000 exposure: $\ln(10,001) \approx 9.21$
- For ₹500,000 exposure: $\ln(500,001) \approx 13.12$
- For ₹10,000,000 exposure: $\ln(10,000,001) \approx 16.12$

---

## 2. Priority Band Thresholds & Operational SLAs

| Priority Band | Score Threshold | Operational SLA | Mandatory Triage Action |
| :--- | :--- | :--- | :--- |
| **P1 (Critical)** | $\text{Score} \ge 150$ or (Severity = 5 and Exposure $\ge ₹500,000$) | $< 15$ Minutes | Immediate automated 24h withdrawal freeze; notify Risk Ops Lead; initiate account review. |
| **P2 (High)** | $80 \le \text{Score} < 150$ | $< 2$ Hours | Assign to Senior Fraud Investigator; verify KYC documents and device IP history; inspect counterparty wallet. |
| **P3 (Medium)** | $30 \le \text{Score} < 80$ | $< 8$ Hours | Review batch gateway reconciliation; monitor subsequent 24-hour transactions for repeat signals. |
| **P4 (Low)** | $\text{Score} < 30$ | $< 24$ Hours | Log into operational audit database; aggregate for weekly fee and threshold tuning reviews. |

---

## 3. Prescriptive Recommendation Engine

Every incident generated receives an operational recommendation string selected via decision logic:
- If `RAPID_PASS_THROUGH`: `"Place temporary 24h withdrawal hold; verify bank originator match; request proof of source of funds."`
- If `BASELINE_SPIKE` and `Exposure > 500000`: `"Initiate outbound phone verification; check recent 2FA and password changes; verify order book liquidity impact."`
- If `REPEATED_FAILURES`: `"Check banking partner gateway status; notify user of payment rail maintenance; monitor for credential stuffing."`
- If `ABNORMAL_FEE`: `"Credit excess fee to user account; flag fee calculation service to Data Engineering for contract review."`
- If `ASSET_SPIKE`: `"Review order book market depth; inspect top 5 taker wallets; verify whether global external markets experienced corresponding volume."`
