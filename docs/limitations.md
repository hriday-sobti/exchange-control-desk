# Limitations & Production Next Steps: Exchange Control Desk

This document candidly articulates the architectural and operational limitations of this prototype and details the concrete steps required to deploy it into an enterprise exchange environment.

---

## 1. Known Architectural Limitations

1. **Synthetic User Ledger:** While anchored to real market pricing from CoinDCX's public API, the underlying user transaction ledger is synthetically generated. Real exchange transaction volumes exhibit complex microstructural behaviors, such as cross-asset correlations, hidden iceberg orders, and dynamic market-maker spreads that simple distributions cannot fully capture.
2. **In-Memory Batch Execution:** The prototype processes data in batch slices using pandas and embedded DuckDB. A true tier-1 exchange processing 5,000+ orders per second requires distributed streaming infrastructure (e.g., Apache Kafka / Apache Flink) for sub-second event-stream processing.
3. **Subjective Qualitative Scales:** While the prioritization formula ($\text{Score} = S \times L \times \ln(1+E)$) effectively ranks threats, the qualitative Severity scale (1 to 5) requires ongoing calibration against real operational triage outcomes.
4. **Power BI Desktop Environment Dependency:** While complete star-schema data models, DAX measures, and dark navy visual themes are provided as code, the final binary `.pbix` packaging requires manual opening and save inside Microsoft Power BI Desktop on a desktop environment.

---

## 2. Production Deployment Next Steps

1. **Event Streaming Integration:** Replace batch CSV/Parquet ingestion with direct Apache Kafka event consumers subscribing to matching engine execution topics (`order.matched`, `wallet.deposit.confirmed`, `wallet.withdrawal.requested`).
2. **Dynamic Alert Feedback Loop:** Implement an active learning / feedback mechanism where investigator dispositions in the triage queue (`Confirmed Fraud`, `False Positive`, `System Bug`) dynamically adjust user risk baselines and typology weights.
3. **Graph-Based Wallet Clustering:** Incorporate graph database technology (e.g., Neo4j) to track multi-hop counterparty transaction clusters and identify circular wash trading networks across related user accounts.
4. **Automated Gateway Circuit Breakers:** Connect P3 gateway failure burst alerts directly to the payment routing service to automatically throttle deteriorating banking rails and route deposits to secondary payment partners.
