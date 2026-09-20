"""
Database Loader and Orchestration Module.
Loads validated data into DuckDB/PostgreSQL relational tables, creates views,
and extracts analytical reporting outputs.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from python.common.config import load_config
from python.common.db import DatabaseConnection
from python.common.logger import get_logger

logger = get_logger()


class DatabaseLoader:
    """Manages schema creation, dimensional staging, and analytical loading."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.db = DatabaseConnection(self.config)

    def initialize_schema(self, schema_file: str = "sql/schema/create_tables.sql"):
        """Executes DDL to create tables and indexes."""
        logger.info("Initializing relational schema from %s", schema_file)
        with open(schema_file, "r", encoding="utf-8") as f:
            ddl = f.read()

        # Split and execute individual DDL statements
        for statement in ddl.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    self.db.execute(stmt)
                except Exception as e:
                    logger.warning("DDL execution notice on: %s...: %s", stmt[:40], str(e))

    def load_date_dimension(
        self, start_date: str = "2026-01-01", end_date: str = "2026-12-31"
    ):
        """Populates dim_dates with temporal calendar attributes."""
        logger.info("Populating dim_dates from %s to %s", start_date, end_date)
        dt_start = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end = datetime.strptime(end_date, "%Y-%m-%d")

        records = []
        curr = dt_start
        while curr <= dt_end:
            records.append(
                {
                    "date_key": int(curr.strftime("%Y%m%d")),
                    "calendar_date": curr.date(),
                    "year": curr.year,
                    "quarter": (curr.month - 1) // 3 + 1,
                    "month": curr.month,
                    "month_name": curr.strftime("%B"),
                    "day_of_month": curr.day,
                    "day_of_week": curr.weekday() + 1,
                    "day_name": curr.strftime("%A"),
                    "is_weekend": curr.weekday() >= 5,
                }
            )
            curr += timedelta(days=1)

        dates_df = pd.DataFrame(records)
        # Load into db
        if self.db.engine_type == "duckdb":
            self.db.conn.register("df_dates_temp", dates_df)
            self.db.execute("INSERT OR REPLACE INTO dim_dates SELECT * FROM df_dates_temp")
            self.db.conn.unregister("df_dates_temp")
        logger.info("dim_dates populated with %d rows", len(dates_df))
        return dates_df

    def load_clean_data(
        self,
        users_df: pd.DataFrame,
        assets_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        market_ticks_df: Optional[pd.DataFrame] = None,
        anomalies_df: Optional[pd.DataFrame] = None,
        incidents_df: Optional[pd.DataFrame] = None,
    ):
        """Loads clean dimensional entities and fact tables into the database."""
        logger.info("Loading clean tables into database engine: %s", self.db.engine_type)

        if self.db.engine_type == "duckdb":
            # Ensure clean tables on fresh run to guarantee idempotent loading
            for tbl in ["fact_transactions", "fact_market_ticks", "fact_anomalies", "fact_incidents", "dim_users", "dim_assets"]:
                try:
                    self.db.execute(f"DELETE FROM {tbl}")
                except Exception:
                    pass

            # 1. Users
            cols_users = [
                "user_id",
                "signup_date",
                "country",
                "user_segment",
                "account_type",
                "risk_tier",
                "base_spend_mean",
                "base_spend_std",
            ]
            self.db.conn.register("df_users_temp", users_df[cols_users])
            self.db.execute("INSERT OR REPLACE INTO dim_users SELECT * FROM df_users_temp")
            self.db.conn.unregister("df_users_temp")

            # 2. Assets
            cols_assets = [
                "asset_id",
                "symbol",
                "name",
                "category",
                "is_stablecoin",
                "base_price_inr",
                "volatility",
            ]
            self.db.conn.register("df_assets_temp", assets_df[cols_assets])
            self.db.execute("INSERT OR REPLACE INTO dim_assets SELECT * FROM df_assets_temp")
            self.db.conn.unregister("df_assets_temp")

            # 3. Transactions
            cols_tx = [
                "transaction_id",
                "user_id",
                "asset_id",
                "date_key",
                "timestamp",
                "transaction_type",
                "side",
                "quantity",
                "price",
                "gross_value",
                "fee",
                "net_value",
                "status",
                "payment_method",
                "device_type",
                "is_injected_anomaly",
                "injected_typology",
            ]
            self.db.conn.register("df_tx_temp", transactions_df[cols_tx])
            self.db.execute("INSERT OR REPLACE INTO fact_transactions SELECT * FROM df_tx_temp")
            self.db.conn.unregister("df_tx_temp")

            # 4. Market Ticks
            if market_ticks_df is not None and not market_ticks_df.empty:
                cols_ticks = [
                    "market_symbol",
                    "asset_id",
                    "date_key",
                    "timestamp",
                    "price",
                    "high",
                    "low",
                    "volume_24h",
                    "change_24h_pct",
                    "bid",
                    "ask",
                ]
                self.db.conn.register("df_ticks_temp", market_ticks_df[cols_ticks])
                self.db.execute("INSERT OR REPLACE INTO fact_market_ticks SELECT * FROM df_ticks_temp")
                self.db.conn.unregister("df_ticks_temp")

            # 5. Anomalies
            if anomalies_df is not None and not anomalies_df.empty:
                cols_ano = [
                    "anomaly_id",
                    "transaction_id",
                    "user_id",
                    "timestamp",
                    "anomaly_type",
                    "metric_name",
                    "observed_value",
                    "baseline_value",
                    "deviation_score",
                    "detector_method",
                    "explanation",
                ]
                self.db.conn.register("df_ano_temp", anomalies_df[cols_ano])
                self.db.execute("INSERT OR REPLACE INTO fact_anomalies SELECT * FROM df_ano_temp")
                self.db.conn.unregister("df_ano_temp")

            # 6. Incidents
            if incidents_df is not None and not incidents_df.empty:
                cols_inc = [
                    "incident_id",
                    "anomaly_id",
                    "transaction_id",
                    "user_id",
                    "created_at",
                    "severity",
                    "likelihood",
                    "exposure_inr",
                    "priority_score",
                    "priority_band",
                    "rationale",
                    "recommendation",
                    "status",
                ]
                self.db.conn.register("df_inc_temp", incidents_df[cols_inc])
                self.db.execute("INSERT OR REPLACE INTO fact_incidents SELECT * FROM df_inc_temp")
                self.db.conn.unregister("df_inc_temp")

        logger.info("Successfully loaded all clean tables into the database.")

    def create_views(self, views_file: str = "sql/views/analytical_views.sql"):
        """Compiles analytical and reporting views."""
        logger.info("Compiling analytical views from %s", views_file)
        with open(views_file, "r", encoding="utf-8") as f:
            views_sql = f.read()

        for statement in views_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    self.db.execute(stmt)
                except Exception as e:
                    logger.warning("View creation notice on: %s...: %s", stmt[:40], str(e))
        logger.info("Analytical views compiled successfully.")
