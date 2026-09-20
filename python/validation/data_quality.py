"""
Comprehensive Automated Data Quality Engine for Exchange Control Desk.
Evaluates 6 Dimensions: Completeness, Validity, Consistency, Uniqueness,
Referential Integrity, and Timeliness.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from python.common.config import load_config
from python.common.logger import get_logger

logger = get_logger()


class DataQualityEngine:
    """Executes deterministic rule-based data quality checks and computes an audit score."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.dq_cfg = self.config.get("data_quality", {})
        self.weights = self.dq_cfg.get(
            "weights",
            {
                "completeness": 0.25,
                "validity": 0.20,
                "consistency": 0.20,
                "uniqueness": 0.15,
                "referential_integrity": 0.10,
                "timeliness": 0.10,
            },
        )
        self.tolerance_pct = self.dq_cfg.get("tolerance_percent", 1.0)
        self.check_results: List[Dict[str, Any]] = []

    def run_all_checks(
        self,
        transactions_df: pd.DataFrame,
        users_df: pd.DataFrame,
        assets_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Executes checks across all 6 dimensions and separates clean from quarantined data."""
        logger.info("Initiating comprehensive Data Quality evaluation on %d records", len(transactions_df))
        self.check_results.clear()

        total_tx = len(transactions_df)
        failing_indices = set()

        # 1. COMPLETENESS CHECKS
        mandatory_fields = [
            "transaction_id",
            "user_id",
            "asset_id",
            "timestamp",
            "gross_value",
            "quantity",
            "price",
            "status",
        ]
        null_counts = transactions_df[mandatory_fields].isnull().sum()
        for field, count in null_counts.items():
            fail_rate = float(count / total_tx) if total_tx > 0 else 0.0
            status = "PASSED" if count == 0 else "FAILED"
            if count > 0:
                failing_indices.update(transactions_df[transactions_df[field].isnull()].index)
            self.check_results.append(
                {
                    "check_id": f"CHK_CMP_{field.upper()}",
                    "dimension": "completeness",
                    "entity": "transactions",
                    "field": field,
                    "records_checked": total_tx,
                    "records_failed": int(count),
                    "failure_rate": round(fail_rate, 6),
                    "status": status,
                    "severity": "CRITICAL",
                    "description": f"Null value check for mandatory field: {field}",
                }
            )

        # 2. VALIDITY CHECKS
        # Valid transaction types
        valid_types = {"DEPOSIT", "WITHDRAWAL", "TRADE"}
        invalid_type_mask = ~transactions_df["transaction_type"].isin(valid_types)
        invalid_type_count = int(invalid_type_mask.sum())
        if invalid_type_count > 0:
            failing_indices.update(transactions_df[invalid_type_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_VAL_TX_TYPE",
                "dimension": "validity",
                "entity": "transactions",
                "field": "transaction_type",
                "records_checked": total_tx,
                "records_failed": invalid_type_count,
                "failure_rate": round(float(invalid_type_count / total_tx), 6),
                "status": "PASSED" if invalid_type_count == 0 else "FAILED",
                "severity": "CRITICAL",
                "description": "Validation of transaction_type allowed enum values",
            }
        )

        # Non-negative gross value and quantity
        neg_val_mask = (transactions_df["gross_value"] <= 0) | (transactions_df["quantity"] <= 0)
        neg_val_count = int(neg_val_mask.sum())
        if neg_val_count > 0:
            failing_indices.update(transactions_df[neg_val_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_VAL_POSITIVE_VALS",
                "dimension": "validity",
                "entity": "transactions",
                "field": "gross_value,quantity",
                "records_checked": total_tx,
                "records_failed": neg_val_count,
                "failure_rate": round(float(neg_val_count / total_tx), 6),
                "status": "PASSED" if neg_val_count == 0 else "FAILED",
                "severity": "CRITICAL",
                "description": "Validation of positive quantity and gross_value",
            }
        )

        # Non-negative fees
        neg_fee_mask = transactions_df["fee"] < 0
        neg_fee_count = int(neg_fee_mask.sum())
        if neg_fee_count > 0:
            failing_indices.update(transactions_df[neg_fee_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_VAL_NON_NEG_FEE",
                "dimension": "validity",
                "entity": "transactions",
                "field": "fee",
                "records_checked": total_tx,
                "records_failed": neg_fee_count,
                "failure_rate": round(float(neg_fee_count / total_tx), 6),
                "status": "PASSED" if neg_fee_count == 0 else "FAILED",
                "severity": "HIGH",
                "description": "Validation that platform fee is non-negative",
            }
        )

        # 3. CONSISTENCY CHECKS (gross_value ≈ quantity * price within tolerance)
        expected_gross = transactions_df["quantity"] * transactions_df["price"]
        diff_pct = np.abs(transactions_df["gross_value"] - expected_gross) / np.maximum(
            expected_gross, 1e-4
        )
        inconsistent_math_mask = diff_pct > (self.tolerance_pct / 100.0)
        inconsistent_math_count = int(inconsistent_math_mask.sum())
        if inconsistent_math_count > 0:
            failing_indices.update(transactions_df[inconsistent_math_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_CON_MATH_BALANCE",
                "dimension": "consistency",
                "entity": "transactions",
                "field": "gross_value",
                "records_checked": total_tx,
                "records_failed": inconsistent_math_count,
                "failure_rate": round(float(inconsistent_math_count / total_tx), 6),
                "status": "PASSED" if inconsistent_math_count == 0 else "FAILED",
                "severity": "HIGH",
                "description": f"Mathematical reconciliation: gross_value ≈ quantity * price within ±{self.tolerance_pct}%",
            }
        )

        # 4. UNIQUENESS CHECKS (duplicate transaction_id)
        duplicate_mask = transactions_df.duplicated(subset=["transaction_id"], keep=False)
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count > 0:
            failing_indices.update(transactions_df[duplicate_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_UNQ_TX_ID",
                "dimension": "uniqueness",
                "entity": "transactions",
                "field": "transaction_id",
                "records_checked": total_tx,
                "records_failed": duplicate_count,
                "failure_rate": round(float(duplicate_count / total_tx), 6),
                "status": "PASSED" if duplicate_count == 0 else "FAILED",
                "severity": "CRITICAL",
                "description": "Zero duplicate primary key assertion",
            }
        )

        # 5. REFERENTIAL INTEGRITY CHECKS
        valid_user_set = set(users_df["user_id"])
        orphan_user_mask = ~transactions_df["user_id"].isin(valid_user_set)
        orphan_user_count = int(orphan_user_mask.sum())
        if orphan_user_count > 0:
            failing_indices.update(transactions_df[orphan_user_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_REF_USER_EXISTS",
                "dimension": "referential_integrity",
                "entity": "transactions",
                "field": "user_id",
                "records_checked": total_tx,
                "records_failed": orphan_user_count,
                "failure_rate": round(float(orphan_user_count / total_tx), 6),
                "status": "PASSED" if orphan_user_count == 0 else "FAILED",
                "severity": "CRITICAL",
                "description": "Foreign key reference: transaction.user_id exists in dim_users",
            }
        )

        valid_asset_set = set(assets_df["asset_id"]).union({"INR"})
        orphan_asset_mask = ~transactions_df["asset_id"].isin(valid_asset_set)
        orphan_asset_count = int(orphan_asset_mask.sum())
        if orphan_asset_count > 0:
            failing_indices.update(transactions_df[orphan_asset_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_REF_ASSET_EXISTS",
                "dimension": "referential_integrity",
                "entity": "transactions",
                "field": "asset_id",
                "records_checked": total_tx,
                "records_failed": orphan_asset_count,
                "failure_rate": round(float(orphan_asset_count / total_tx), 6),
                "status": "PASSED" if orphan_asset_count == 0 else "FAILED",
                "severity": "CRITICAL",
                "description": "Foreign key reference: transaction.asset_id exists in dim_assets",
            }
        )

        # 6. TIMELINESS CHECKS (future dated transactions)
        now_utc = datetime.now(timezone.utc)
        # Ensure timestamp is tz-aware
        tx_ts = pd.to_datetime(transactions_df["timestamp"], utc=True)
        future_mask = tx_ts > (now_utc + pd.Timedelta(minutes=5))
        future_count = int(future_mask.sum())
        if future_count > 0:
            failing_indices.update(transactions_df[future_mask].index)
        self.check_results.append(
            {
                "check_id": "CHK_TIM_FUTURE_DATED",
                "dimension": "timeliness",
                "entity": "transactions",
                "field": "timestamp",
                "records_checked": total_tx,
                "records_failed": future_count,
                "failure_rate": round(float(future_count / total_tx), 6),
                "status": "PASSED" if future_count == 0 else "FAILED",
                "severity": "MEDIUM",
                "description": "Check that transactions are not future-dated past UTC threshold",
            }
        )

        # Separate clean vs quarantined data
        clean_df = transactions_df.drop(index=list(failing_indices)).copy()
        quarantined_df = transactions_df.loc[list(failing_indices)].copy()

        # Compute dimension failure rates and aggregate score
        dim_fail_rates = {}
        for dim in self.weights.keys():
            dim_checks = [c for c in self.check_results if c["dimension"] == dim]
            if dim_checks:
                dim_fail_rates[dim] = max(c["failure_rate"] for c in dim_checks)
            else:
                dim_fail_rates[dim] = 0.0

        dq_score = 100.0 * sum(
            self.weights[dim] * (1.0 - dim_fail_rates[dim]) for dim in self.weights.keys()
        )
        dq_score = max(0.0, min(100.0, round(dq_score, 2)))

        report = {
            "evaluation_timestamp": now_utc.isoformat(),
            "records_evaluated": total_tx,
            "records_passed": len(clean_df),
            "records_quarantined": len(quarantined_df),
            "data_quality_score": dq_score,
            "dimension_scores": {
                dim: round(100.0 * (1.0 - dim_fail_rates[dim]), 2) for dim in self.weights.keys()
            },
            "checks_executed": len(self.check_results),
            "checks_passed": sum(1 for c in self.check_results if c["status"] == "PASSED"),
            "checks_failed": sum(1 for c in self.check_results if c["status"] == "FAILED"),
            "detailed_checks": self.check_results,
        }

        logger.info(
            "Data Quality evaluation complete. Score: %.2f/100. Clean: %d, Quarantined: %d",
            dq_score,
            len(clean_df),
            len(quarantined_df),
        )
        return clean_df, quarantined_df, report

    def save_report(self, report: Dict[str, Any], output_dir: str = "outputs/quality"):
        """Exports data quality report in JSON, CSV, and summary Markdown."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        with open(path / "data_quality_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        checks_df = pd.DataFrame(report["detailed_checks"])
        checks_df.to_csv(path / "data_quality_checks.csv", index=False)

        # Markdown executive scorecard
        md = f"""# Data Quality Audit Report

**Audit Date:** {report['evaluation_timestamp']}  
**Overall Data Quality Score:** **{report['data_quality_score']} / 100.0**  
**Total Records Evaluated:** {report['records_evaluated']:,}  
**Clean Records Loaded:** {report['records_passed']:,} ({report['records_passed']/report['records_evaluated']*100:.2f}%)  
**Quarantined Records:** {report['records_quarantined']:,}  

---

## Dimension Breakdown

| Dimension | Weight | Dimension Score (%) |
| :--- | :--- | :--- |
| **Completeness** | 25% | {report['dimension_scores']['completeness']}% |
| **Validity** | 20% | {report['dimension_scores']['validity']}% |
| **Consistency** | 20% | {report['dimension_scores']['consistency']}% |
| **Uniqueness** | 15% | {report['dimension_scores']['uniqueness']}% |
| **Referential Integrity** | 10% | {report['dimension_scores']['referential_integrity']}% |
| **Timeliness** | 10% | {report['dimension_scores']['timeliness']}% |

---

## Detailed Check Results

| Check ID | Dimension | Field | Records Checked | Failed | Failure Rate | Status | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for c in report["detailed_checks"]:
            md += f"| `{c['check_id']}` | {c['dimension']} | `{c['field']}` | {c['records_checked']:,} | {c['records_failed']:,} | {c['failure_rate']:.4%} | **{c['status']}** | {c['severity']} |\n"

        with open(path / "data_quality_summary.md", "w", encoding="utf-8") as f:
            f.write(md)
        logger.info("Exported Data Quality reports to %s", output_dir)


if __name__ == "__main__":
    from python.ingestion.synthetic_generator import SyntheticExchangeDataGenerator

    gen = SyntheticExchangeDataGenerator()
    assets = gen.generate_assets()
    users = gen.generate_users()
    txs, _ = gen.generate_transactions()

    engine = DataQualityEngine()
    clean, quarantined, rpt = engine.run_all_checks(txs, users, assets)
    engine.save_report(rpt)
    print("Data Quality Engine test completed successfully!")
