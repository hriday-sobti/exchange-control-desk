# Analytical Method Selection & Mathematical Rationale

This document details why specific statistical and analytical techniques were chosen for anomaly detection, feature engineering, and operational risk scoring in **Exchange Control Desk**, including formulas, assumptions, limitations, and rejected alternatives.

---

## 1. Summary of Selected Methods

| Analytical Technique | Target Metric / Entity | Why Chosen | Rejected Alternative | Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **Rolling User Baseline Z-Score** | Individual transaction gross value vs. 30-day user mean | Directly isolates sudden, uncharacteristic spikes for a given user account while respecting differing wealth profiles. | Static population Z-score (fails because legitimate high-net-worth users are constantly flagged). | Assumes normal/symmetric distribution around the rolling mean; requires sufficient history ($N \ge 5$). |
| **Interquartile Range (IQR) Rule** | Asset-level trade size & fee anomalies | Non-parametric; highly robust to heavy-tailed and skewed financial distributions. | Standard deviation (overly sensitive to extreme outliers, distorting mean). | Less sensitive to subtle drift; fixed multiplier ($1.5 \times \text{IQR}$) requires domain calibration. |
| **Rolling Time-Window Velocity Counters** | Transaction frequency ($N$ tx per 60 min window) | Essential for detecting automated credential stuffing, bot scraping, or rapid layering attacks. | Batch daily count (too slow; operational damage occurs in minutes). | Requires sliding-window state tracking; boundary effects at start of analysis. |
| **Sequential State Transition Timing** | Deposit-to-withdrawal latency ($\Delta t \le 15 \text{ min}$) | Pinpoints rapid pass-through / structuring behavior with zero economic trading rationale. | Global volume anomaly detectors (misses account-level rapid pass-throughs). | Legitimate urgent transfers may trigger false positives without secondary context. |
| **Risk-Based Incident Prioritization** | Composite Incident Score ($S \times L \times E$) | Converts hundreds of statistical anomalies into an actionable, sorted operational triage queue. | Unranked alert lists (causes alert fatigue and missed critical incidents). | Subjective calibration of qualitative severity scales; requires ongoing tuning. |

---

## 2. Mathematical Formulations

### A. Rolling Baseline Z-Score ($Z_{i, u}$)
For a user $u$ with rolling historical transaction values $X_{u} = \{x_{1}, x_{2}, \dots, x_{k}\}$ over a lookback window $W$ (default: 30 days or prior $k \ge 5$ transactions):

$$\mu_{u} = \frac{1}{k} \sum_{j=1}^{k} x_{j}, \quad \sigma_{u} = \sqrt{\frac{1}{k-1} \sum_{j=1}^{k} (x_{j} - \mu_{u})^2}$$

$$Z_{i, u} = \frac{x_{i} - \mu_{u}}{\max(\sigma_{u}, \epsilon)}$$

*Where $\epsilon = 1.0$ prevents division by zero in zero-variance sequences.*  
*Flag condition:* $|Z_{i, u}| \ge 3.0$.

### B. Interquartile Range (IQR) Fence
For skewed distributions such as transaction fees:

$$\text{IQR} = Q_{3} - Q_{1}$$

$$\text{Upper Fence} = Q_{3} + 1.5 \times \text{IQR}$$

*Flag condition:* $x_{i} > \text{Upper Fence}$.

### C. Incident Prioritization Scoring
To determine operational queue position:

$$\text{Priority Score} = \text{Severity} \times \text{Likelihood} \times \ln(1 + \text{Exposure})$$

Where:
- $\text{Severity} \in [1, 5]$: Intrinsic risk of the anomaly typology (e.g., rapid deposit-withdrawal = 5; fee discrepancy = 2).
- $\text{Likelihood} \in [1, 5]$: Confidence of detection based on deviation magnitude (e.g., $Z > 4.5 \rightarrow 5$).
- $\text{Exposure}$: Gross financial value at risk in INR.
- Priority Bands:
  - **P1 (Critical):** $\text{Score} \ge 150$ or immediate high-risk rapid drain $\ge ₹500,000$.
  - **P2 (High):** $80 \le \text{Score} < 150$.
  - **P3 (Medium):** $30 \le \text{Score} < 80$.
  - **P4 (Low):** $\text{Score} < 30$.

---

## 3. Why Deep Learning / Black-Box ML Was Rejected for Core Detection

1. **Regulatory & Audit Explainability:** Compliance officers and operational supervisors cannot present an uninterpretable neural network weight as justification for freezing an account or lodging an STR.
2. **Alert Triaging Actionability:** Analysts require causal explanations (e.g., *"Transaction value ₹1,250,000 is 4.8σ above user's 30-day baseline of ₹24,500"*).
3. **Operational Stability:** Rule and statistical baseline models are deterministic, reproducible, compute in milliseconds, and do not suffer catastrophic forgetting or silent concept drift.
