"""
End-to-End Pipeline Integration Test.
Runs the complete analytical workflow and asserts all stages succeed and reconcile.
"""

import unittest
from python.common.config import load_config
from scripts.run_pipeline import run_pipeline


class TestEndToEndPipeline(unittest.TestCase):
    """Verifies that the entire pipeline executes deterministically from start to finish."""

    def test_pipeline_execution_and_reconciliation(self):
        """Pipeline must run completely and pass zero-tolerance reconciliation."""
        result = run_pipeline()
        self.assertIsNotNone(result)
        self.assertTrue(result["reconciliation_passed"])
        self.assertGreaterEqual(result["records_processed"], 10000)
        self.assertGreater(result["anomalies_detected"], 0)
        self.assertGreater(result["incidents_triaged"], 0)
        self.assertGreaterEqual(result["data_quality_score"], 95.0)


if __name__ == "__main__":
    unittest.main()
