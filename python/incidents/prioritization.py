"""
Incident Prioritization and Operational Queue Engine for Exchange Control Desk.
Transforms raw anomalies into scored, ranked, and triaged operational incidents.
"""

import math
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from python.common.config import load_config
from python.common.logger import get_logger

logger = get_logger()


class IncidentPrioritizationEngine:
    """Computes risk scores and assigns priority bands with actionable recommendations."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.p_cfg = self.config.get("incident_prioritization", {})
        self.p1_thresh = self.p_cfg.get("p1_threshold", 150.0)
        self.p2_thresh = self.p_cfg.get("p2_threshold", 80.0)
        self.p3_thresh = self.p_cfg.get("p3_threshold", 30.0)
        self.high_exposure_limit = self.p_cfg.get("high_exposure_threshold_inr", 500000.0)

    def prioritize_incidents(self, anomalies_df: pd.DataFrame) -> pd.DataFrame:
        """Calculates Priority Score = Severity * Likelihood * ln(1 + Exposure) and builds triage queue."""
        logger.info("Prioritizing %d anomalies into operational incident queue", len(anomalies_df))
        if anomalies_df.empty:
            return pd.DataFrame()

        incidents: List[Dict[str, Any]] = []

        for _, row in anomalies_df.iterrows():
            severity = int(row.get("severity", 3))
            likelihood = int(row.get("likelihood", 3))
            exposure = float(row.get("exposure_inr", 0.0))
            typology = row.get("anomaly_type", "UNKNOWN")

            # Mathematical Prioritization Formula
            # Score = Severity * Likelihood * ln(1 + Exposure)
            exposure_factor = math.log(1.0 + max(exposure, 0.0))
            raw_score = severity * likelihood * exposure_factor
            priority_score = round(raw_score, 2)

            # Assign Priority Bands
            # Fast-track rule: Critical typology with >= ₹500,000 exposure auto-promoted to P1
            if priority_score >= self.p1_thresh or (
                severity == 5 and exposure >= self.high_exposure_limit
            ):
                band = "P1"
                rationale = (
                    f"P1 CRITICAL: High-severity {typology} with substantial financial exposure "
                    f"(₹{exposure:,.2f}) exceeding risk threshold."
                )
            elif priority_score >= self.p2_thresh:
                band = "P2"
                rationale = (
                    f"P2 HIGH: Elevated risk anomaly with notable score {priority_score:.1f} "
                    f"and exposure ₹{exposure:,.2f}."
                )
            elif priority_score >= self.p3_thresh:
                band = "P3"
                rationale = (
                    f"P3 MEDIUM: Moderate risk exception (Score: {priority_score:.1f}); standard operational review."
                )
            else:
                band = "P4"
                rationale = (
                    f"P4 LOW: Low-exposure operational exception (Score: {priority_score:.1f}); routine monitoring."
                )

            # Assign Prescriptive Action Recommendations
            if typology == "RAPID_PASS_THROUGH":
                rec = "Place temporary 24h withdrawal hold; verify bank account originator name; request source-of-funds declaration."
            elif typology == "BASELINE_SPIKE":
                if exposure >= self.high_exposure_limit:
                    rec = "Initiate outbound phone verification; inspect recent device IP and 2FA changes; check order book liquidity depth."
                else:
                    rec = "Verify user trading history; request KYC Tier-2 verification if unverified."
            elif typology == "VELOCITY_BURST":
                rec = "Enforce temporary rate-limiting on user API key/session; inspect user agent and IP subnet."
            elif typology == "REPEATED_FAILURES":
                rec = "Inspect payment gateway integration status; notify customer support; check for credential brute forcing."
            elif typology == "ABNORMAL_FEE":
                rec = "Credit excess fee to user balance; notify engineering of smart contract / fee calculation parameter check."
            else:
                rec = "Review user transaction log and monitor subsequent 24-hour activity."

            incidents.append(
                {
                    "incident_id": f"INC_{uuid.uuid4().hex[:10].upper()}",
                    "anomaly_id": row["anomaly_id"],
                    "transaction_id": row.get("transaction_id"),
                    "user_id": row["user_id"],
                    "created_at": row["timestamp"],
                    "anomaly_type": typology,
                    "severity": severity,
                    "likelihood": likelihood,
                    "exposure_inr": exposure,
                    "priority_score": priority_score,
                    "priority_band": band,
                    "rationale": rationale,
                    "recommendation": rec,
                    "status": "OPEN",
                }
            )

        incidents_df = pd.DataFrame(incidents)

        # Sort queue by Priority Band (P1 -> P4), then by descending Priority Score
        band_order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
        incidents_df["band_rank"] = incidents_df["priority_band"].map(band_order)
        incidents_df = incidents_df.sort_values(
            by=["band_rank", "priority_score"], ascending=[True, False]
        ).drop(columns=["band_rank"])

        logger.info(
            "Prioritization complete. Triage breakdown: P1=%d, P2=%d, P3=%d, P4=%d",
            (incidents_df["priority_band"] == "P1").sum(),
            (incidents_df["priority_band"] == "P2").sum(),
            (incidents_df["priority_band"] == "P3").sum(),
            (incidents_df["priority_band"] == "P4").sum(),
        )
        return incidents_df

    def export_queue(self, incidents_df: pd.DataFrame, output_dir: str = "outputs/incidents"):
        """Exports the actionable investigation queue in CSV and Parquet."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        incidents_df.to_csv(path / "investigation_queue.csv", index=False)
        incidents_df.to_parquet(path / "investigation_queue.parquet", index=False)
        logger.info("Exported investigation queue to %s", output_dir)
