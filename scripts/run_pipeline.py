"""
Master End-to-End Pipeline Execution Script.
Executes the full pipeline in order: Ingestion -> DQ -> DB Load -> Transformations ->
Feature Engineering -> Anomaly Detection -> Prioritization -> Reporting & Reconciliation.
"""

import sys
import time
from pathlib import Path
from python.common.config import load_config
from python.common.db import DatabaseConnection
from python.common.loader import DatabaseLoader
from python.common.logger import setup_logger
from python.ingestion.market_data import MarketDataIngestion
from python.ingestion.synthetic_generator import SyntheticExchangeDataGenerator
from python.validation.data_quality import DataQualityEngine
from python.feature_engineering.features import FeatureEngineeringEngine
from python.anomaly_detection.engine import AnomalyDetectionEngine
from python.anomaly_detection.evaluator import AnomalyEvaluator
from python.incidents.prioritization import IncidentPrioritizationEngine
from python.reporting.market_intelligence import MarketIntelligenceEngine
from python.reporting.reporting_engine import ReportingEngine
from python.reporting.reconciliation import ReconciliationEngine

logger = setup_logger()


def run_pipeline():
    """Runs the complete end-to-end analytical pipeline."""
    start_total = time.time()
    logger.info("==================================================================")
    logger.info("STARTING MASTER PIPELINE: EXCHANGE CONTROL DESK")
    logger.info("==================================================================")

    config = load_config()

    # Step 1: Ingest Market Data
    t0 = time.time()
    market_ingestor = MarketDataIngestion(config)
    market_ticks_df = market_ingestor.ingest_market_ticks()
    logger.info("Step 1 [Market Ingestion] completed in %.2fs", time.time() - t0)

    # Step 2: Generate Synthetic Exchange Entities
    t0 = time.time()
    generator = SyntheticExchangeDataGenerator(config)
    assets_df = generator.generate_assets()
    users_df = generator.generate_users()
    transactions_df, ground_truth_df = generator.generate_transactions()
    generator.save_datasets()
    logger.info("Step 2 [Synthetic Generation] completed in %.2fs", time.time() - t0)

    # Step 3: Automated Data Quality Engine
    t0 = time.time()
    dq_engine = DataQualityEngine(config)
    clean_tx_df, quarantined_tx_df, dq_report = dq_engine.run_all_checks(
        transactions_df, users_df, assets_df
    )
    dq_engine.save_report(dq_report)
    logger.info("Step 3 [Data Quality] completed in %.2fs (Score: %.1f/100)", time.time() - t0, dq_report['data_quality_score'])

    # Step 4: Feature Engineering
    t0 = time.time()
    fe_engine = FeatureEngineeringEngine(config)
    enriched_tx_df = fe_engine.extract_features(clean_tx_df, users_df, assets_df)
    logger.info("Step 4 [Feature Engineering] completed in %.2fs", time.time() - t0)

    # Step 5: Anomaly Detection & Ground Truth Evaluation
    t0 = time.time()
    ano_engine = AnomalyDetectionEngine(config)
    anomalies_df = ano_engine.detect_anomalies(enriched_tx_df)

    evaluator = AnomalyEvaluator()
    eval_report = evaluator.evaluate(enriched_tx_df, anomalies_df)
    logger.info(
        "Step 5 [Anomaly Detection & Eval] completed in %.2fs (Precision: %.1f%%, Recall: %.1f%%)",
        time.time() - t0,
        eval_report["precision"] * 100,
        eval_report["recall"] * 100,
    )

    # Step 6: Incident Prioritization & Investigation Queue
    t0 = time.time()
    inc_engine = IncidentPrioritizationEngine(config)
    incidents_df = inc_engine.prioritize_incidents(anomalies_df)
    inc_engine.export_queue(incidents_df)
    logger.info("Step 6 [Incident Prioritization] completed in %.2fs (%d incidents)", time.time() - t0, len(incidents_df))

    # Step 7: Relational Database Loading & Analytical Views
    t0 = time.time()
    loader = DatabaseLoader(config)
    loader.initialize_schema()
    loader.load_date_dimension()
    loader.load_clean_data(
        users_df=users_df,
        assets_df=assets_df,
        transactions_df=enriched_tx_df,
        market_ticks_df=market_ticks_df,
        anomalies_df=anomalies_df,
        incidents_df=incidents_df,
    )
    loader.create_views()
    logger.info("Step 7 [Database Loading & Views] completed in %.2fs", time.time() - t0)

    # Step 8: Market Intelligence & Segmentation
    t0 = time.time()
    mi_engine = MarketIntelligenceEngine()
    mi_engine.compute_market_divergence(clean_tx_df, market_ticks_df)
    mi_engine.segment_users(clean_tx_df, users_df)
    logger.info("Step 8 [Market Intelligence & Segmentation] completed in %.2fs", time.time() - t0)

    # Step 9: Reporting, Visuals & Power BI Dataset Exports
    t0 = time.time()
    reporting = ReportingEngine(loader.db)
    reporting.export_powerbi_datasets()
    reporting.generate_visual_artifacts()
    reporting.generate_executive_summary(dq_report, eval_report)
    logger.info("Step 9 [Reporting & Visual Artifacts] completed in %.2fs", time.time() - t0)

    # Step 10: Zero-Tolerance Cross-System Reconciliation
    t0 = time.time()
    reconciliation = ReconciliationEngine(loader.db)
    recon_passed, recon_df = reconciliation.reconcile_kpis(clean_tx_df)
    logger.info("Step 10 [Reconciliation Audit] completed in %.2fs (Passed: %s)", time.time() - t0, recon_passed)

    loader.db.close()

    total_duration = time.time() - start_total
    logger.info("==================================================================")
    logger.info("MASTER PIPELINE COMPLETED SUCCESSFULLY in %.2f seconds", total_duration)
    logger.info("==================================================================")
    return {
        "total_duration": total_duration,
        "records_processed": len(clean_tx_df),
        "anomalies_detected": len(anomalies_df),
        "incidents_triaged": len(incidents_df),
        "data_quality_score": dq_report["data_quality_score"],
        "reconciliation_passed": recon_passed,
    }


if __name__ == "__main__":
    run_pipeline()
