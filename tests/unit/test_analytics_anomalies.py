"""
Unit and integration tests for feature engineering, anomaly detection,
evaluator, and incident prioritization.
"""

import unittest
from python.common.config import load_config
from python.feature_engineering.features import FeatureEngineeringEngine
from python.anomaly_detection.engine import AnomalyDetectionEngine
from python.anomaly_detection.evaluator import AnomalyEvaluator
from python.incidents.prioritization import IncidentPrioritizationEngine
from python.ingestion.synthetic_generator import SyntheticExchangeDataGenerator


class TestAnalyticsAndAnomalyEngine(unittest.TestCase):
    """Tests the feature extraction, anomaly rules, and prioritization engine."""

    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.gen = SyntheticExchangeDataGenerator(cls.config)
        cls.assets = cls.gen.generate_assets()
        cls.users = cls.gen.generate_users()
        cls.txs, cls.gt = cls.gen.generate_transactions()

        # Run feature engineering
        fe = FeatureEngineeringEngine(cls.config)
        cls.enriched_df = fe.extract_features(cls.txs, cls.users, cls.assets)

    def test_feature_engineering_columns(self):
        """Verifies presence of required analytical features."""
        required_features = {
            "user_baseline_zscore",
            "tx_velocity_60m",
            "is_rapid_pass_through",
            "consecutive_failures",
            "is_abnormal_fee",
        }
        self.assertTrue(required_features.issubset(self.enriched_df.columns))

    def test_anomaly_detection_execution(self):
        """Verifies that anomalies are detected and have plain-English explanations."""
        engine = AnomalyDetectionEngine(self.config)
        anomalies_df = engine.detect_anomalies(self.enriched_df)
        self.assertFalse(anomalies_df.empty)
        self.assertIn("explanation", anomalies_df.columns)
        # Check that explanation is not empty
        self.assertTrue((anomalies_df["explanation"].str.len() > 10).all())

    def test_anomaly_evaluation_metrics(self):
        """Verifies that the evaluator correctly computes synthetic precision/recall."""
        engine = AnomalyDetectionEngine(self.config)
        anomalies_df = engine.detect_anomalies(self.enriched_df)
        evaluator = AnomalyEvaluator()
        metrics = evaluator.evaluate(self.enriched_df, anomalies_df)

        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("f1_score", metrics)
        self.assertGreater(metrics["recall"], 0.70)  # >70% recall on synthetic anomalies

    def test_incident_prioritization_bands(self):
        """Verifies incident scoring and priority band assignment."""
        engine = AnomalyDetectionEngine(self.config)
        anomalies_df = engine.detect_anomalies(self.enriched_df)
        p_engine = IncidentPrioritizationEngine(self.config)
        incidents_df = p_engine.prioritize_incidents(anomalies_df)

        self.assertFalse(incidents_df.empty)
        bands = set(incidents_df["priority_band"])
        self.assertTrue({"P1", "P2"}.intersection(bands))
        self.assertTrue((incidents_df["priority_score"] > 0).all())


if __name__ == "__main__":
    unittest.main()
