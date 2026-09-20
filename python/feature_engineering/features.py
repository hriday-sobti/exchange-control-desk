"""
Feature Engineering Engine for Exchange Control Desk.
Extracts user-level, transaction-level, and asset-level features for anomaly detection.
"""

from typing import Optional
import numpy as np
import pandas as pd
from python.common.config import load_config
from python.common.logger import get_logger

logger = get_logger()


class FeatureEngineeringEngine:
    """Computes statistical baselines, velocity counts, and historical deviations."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.velocity_window_mins = self.config.get("anomaly_detection", {}).get(
            "velocity_window_minutes", 60
        )
        self.min_history = self.config.get("anomaly_detection", {}).get(
            "zscore_min_history_count", 5
        )

    def extract_features(
        self,
        transactions_df: pd.DataFrame,
        users_df: pd.DataFrame,
        assets_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Enriches transactions with rolling velocity, user baselines, and delta metrics."""
        logger.info("Starting feature engineering on %d transactions", len(transactions_df))
        # Ensure chronological ordering per user
        df = transactions_df.sort_values(by=["user_id", "timestamp"]).copy()

        # Ensure timestamp is datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        # 1. User Cumulative History Features
        df["user_tx_seq"] = df.groupby("user_id").cumcount() + 1

        # Calculate prior cumulative sum and count strictly before current transaction
        cum_count = df.groupby("user_id").cumcount()
        cum_sum = df.groupby("user_id")["gross_value"].cumsum() - df["gross_value"]
        prior_mean = cum_sum / cum_count.replace(0, float("nan"))

        user_baseline_map_mean = users_df.set_index("user_id")["base_spend_mean"].to_dict()
        user_baseline_map_std = users_df.set_index("user_id")["base_spend_std"].to_dict()

        df["effective_user_mean"] = prior_mean.fillna(df["user_id"].map(user_baseline_map_mean))
        df["effective_user_std"] = df["user_id"].map(user_baseline_map_std).replace(0.0, 1.0)

        # Compute Z-score vs User Baseline
        df["user_baseline_zscore"] = (
            df["gross_value"] - df["effective_user_mean"]
        ) / df["effective_user_std"].clip(lower=1.0)

        # 2. Time Deltas & Rapid Pass-Through Features
        df["prev_timestamp"] = df.groupby("user_id")["timestamp"].shift(1)
        df["prev_tx_type"] = df.groupby("user_id")["transaction_type"].shift(1)
        df["prev_gross_value"] = df.groupby("user_id")["gross_value"].shift(1)

        # Time delta in minutes
        df["minutes_since_prev_tx"] = (
            df["timestamp"] - df["prev_timestamp"]
        ).dt.total_seconds() / 60.0

        # Rapid pass-through indicator (Deposit followed by Withdrawal within 15 min)
        df["is_rapid_pass_through"] = (
            (df["transaction_type"] == "WITHDRAWAL")
            & (df["prev_tx_type"] == "DEPOSIT")
            & (df["minutes_since_prev_tx"] <= 15.0)
            & (df["gross_value"] >= (df["prev_gross_value"] * 0.85))
        )

        # 3. Rolling Velocity Window (Transactions in last 60 minutes)
        logger.info("Computing rolling 60-minute transaction velocity per user")
        # Compute rolling count using grouped transform
        user_velocities = []
        for _, group in df.groupby("user_id"):
            indexed = group.set_index("timestamp")
            rolling_counts = indexed["transaction_id"].rolling("60min").count().values
            user_velocities.extend(rolling_counts)

        df["tx_velocity_60m"] = user_velocities

        # 4. Consecutive Failures Indicator (Rolling 30-minute window)
        # Identify failed transactions and count failures within a rolling 30m window per user
        fail_velocities = []
        for _, group in df.groupby("user_id"):
            is_fail = (group["status"] == "FAILED").astype(int)
            indexed_fail = group.assign(is_fail=is_fail).set_index("timestamp")
            fail_rolling = indexed_fail["is_fail"].rolling("30min").sum().values
            fail_velocities.extend(fail_rolling)

        df["consecutive_failures"] = fail_velocities

        # 5. Asset-Level Fee Quartiles
        asset_fee_stats = (
            df.groupby("asset_id")["fee"]
            .agg(
                q25=lambda x: np.percentile(x, 25),
                q75=lambda x: np.percentile(x, 75),
            )
            .reset_index()
        )
        asset_fee_stats["fee_iqr"] = asset_fee_stats["q75"] - asset_fee_stats["q25"]
        asset_fee_stats["fee_upper_fence"] = (
            asset_fee_stats["q75"] + 1.5 * asset_fee_stats["fee_iqr"]
        )

        df = df.merge(
            asset_fee_stats[["asset_id", "fee_upper_fence"]],
            on="asset_id",
            how="left",
        )
        df["fee_upper_fence"] = df["fee_upper_fence"].fillna(100.0)
        df["is_abnormal_fee"] = df["fee"] > df["fee_upper_fence"]

        # Restore original chronological sort
        df = df.sort_values(by="timestamp").reset_index(drop=True)
        logger.info("Feature engineering completed successfully.")
        return df
