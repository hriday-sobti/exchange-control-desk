# Stakeholder Map: Exchange Control Desk

This document maps the organizational stakeholders modeled for **Exchange Control Desk**, their primary business questions, KPI requirements, and decision workflows.

---

## 1. Stakeholder Matrix

| Stakeholder Role | Business Focus | Core Questions Asked | Decision / Action Driven | Primary Reporting Surface |
| :--- | :--- | :--- | :--- | :--- |
| **Head of Operations** | Platform reliability, throughput, payment rail health | Are deposits and withdrawals settling smoothly? Which payment gateways are dropping? | Re-route payment gateway traffic; scale operational support desks. | Page 1 (Executive) & Page 3 (Transactions) |
| **Risk & AML Operations Lead** | Fraud mitigation, illicit flow prevention, alert triage | Which user accounts exhibit suspicious rapid layering or baseline spikes? What is our financial exposure? | Place temporary account holds; initiate enhanced due diligence (EDD) investigations. | Page 4 (Anomaly / Incident Desk) |
| **Compliance Officer (FIU Liaison)** | Adherence to PMLA guidelines, STR defensibility | Are transaction monitoring thresholds defensible and explainable? Can we audit alert logic? | Prepare internal audit logs; ensure adherence to Section 5.2 FIU-IND monitoring guidelines. | Page 4 & Audit Logs |
| **Data Engineering & Analytics Lead** | Data pipeline health, semantic consistency, pipeline latency | Can downstream decision-makers trust today's metrics? Are there nulls or schema drift in upstream feeds? | Quarantine bad feeds; trace upstream CDC pipeline bugs; trigger reconciliation. | Page 5 (Data Quality Desk) |
| **Product Growth & Trading Desk** | Liquidity, asset adoption, market/platform divergence | Are users trading in line with global crypto market momentum? Which tokens drive volume? | Adjust maker/taker incentives; update order book depth parameters. | Page 2 (Market & Platform) |
| **Chief Executive Officer / COO** | High-level platform health, total volume, risk posture | What is our total daily GTV and net fee revenue? Are there catastrophic operational or financial risks open? | Strategic resource allocation; regulatory disclosures; executive governance. | Page 1 (Executive Overview) |

---

## 2. Interaction & Escalation Workflow

```text
[Data Feeds Ingested]
         |
         v
[Data Quality Engine] ---- (Failures > 2%) ----> [Alert Data Engineering]
         |
         | (Passed / Quarantined)
         v
[Analytical Fact Tables]
         |
         v
[Anomaly Detection Engine]
         |
         v
[Incident Prioritization]
         |
         +---- [P1 / Critical] ----> Immediate Escalation to Risk Ops Lead & Account Freeze
         |
         +---- [P2 / High] --------> Assigned to Fraud Investigator Queue (SLA: 2 Hours)
         |
         +---- [P3 / P4] ----------> Operational Review Queue / Automated Monitoring
         |
         v
[Power BI Executive & Operational Control Desk]
```
