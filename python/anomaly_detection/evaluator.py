"""
Synthetic Evaluation Module for Anomaly Detection.
Compares detector output against injected ground truth labels and computes
Precision, Recall, F1-Score, and False Positive Rates.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from python.common.logger import get_logger

logger = get_logger()


class AnomalyEvaluator:
    """Evaluates detection performance on controlled synthetic ground truth."""

    def evaluate(
        self,
        transactions_df: pd.DataFrame,
        detected_anomalies_df: pd.DataFrame,
        output_dir: str = "outputs/anomalies",
    ) -> Dict[str, Any]:
        """Calculates confusion matrix and precision/recall across all typologies."""
        logger.info("Evaluating anomaly detection against synthetic ground truth")

        # Flagged transaction IDs by the detector
        detected_tx_ids = set(detected_anomalies_df["transaction_id"].dropna())

        # Ground truth flag in transactions
        gt_mask = transactions_df["is_injected_anomaly"] == True
        gt_tx_ids = set(transactions_df[gt_mask]["transaction_id"])
        clean_tx_ids = set(transactions_df[~gt_mask]["transaction_id"])

        tp = len(detected_tx_ids.intersection(gt_tx_ids))
        fp = len(detected_tx_ids.intersection(clean_tx_ids))
        fn = len(gt_tx_ids.difference(detected_tx_ids))
        tn = len(clean_tx_ids.difference(detected_tx_ids))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        # Typology level breakdown
        typology_metrics = []
        for typology, group in transactions_df[gt_mask].groupby("injected_typology"):
            group_ids = set(group["transaction_id"])
            typ_tp = len(detected_tx_ids.intersection(group_ids))
            typ_fn = len(group_ids.difference(detected_tx_ids))
            typ_recall = typ_tp / len(group_ids) if len(group_ids) > 0 else 0.0
            typology_metrics.append(
                {
                    "typology": typology,
                    "injected_count": len(group_ids),
                    "detected_count": typ_tp,
                    "missed_count": typ_fn,
                    "recall": round(typ_recall, 4),
                }
            )

        evaluation_result = {
            "evaluation_type": "Synthetic Ground Truth Benchmark",
            "total_transactions": len(transactions_df),
            "ground_truth_anomalies": len(gt_tx_ids),
            "detected_anomalies": len(detected_tx_ids),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "false_positive_rate": round(fpr, 6),
            "typology_breakdown": typology_metrics,
        }

        # Export metrics
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        summary_df = pd.DataFrame(
            [
                {"Metric": "Total Transactions", "Value": len(transactions_df)},
                {"Metric": "Ground Truth Injected", "Value": len(gt_tx_ids)},
                {"Metric": "Total Detected", "Value": len(detected_tx_ids)},
                {"Metric": "True Positives (TP)", "Value": tp},
                {"Metric": "False Positives (FP)", "Value": fp},
                {"Metric": "False Negatives (FN)", "Value": fn},
                {"Metric": "Precision", "Value": f"{precision:.2%}"},
                {"Metric": "Recall", "Value": f"{recall:.2%}"},
                {"Metric": "F1-Score", "Value": f"{f1_score:.4f}"},
                {"Metric": "False Positive Rate", "Value": f"{fpr:.4%}"},
            ]
        )
        summary_df.to_csv(path / "anomaly_evaluation.csv", index=False)
        pd.DataFrame(typology_metrics).to_csv(path / "typology_performance.csv", index=False)

        logger.info(
            "Evaluation complete: Precision: %.2f%%, Recall: %.2f%%, F1: %.4f",
            precision * 100,
            recall * 100,
            f1_score,
        )
        return evaluation_result
