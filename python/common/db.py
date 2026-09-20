"""
Database connector and abstraction for PostgreSQL and embedded DuckDB.
"""

from typing import Any, Optional
import duckdb
from python.common.config import load_config
from python.common.logger import get_logger

logger = get_logger()


class DatabaseConnection:
    """Provides a managed connection to either embedded DuckDB or external PostgreSQL."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.engine_type = self.config.get("database", {}).get("engine", "duckdb").lower()
        self.duckdb_path = self.config.get("database", {}).get(
            "duckdb_path", "data/processed/exchange_control_desk.duckdb"
        )
        self.conn = None

    def connect(self):
        """Establishes database connection."""
        if self.engine_type == "duckdb":
            logger.info("Connecting to embedded DuckDB at: %s", self.duckdb_path)
            self.conn = duckdb.connect(self.duckdb_path)
        elif self.engine_type == "postgresql":
            import psycopg

            pg_conf = self.config.get("database", {}).get("postgres", {})
            conn_info = (
                f"host={pg_conf.get('host', 'localhost')} "
                f"port={pg_conf.get('port', 5432)} "
                f"dbname={pg_conf.get('dbname', 'exchange_control_desk')} "
                f"user={pg_conf.get('user', 'postgres')} "
                f"password={pg_conf.get('password', '')}"
            )
            logger.info("Connecting to PostgreSQL at %s:%s", pg_conf.get("host"), pg_conf.get("port"))
            self.conn = psycopg.connect(conn_info)
        else:
            raise ValueError(f"Unsupported database engine: {self.engine_type}")
        return self.conn

    def execute(self, query: str, params: Optional[Any] = None):
        """Executes a SQL statement."""
        if self.conn is None:
            self.connect()
        if params:
            return self.conn.execute(query, params)
        return self.conn.execute(query)

    def query_df(self, query: str, params: Optional[Any] = None):
        """Executes a SQL query and returns a pandas DataFrame."""
        if self.conn is None:
            self.connect()
        if self.engine_type == "duckdb":
            if params:
                return self.conn.execute(query, params).df()
            return self.conn.execute(query).df()
        else:
            import pandas as pd

            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=cols)

    def close(self):
        """Closes connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")
