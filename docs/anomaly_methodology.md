# Anomaly Methodology & Ground Truth Scenarios

This document formalizes the mathematical logic, detection parameters, and ground-truth injection profiles for all anomaly typologies in **Exchange Control Desk**.

---

## 1. Ground Truth Anomaly Typologies

To rigorously benchmark detection performance, the synthetic generator injects 10 controlled operational risk and fraud scenarios:

1. **Velocity Burst (`VELOCITY_BURST`):** An automated bot or account takeover fires $>10$ transactions within a 15-minute sliding window (normal retail rate: $<2$ tx/day).
2. **User Baseline Spike (`BASELINE_SPIKE`):** A sudden transaction whose gross value exceeds the user's historical rolling 30-day mean by $>4.0$ standard deviations ($Z \ge 4.0$).
3. **Repeated Gateway Failures (`REPEATED_FAILURES`):** A user experiences $\ge 4$ consecutive failed deposit/withdrawal attempts within 30 minutes, indicating credential stuffing or gateway routing faults.
4. **Rapid Pass-Through Layering (`RAPID_PASS_THROUGH`):** A large fiat deposit followed immediately by a total withdrawal in an unhosted crypto asset within $\le 15$ minutes with no trading activity, matching classical PMLA layering typologies.
5. **Abnormal Fee Outlier (`ABNORMAL_FEE`):** A transaction assessed an exorbitant fee breaching the asset's IQR upper fence ($> Q_3 + 3.0 \times \text{IQR}$), signaling fee calculation bugs or front-running gas spikes.
6. **Asset-Level Volume Spike (`ASSET_SPIKE`):** Hourly aggregate volume on a low-liquidity token surges $>5.0\sigma$ above its 7-day rolling median without broader market correlation, signaling potential pump-and-dump manipulation.
7. **Round-Trip Circular Wash (`CIRCULAR_WASH`):** Rapid succession of matched buy and sell trades between related accounts with zero net inventory change within 10 minutes.
8. **Dormant Account Awakening (`DORMANT_AWAKENING`):** An account with zero transactional activity for $>90$ days suddenly executes a maximum-limit withdrawal.
9. **Off-Hours High-Exposure Shift (`OFF_HOURS_SURGE`):** Multi-million INR transfers executing at uncharacteristic off-hours (03:00–04:30 AM local time) with new device fingerprints.
10. **Duplicate Transaction Submissions (`DUPLICATE_TX`):** Rapid re-submission of identical transaction quantities and timestamps within 2 seconds due to network retries or replay attempts.

---

## 2. Detection Logic & Threshold Calibration

| Typology Code | Primary Detector Algorithm | Calibrated Decision Threshold | Required Explainability Output Format |
| :--- | :--- | :--- | :--- |
| `VELOCITY_BURST` | Rolling Window Sliding Count | $N_{\text{tx}} \ge 5$ in 60 min | `"User executed {n} transactions in past 60m (Threshold: {thresh})"` |
| `BASELINE_SPIKE` | Rolling 30-Day Z-Score | $Z_{i, u} \ge 3.0$ with $k \ge 5$ hist | `"Transaction ₹{val:,.2f} is {z:.1f}σ above 30d baseline of ₹{mean:,.2f}"` |
| `REPEATED_FAILURES` | Consecutive Failure State Machine | Count $\ge 3$ consecutive FAILED | `"User suffered {n} consecutive failed transactions within 30 minutes"` |
| `RAPID_PASS_THROUGH` | Cross-Transaction Latency Delta | $\Delta t(\text{Deposit} \rightarrow \text{Withdrawal}) \le 15\text{m}$ | `"Rapid pass-through: Deposit of ₹{d_val:,.2f} followed by withdrawal in {delta}m with zero trading"` |
| `ABNORMAL_FEE` | Non-Parametric IQR Fence | $\text{Fee} > Q_3 + 1.5 \times \text{IQR}$ | `"Transaction fee ₹{fee:,.2f} exceeds asset IQR upper fence of ₹{fence:,.2f}"` |
| `ASSET_SPIKE` | Asset Volume Deviation | $\text{Vol}_{\text{hour}} > \mu_{\text{asset}} + 3\sigma$ | `"Asset {symbol} 1h volume of {vol} is {z:.1f}σ above rolling mean"` |

---

## 3. Ground Truth Evaluation Framework

Every generated transaction record carries an internal ground-truth label:
- `is_injected_anomaly`: Boolean (`True` / `False`)
- `injected_typology`: String identifier or `None`

The evaluation module (`python/anomaly_detection/evaluator.py`) automatically tallies:
- **True Positives (TP):** Flagged by detector $\land$ `is_injected_anomaly == True`
- **False Positives (FP):** Flagged by detector $\land$ `is_injected_anomaly == False`
- **False Negatives (FN):** Not flagged by detector $\land$ `is_injected_anomaly == True`
- **True Negatives (TN):** Not flagged $\land$ `is_injected_anomaly == False`

Outputs precision, recall, and F1-score saved to `outputs/anomalies/anomaly_evaluation.csv`.
