"""
Generates publication-quality architectural and dimensional data model PNG diagrams.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def generate_diagrams():
    os.makedirs("docs", exist_ok=True)

    # 1. Architecture Diagram
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0F172A")
    ax.set_facecolor("#0F172A")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title
    ax.text(50, 95, "EXCHANGE CONTROL DESK: END-TO-END ARCHITECTURE", ha="center", va="center", color="#F8FAFC", fontsize=16, weight="bold")
    ax.text(50, 91, "Transaction, Market & Risk Analytics for a VDA Platform", ha="center", va="center", color="#94A3B8", fontsize=11)

    boxes = [
        (10, 75, 80, 10, "1. INGESTION & MARKET BENCHMARKS", "Live CoinDCX Public Ticker API (995 Pairs) + Synthetic Exchange Engine (101k Txs) + Ground Truth Injections", "#1E293B", "#38BDF8"),
        (10, 60, 80, 10, "2. DATA QUALITY & GOVERNANCE GATE", "6 Dimensions (Completeness, Validity, Consistency, Uniqueness, Timeliness, Ref. Integrity) -> 100/100 Score", "#1E293B", "#34D399"),
        (10, 45, 80, 10, "3. RELATIONAL STORAGE & SQL ANALYTICS", "Star Schema (PostgreSQL DDL / Embedded DuckDB) + Rolling 24H Windows + Islands & Gaps Failure SQL", "#1E293B", "#FBBF24"),
        (10, 30, 80, 10, "4. FEATURE ENGINEERING & ANOMALY ENGINE", "Rolling 30D Baselines, Z-Scores, IQR Fences, Causal Narratives -> Synthetic Evaluation (71.8% Recall)", "#1E293B", "#F87171"),
        (10, 15, 80, 10, "5. INCIDENT PRIORITIZATION & TRIAGE QUEUE", "Priority Score = S * L * ln(1+E) -> P1 (<15m SLA), P2 (<2h SLA), P3, P4 Actionable Triage Queue", "#1E293B", "#A78BFA"),
        (10, 0, 80, 10, "6. POWER BI SEMANTIC LAYER & RECONCILIATION", "5 Operational Pages, Complete DAX Library, Zero-Tolerance Discrepancy Audit (Python == SQL == DAX)", "#1E293B", "#38BDF8")
    ]

    for x, y, w, h, title, desc, bg, border in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1", facecolor=bg, edgecolor=border, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 2, y + 6.5, title, color=border, fontsize=11, weight="bold")
        ax.text(x + 2, y + 2.5, desc, color="#E2E8F0", fontsize=9)

    plt.tight_layout()
    plt.savefig("docs/architecture.png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

    # 2. Data Model Diagram
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0F172A")
    ax.set_facecolor("#0F172A")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 95, "STAR-SCHEMA RELATIONAL DATA MODEL", ha="center", va="center", color="#F8FAFC", fontsize=16, weight="bold")

    tables = [
        (5, 55, 25, 28, "dim_users", ["PK: user_id", "signup_date", "country", "user_segment", "account_type", "risk_tier", "base_spend_mean", "base_spend_std"], "#38BDF8"),
        (70, 55, 25, 28, "dim_assets", ["PK: asset_id", "symbol", "name", "category", "is_stablecoin", "base_price_inr", "volatility"], "#38BDF8"),
        (37.5, 75, 25, 18, "dim_dates", ["PK: date_key", "calendar_date", "year, quarter, month", "is_weekend"], "#38BDF8"),
        (35, 30, 30, 38, "fact_transactions", ["PK: transaction_id", "FK: user_id", "FK: asset_id", "FK: date_key", "timestamp", "transaction_type, side", "quantity, price", "gross_value, fee, net_value", "status, payment_method", "device_type"], "#34D399"),
        (5, 5, 25, 20, "fact_anomalies", ["PK: anomaly_id", "FK: transaction_id", "FK: user_id", "anomaly_type", "deviation_score", "explanation"], "#F87171"),
        (70, 5, 25, 20, "fact_incidents", ["PK: incident_id", "FK: anomaly_id", "severity, likelihood", "exposure_inr", "priority_score, priority_band", "recommendation"], "#A78BFA"),
        (37.5, 5, 25, 18, "fact_market_ticks", ["PK: market_symbol, timestamp", "FK: asset_id", "FK: date_key", "price, high, low, volume_24h"], "#FBBF24")
    ]

    for x, y, w, h, name, fields, border in tables:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor=border, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 1, y + h - 3, name, color=border, fontsize=10, weight="bold")
        for idx, f in enumerate(fields):
            ax.text(x + 1, y + h - 6 - (idx * 2.5), f, color="#CBD5E1", fontsize=7.5)

    plt.tight_layout()
    plt.savefig("docs/data_model.png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("Architecture and Data Model PNG diagrams generated successfully!")


if __name__ == "__main__":
    generate_diagrams()
