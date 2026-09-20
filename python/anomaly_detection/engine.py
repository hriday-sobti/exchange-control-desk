"""
Explainable Anomaly Detection Engine for Exchange Control Desk.
Flags operational exceptions and constructs causal natural-language explanations.
"""

import uuid
from typing import Any, Dict, List, Optional
import pandas as pd
from python.common.config import load_config
from python.common.logger import get_logger

logger = get_logger()


class AnomalyDetectionEngine:
    """Executes explainable multi-tier anomaly detection across engineered features."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.ano_cfg = self.config.get("anomaly_detection", {})
        self.zscore_thresh = self.ano_cfg.get("zscore_threshold", 3.0)
        self.velocity_thresh = self.ano_cfg.get("velocity_threshold_count", 5)
        self.failures_thresh = self.ano_cfg.get("repeated_failures_count", 3)

    def detect_anomalies(self, enriched_df: pd.DataFrame) -> pd.DataFrame:
        """Evaluates transactions against explainable detection rules and emits structured anomaly records."""
        logger.info("Executing explainable anomaly detection on %d records", len(enriched_df))
        anomalies: List[Dict[str, Any]] = []

        for _, row in enriched_df.iterrows():
            tx_id = row["transaction_id"]
            user_id = row["user_id"]
            ts = row["timestamp"]
            gross_val = float(row["gross_value"])

            # 1. Typology: USER BASELINE SPIKE
            zscore = float(row.get("user_baseline_zscore", 0.0))
            if zscore >= self.zscore_thresh:
                mean_val = float(row.get("effective_user_mean", gross_val))
                anomalies.append(
                    {
                        "anomaly_id": f"ANO_{uuid.uuid4().hex[:10].upper()}",
                        "transaction_id": tx_id,
                        "user_id": user_id,
                        "timestamp": ts,
                        "anomaly_type": "BASELINE_SPIKE",
                        "metric_name": "user_baseline_zscore",
                        "observed_value": gross_val,
                        "baseline_value": mean_val,
                        "deviation_score": round(zscore, 2),
                        "detector_method": "ROLLING_ZSCORE",
                        "severity": 4,
                        "likelihood": 5 if zscore >= 5.0 else 4,
                        "exposure_inr": gross_val,
                        "explanation": (
                            f"Transaction value ₹{gross_val:,.2f} is {zscore:.1f}σ above "
                            f"user's rolling historical baseline of ₹{mean_val:,.2f}."
                        ),
                    }
                )

            # 2. Typology: HIGH VELOCITY BURST
            velocity = int(row.get("tx_velocity_60m", 1))
            if velocity >= self.velocity_thresh:
                anomalies.append(
                    {
                        "anomaly_id": f"ANO_{uuid.uuid4().hex[:10].upper()}",
                        "transaction_id": tx_id,
                        "user_id": user_id,
                        "timestamp": ts,
                        "anomaly_type": "VELOCITY_BURST",
                        "metric_name": "tx_velocity_60m",
                        "observed_value": velocity,
                        "baseline_value": self.velocity_thresh,
                        "deviation_score": round(velocity / self.velocity_thresh, 2),
                        "detector_method": "TIME_WINDOW_COUNTER",
                        "severity": 4,
                        "likelihood": 5 if velocity >= 10 else 4,
                        "exposure_inr": gross_val,
                        "explanation": (
                            f"User executed {velocity} transactions within a 60-minute window, "
                            f"breaching velocity threshold of {self.velocity_thresh}."
                        ),
                    }
                )

            # 3. Typology: RAPID PASS-THROUGH (Layering)
            if row.get("is_rapid_pass_through", False):
                prev_val = float(row.get("prev_gross_value", gross_val))
                delta_m = float(row.get("minutes_since_prev_tx", 0.0))
                anomalies.append(
                    {
                        "anomaly_id": f"ANO_{uuid.uuid4().hex[:10].upper()}",
                        "transaction_id": tx_id,
                        "user_id": user_id,
                        "timestamp": ts,
                        "anomaly_type": "RAPID_PASS_THROUGH",
                        "metric_name": "pass_through_minutes",
                        "observed_value": delta_m,
                        "baseline_value": 15.0,
                        "deviation_score": round(15.0 / max(delta_m, 0.1), 2),
                        "detector_method": "STATE_TRANSITION_TIMING",
                        "severity": 5,
                        "likelihood": 5,
                        "exposure_inr": gross_val,
                        "explanation": (
                            f"Rapid pass-through: Withdrawal of ₹{gross_val:,.2f} requested just "
                            f"{delta_m:.1f}m after fiat deposit of ₹{prev_val:,.2f} with zero trading activity."
                        ),
                    }
                )

            # 4. Typology: REPEATED GATEWAY FAILURES
            consec_fails = int(row.get("consecutive_failures", 0))
            if row.get("status") == "FAILED" and consec_fails >= 2:
                anomalies.append(
                    {
                        "anomaly_id": f"ANO_{uuid.uuid4().hex[:10].upper()}",
                        "transaction_id": tx_id,
                        "user_id": user_id,
                        "timestamp": ts,
                        "anomaly_type": "REPEATED_FAILURES",
                        "metric_name": "consecutive_failures",
                        "observed_value": consec_fails,
                        "baseline_value": self.failures_thresh,
                        "deviation_score": round(consec_fails / self.failures_thresh, 2),
                        "detector_method": "FAILURE_STATE_MACHINE",
                        "severity": 3,
                        "likelihood": 4,
                        "exposure_inr": gross_val,
                        "explanation": (
                            f"User encountered {consec_fails} consecutive failed transactions within 30m, "
                            "indicating potential brute force credential guessing or payment gateway fault."
                        ),
                    }
                )

            # 5. Typology: ABNORMAL FEE
            if row.get("is_abnormal_fee", False):
                fee_val = float(row.get("fee", 0.0))
                fence = float(row.get("fee_upper_fence", 50.0))
                anomalies.append(
                    {
                        "anomaly_id": f"ANO_{uuid.uuid4().hex[:10].upper()}",
                        "transaction_id": tx_id,
                        "user_id": user_id,
                        "timestamp": ts,
                        "anomaly_type": "ABNORMAL_FEE",
                        "metric_name": "fee_inr",
                        "observed_value": fee_val,
                        "baseline_value": fence,
                        "deviation_score": round(fee_val / max(fence, 1.0), 2),
                        "detector_method": "IQR_UPPER_FENCE",
                        "severity": 2,
                        "likelihood": 4,
                        "exposure_inr": fee_val,
                        "explanation": (
                            f"Platform fee ₹{fee_val:,.2f} breaches the asset's IQR upper fence "
                            f"of ₹{fence:,.2f}."
                        ),
                    }
                )

        anomalies_df = pd.DataFrame(anomalies)
        logger.info(
            "Anomaly detection completed. Total anomalies identified: %d across %d records",
            len(anomalies_df),
            len(enriched_df),
        )
        return anomalies_df
