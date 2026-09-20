"""
Cleaning and Preprocessing Module for Exchange Control Desk.
Handles date normalization, deduplication, and schema validation.
"""

from typing import Optional
import pandas as pd
from python.common.logger import get_logger

logger = get_logger()


class DataCleaner:
    """Normalizes raw input streams prior to feature extraction."""

    def clean_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deduplicates, enforces timestamp timezone, and sorts chronologically."""
        logger.info("Cleaning and normalizing %d transaction records", len(df))
        clean_df = df.drop_duplicates(subset=["transaction_id"]).copy()

        # Enforce UTC datetime
        clean_df["timestamp"] = pd.to_datetime(clean_df["timestamp"], utc=True)
        clean_df["date_key"] = clean_df["timestamp"].dt.strftime("%Y%m%d").astype(int)

        # Enforce numeric types
        clean_df["gross_value"] = clean_df["gross_value"].astype(float).round(2)
        clean_df["fee"] = clean_df["fee"].astype(float).round(2)
        clean_df["price"] = clean_df["price"].astype(float).round(4)
        clean_df["quantity"] = clean_df["quantity"].astype(float).round(8)

        clean_df = clean_df.sort_values(by="timestamp").reset_index(drop=True)
        return clean_df
