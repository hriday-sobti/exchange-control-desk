"""
Unit tests for data generation, configuration, and data quality validation.
"""

import unittest
import pandas as pd
from python.common.config import load_config
from python.ingestion.synthetic_generator import SyntheticExchangeDataGenerator
from python.validation.data_quality import DataQualityEngine


class TestDataGenerationAndQuality(unittest.TestCase):
    """Verifies synthetic generation distributions and data quality assertions."""

    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        # Small dev scale for fast unit tests
        cls.generator = SyntheticExchangeDataGenerator(cls.config)
        cls.assets_df = cls.generator.generate_assets()
        cls.users_df = cls.generator.generate_users()
        cls.txs_df, cls.gt_df = cls.generator.generate_transactions()

    def test_asset_generation(self):
        """Asset dimension should have non-empty records and required columns."""
        self.assertGreaterEqual(len(self.assets_df), 6)
        required_cols = {"asset_id", "symbol", "name", "category", "base_price_inr"}
        self.assertTrue(required_cols.issubset(self.assets_df.columns))

    def test_user_generation_and_segments(self):
        """User dimension should contain expected segments."""
        self.assertGreater(len(self.users_df), 100)
        segments = set(self.users_df["user_segment"])
        self.assertIn("Retail Casual", segments)
        self.assertIn("Active Trader", segments)
        self.assertIn("Institutional / HNW", segments)

    def test_transaction_fields_and_integrity(self):
        """Transaction stream should respect financial constraints."""
        self.assertGreater(len(self.txs_df), 100)
        self.assertTrue((self.txs_df["gross_value"] > 0).all())
        self.assertTrue((self.txs_df["fee"] >= 0).all())
        self.assertTrue((self.txs_df["quantity"] > 0).all())

    def test_data_quality_engine_clean_pass(self):
        """Data quality engine should evaluate clean synthetic data with high score."""
        engine = DataQualityEngine(self.config)
        clean, quarantined, rpt = engine.run_all_checks(
            self.txs_df, self.users_df, self.assets_df
        )
        self.assertGreaterEqual(rpt["data_quality_score"], 95.0)
        self.assertEqual(len(clean), len(self.txs_df))
        self.assertEqual(len(quarantined), 0)


if __name__ == "__main__":
    unittest.main()
