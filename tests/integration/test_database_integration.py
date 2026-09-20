"""
Integration tests for database loading and analytical SQL view querying.
Verifies that DuckDB/PostgreSQL loads clean dimensional tables and view aggregations work.
"""

import unittest
from python.common.config import load_config
from python.common.db import DatabaseConnection
from python.common.loader import DatabaseLoader
from python.ingestion.synthetic_generator import SyntheticExchangeDataGenerator
from python.validation.data_quality import DataQualityEngine


class TestDatabaseIntegration(unittest.TestCase):
    """Verifies relational loading, primary keys, and analytical views."""

    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.loader = DatabaseLoader(cls.config)
        cls.db = cls.loader.db

        # Generate small dataset
        gen = SyntheticExchangeDataGenerator(cls.config)
        gen.num_users = 200
        gen.num_transactions = 1000
        cls.assets_df = gen.generate_assets()
        cls.users_df = gen.generate_users()
        cls.txs_df, _ = gen.generate_transactions()

        # Data quality
        dq = DataQualityEngine(cls.config)
        cls.clean_tx, _, _ = dq.run_all_checks(cls.txs_df, cls.users_df, cls.assets_df)

        # Initialize and load
        cls.loader.initialize_schema()
        cls.loader.load_date_dimension("2026-08-01", "2026-09-20")
        cls.loader.load_clean_data(
            users_df=cls.users_df,
            assets_df=cls.assets_df,
            transactions_df=cls.clean_tx,
        )
        cls.loader.create_views()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_table_row_counts(self):
        """Verifies row counts in relational tables."""
        tx_count = self.db.query_df("SELECT COUNT(*) as cnt FROM fact_transactions").iloc[0]["cnt"]
        user_count = self.db.query_df("SELECT COUNT(*) as cnt FROM dim_users").iloc[0]["cnt"]
        asset_count = self.db.query_df("SELECT COUNT(*) as cnt FROM dim_assets").iloc[0]["cnt"]

        self.assertEqual(tx_count, len(self.clean_tx))
        self.assertEqual(user_count, len(self.users_df))
        self.assertEqual(asset_count, len(self.assets_df))

    def test_analytical_views_execute(self):
        """Verifies that analytical SQL views return valid aggregations."""
        df_daily = self.db.query_df("SELECT * FROM vw_daily_platform_metrics")
        self.assertFalse(df_daily.empty)
        self.assertIn("total_transactions", df_daily.columns)
        self.assertIn("total_gtv_inr", df_daily.columns)

        df_assets = self.db.query_df("SELECT * FROM vw_asset_volume_summary")
        self.assertFalse(df_assets.empty)
        self.assertIn("platform_volume_share_pct", df_assets.columns)


if __name__ == "__main__":
    unittest.main()
