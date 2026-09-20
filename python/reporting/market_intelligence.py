"""
Market Intelligence and User Segmentation Module.
Connects external market data to internal exchange activity to detect divergence,
market share momentum, and behavioral user cohorts.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from python.common.logger import get_logger

logger = get_logger()


class MarketIntelligenceEngine:
    """Analyzes market vs platform divergence and segments users by transactional behavior."""

    def compute_market_divergence(
        self,
        transactions_df: pd.DataFrame,
        market_ticks_df: pd.DataFrame,
        output_dir: str = "outputs/executive",
    ) -> pd.DataFrame:
        """Compares platform volume share and price spreads against public market benchmarks."""
        logger.info("Computing platform vs market liquidity divergence")

        # Aggregate platform completed volume by asset
        platform_vol = (
            transactions_df[transactions_df["status"] == "COMPLETED"]
            .groupby("asset_id")
            .agg(
                platform_tx_count=("transaction_id", "count"),
                platform_gtv_inr=("gross_value", "sum"),
                platform_avg_price=("price", "mean"),
            )
            .reset_index()
        )

        # Aggregate market ticks latest metrics
        market_latest = (
            market_ticks_df.sort_values(by="timestamp")
            .groupby("asset_id")
            .last()
            .reset_index()[["asset_id", "price", "volume_24h", "change_24h_pct"]]
            .rename(
                columns={
                    "price": "market_benchmark_price",
                    "volume_24h": "market_24h_volume",
                    "change_24h_pct": "market_24h_change_pct",
                }
            )
        )

        merged = platform_vol.merge(market_latest, on="asset_id", how="left")

        # Calculate divergence metrics
        merged["price_divergence_pct"] = round(
            (merged["platform_avg_price"] - merged["market_benchmark_price"])
            / merged["market_benchmark_price"]
            * 100.0,
            3,
        )

        merged["platform_volume_share_pct"] = round(
            merged["platform_gtv_inr"] / merged["platform_gtv_inr"].sum() * 100.0, 2
        )

        # Flag divergence risks
        merged["liquidity_divergence_flag"] = np.where(
            merged["price_divergence_pct"].abs() > 2.5, "DIVERGENT", "ALIGNED"
        )

        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        merged.to_csv(path / "market_platform_divergence.csv", index=False)
        logger.info("Market divergence analysis completed.")
        return merged

    def segment_users(
        self,
        transactions_df: pd.DataFrame,
        users_df: pd.DataFrame,
        output_dir: str = "outputs/executive",
    ) -> pd.DataFrame:
        """Segments user population into operational behavioral cohorts."""
        logger.info("Computing analytical user behavioral segmentation")

        tx_stats = (
            transactions_df[transactions_df["status"] == "COMPLETED"]
            .groupby("user_id")
            .agg(
                tx_count=("transaction_id", "count"),
                total_gtv=("gross_value", "sum"),
                avg_ticket_size=("gross_value", "mean"),
                unique_assets=("asset_id", "nunique"),
            )
            .reset_index()
        )

        segmented = users_df.merge(tx_stats, on="user_id", how="left").fillna(
            {"tx_count": 0, "total_gtv": 0.0, "avg_ticket_size": 0.0, "unique_assets": 0}
        )

        # Behavioral rule-based categorization
        def assign_cohort(row):
            count = row["tx_count"]
            gtv = row["total_gtv"]
            if gtv >= 2000000.0:
                return "Institutional / Ultra-HNW"
            elif gtv >= 300000.0 or count >= 50:
                return "High-Value Active Trader"
            elif count >= 10:
                return "Regular Active Retail"
            elif count >= 1:
                return "Occasional Retail"
            else:
                return "Dormant / Inactive"

        segmented["behavioral_cohort"] = segmented.apply(assign_cohort, axis=1)

        cohort_summary = (
            segmented.groupby("behavioral_cohort")
            .agg(
                user_count=("user_id", "count"),
                total_gtv=("total_gtv", "sum"),
                avg_user_gtv=("total_gtv", "mean"),
                avg_user_tx=("tx_count", "mean"),
            )
            .reset_index()
        )
        cohort_summary["user_share_pct"] = round(
            cohort_summary["user_count"] / max(len(segmented), 1) * 100.0, 2
        )
        gtv_sum = float(cohort_summary["total_gtv"].sum())
        if gtv_sum > 0:
            cohort_summary["gtv_share_pct"] = (cohort_summary["total_gtv"] / gtv_sum * 100.0).round(2)
        else:
            cohort_summary["gtv_share_pct"] = 0.0
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        cohort_summary.to_csv(path / "user_behavioral_segmentation.csv", index=False)
        logger.info("User behavioral segmentation completed.")
        return cohort_summary
