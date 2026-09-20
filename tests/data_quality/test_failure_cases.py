"""
Failure and Edge-Case Tests.
Deliberately feeds corrupt data to confirm system rejects and flags issues properly.
"""

import unittest
import numpy as np
import pandas as pd
from python.common.config import load_config
from python.validation.data_quality import DataQualityEngine


class TestFailureCasesAndQuarantine(unittest.TestCase):
    """Tests that corrupt, negative, or orphan records are properly quarantined."""

    def setUp(self):
        self.config = load_config()
        self.engine = DataQualityEngine(self.config)

        # Baseline valid mock data
        self.valid_users = pd.DataFrame([{"user_id": "USR_0001"}])
        self.valid_assets = pd.DataFrame([{"asset_id": "BTC"}])

    def test_null_mandatory_field_rejected(self):
        """Transaction with null user_id must fail completeness and be quarantined."""
        corrupt_txs = pd.DataFrame(
            [
                {
                    "transaction_id": "TX_BAD_1",
                    "user_id": None,  # Null user ID
                    "asset_id": "BTC",
                    "timestamp": pd.Timestamp.now(tz="UTC"),
                    "transaction_type": "TRADE",
                    "side": "BUY",
                    "quantity": 1.0,
                    "price": 1000.0,
                    "gross_value": 1000.0,
                    "fee": 1.0,
                    "net_value": 1001.0,
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "WEB_PORTAL",
                }
            ]
        )
        clean, quarantined, rpt = self.engine.run_all_checks(
            corrupt_txs, self.valid_users, self.valid_assets
        )
        self.assertEqual(len(clean), 0)
        self.assertEqual(len(quarantined), 1)
        self.assertLess(rpt["data_quality_score"], 100.0)

    def test_negative_values_quarantined(self):
        """Negative gross_value must trigger validity failure."""
        corrupt_txs = pd.DataFrame(
            [
                {
                    "transaction_id": "TX_BAD_2",
                    "user_id": "USR_0001",
                    "asset_id": "BTC",
                    "timestamp": pd.Timestamp.now(tz="UTC"),
                    "transaction_type": "TRADE",
                    "side": "BUY",
                    "quantity": 1.0,
                    "price": -500.0,
                    "gross_value": -500.0,  # Negative value
                    "fee": 1.0,
                    "net_value": -499.0,
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "WEB_PORTAL",
                }
            ]
        )
        clean, quarantined, rpt = self.engine.run_all_checks(
            corrupt_txs, self.valid_users, self.valid_assets
        )
        self.assertEqual(len(clean), 0)
        self.assertEqual(len(quarantined), 1)

    def test_math_inconsistency_quarantined(self):
        """Gross value deviating significantly from price * qty must trigger consistency failure."""
        corrupt_txs = pd.DataFrame(
            [
                {
                    "transaction_id": "TX_BAD_3",
                    "user_id": "USR_0001",
                    "asset_id": "BTC",
                    "timestamp": pd.Timestamp.now(tz="UTC"),
                    "transaction_type": "TRADE",
                    "side": "BUY",
                    "quantity": 2.0,
                    "price": 50000.0,
                    "gross_value": 999999.0,  # Huge mismatch: 2 * 50k != 999k
                    "fee": 10.0,
                    "net_value": 1000009.0,
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "WEB_PORTAL",
                }
            ]
        )
        clean, quarantined, rpt = self.engine.run_all_checks(
            corrupt_txs, self.valid_users, self.valid_assets
        )
        self.assertEqual(len(clean), 0)
        self.assertEqual(len(quarantined), 1)

    def test_duplicate_primary_key_quarantined(self):
        """Duplicate transaction IDs must trigger uniqueness failure."""
        corrupt_txs = pd.DataFrame(
            [
                {
                    "transaction_id": "TX_DUP",
                    "user_id": "USR_0001",
                    "asset_id": "BTC",
                    "timestamp": pd.Timestamp.now(tz="UTC"),
                    "transaction_type": "TRADE",
                    "side": "BUY",
                    "quantity": 1.0,
                    "price": 50000.0,
                    "gross_value": 50000.0,
                    "fee": 10.0,
                    "net_value": 50010.0,
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "WEB_PORTAL",
                },
                {
                    "transaction_id": "TX_DUP",  # Same PK
                    "user_id": "USR_0001",
                    "asset_id": "BTC",
                    "timestamp": pd.Timestamp.now(tz="UTC"),
                    "transaction_type": "TRADE",
                    "side": "BUY",
                    "quantity": 1.0,
                    "price": 50000.0,
                    "gross_value": 50000.0,
                    "fee": 10.0,
                    "net_value": 50010.0,
                    "status": "COMPLETED",
                    "payment_method": "INTERNAL_MATCH",
                    "device_type": "WEB_PORTAL",
                },
            ]
        )
        clean, quarantined, rpt = self.engine.run_all_checks(
            corrupt_txs, self.valid_users, self.valid_assets
        )
        self.assertEqual(len(clean), 0)
        self.assertEqual(len(quarantined), 2)


if __name__ == "__main__":
    unittest.main()
