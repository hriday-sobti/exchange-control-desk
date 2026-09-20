# Virtual Digital Asset (VDA) Indian Regulatory Context

**Document Type:** Analytical Domain Reference  
**Effective Baseline:** 2026 Guidelines (FIU-IND, PMLA, Income Tax Act)  
**Classification:** Prototype Technical Reference & Non-Legal Advisory

---

## 1. Regulatory Status of Virtual Digital Assets in India

In India, cryptocurrencies and digital tokens are legally classified as **Virtual Digital Assets (VDAs)** under Section 2(47A) of the Income Tax Act, 1961. 

Key statutory pillars governing VDA operations include:
1. **PMLA Coverage (2023 - Present):** In March 2023, the Ministry of Finance brought VDA activities (exchange between VDA and fiat, transfer of VDAs, safekeeping/administration of VDAs, and financial services related to issuer offerings) under the ambit of the **Prevention of Money Laundering Act, 2002 (PMLA)**.
2. **Reporting Entities (REs):** Indian VDA Service Providers (VDASPs) such as CoinDCX, CoinSwitch, and WazirX are formally designated as **Reporting Entities** registered with the **Financial Intelligence Unit - India (FIU-IND)**.
3. **Taxation Framework:** 30% flat tax on gains from VDA transfers (without set-off against other business losses) and a mandatory 1% Tax Deducted at Source (TDS) under Section 194S on all VDA transactions exceeding prescribed thresholds.

---

## 2. FIU-IND Compliance Mandates Relevant to Analytics

Under the updated **AML & CFT Guidelines for Reporting Entities Providing Services Related to Virtual Digital Assets (Updated January 2026)**, VDA exchanges must maintain systematic technological controls:

### A. Ongoing Due Diligence & Transaction Monitoring (Section 5.2)
- Reporting Entities must deploy automated systems capable of monitoring customer transactions on an ongoing basis.
- The monitoring system must flag:
  - Transactions of unusually large value relative to declared customer income/profile.
  - Unusual velocity of transactions within compressed time windows (rapid successive trades or deposits).
  - Unexplained complexity or lack of economic rationale (e.g., immediate pass-through of funds).
  - Transactions involving high-risk jurisdictions or sanctioned entities.

### B. Travel Rule Implementation (Section 5.3)
- VDASPs must capture, verify, and transmit originator and beneficiary information for all cross-wallet transfers exceeding prescribed limits.

### C. Suspicious Transaction Reporting (STR) (Section 5.5)
- Under Rule 7 of the PML (Maintenance of Records) Rules, an STR must be furnished to the Director, FIU-IND within 7 working days of arriving at a conclusion of suspicion.
- The grounds for suspicion include transactions giving rise to reasonable suspicion that they may involve proceeds of crime or structured layering.

---

## 3. Scope & Boundary of Exchange Control Desk

To maintain absolute professional integrity, the role and boundary of **Exchange Control Desk** are strictly defined:

```
+-------------------------------------------------------------+
|               EXCHANGE CONTROL DESK SCOPE                   |
+-------------------------------------------------------------+
| [IN SCOPE]                                                  |
| - Operational Risk & Transaction Anomaly Analytics         |
| - Statistical baseline deviation detection                  |
| - Rapid fiat-crypto layering pattern recognition           |
| - Prioritized operational investigation queue for analysts  |
| - Data quality auditing of exchange operational feeds       |
+-------------------------------------------------------------+
| [OUT OF SCOPE / EXPLICIT DISCLAIMERS]                       |
| - NOT a production AML regulatory compliance engine         |
| - NOT an official FIU-IND filing utility or STR generator   |
| - NOT a substitute for licensed compliance officers         |
| - Does NOT accuse any user or entity of legal wrongdoing   |
+-------------------------------------------------------------+
```

### Terminology Standard
- System alerts are referred to as **"Anomalies"**, **"Exceptions"**, or **"Operational Incidents"**.
- Anomalies describe **observable deviations in mathematical and transactional patterns**, never legal guilt.
- The incident queue assists operational analysts in triaging potential fraud, system bugs, or unusual market activity before escalation to specialized compliance units.
