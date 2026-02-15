"""
DuckDB connector utility for NFL Market Value Analysis.
Provides easy access to the DuckDB database created by dbt.
"""

import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDBConnector:
    """
    A connector class for DuckDB to easily query bronze, silver, and gold models.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """
        Initialize the DuckDB connector.

        Args:
            db_path: Path to the DuckDB database file. If None, uses default location.
        """
        if db_path is None:
            # Default to project root
            self.project_root = Path(__file__).parent.parent.parent
            self.db_path = self.project_root / "nfl_contracts.duckdb"
        else:
            self.db_path = Path(db_path)
            self.project_root = self.db_path.parent

        self.conn = None
        logger.info(f"DuckDBConnector initialized with database: {
                self.db_path}")

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Establish connection to DuckDB."""
        try:
            self.conn = duckdb.connect(str(self.db_path))
            logger.info(f"Connected to database: {self.db_path}")
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self  # Return self, not just the connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a DataFrame.

        Args:
            sql: SQL query string
            params: Optional parameters for the query

        Returns:
            pandas DataFrame with query results
        """
        if not self.conn:
            self.connect()

        try:
            if params:
                result = self.conn.execute(sql, params).fetchdf()
            else:
                result = self.conn.execute(sql).fetchdf()

            logger.info(f"Query executed successfully: {sql[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Query failed: {e}")
            logger.error(f"SQL: {sql}")
            raise

    def get_bronze_contracts(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Get contracts from bronze layer."""
        sql = "SELECT * FROM main_bronze.contracts"
        if limit:
            sql += f" LIMIT {limit}"
        return self.query(sql)

    def get_silver_qb_contracts(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Get QB contracts from silver layer."""
        sql = "SELECT * FROM main_silver.qb_contracts"
        if limit:
            sql += f" LIMIT {limit}"
        return self.query(sql)

    def get_top_contracts(self, position: str = "QB", n: int = 10) -> pd.DataFrame:
        """
        Get top N contracts by value for a specific position.

        Args:
            position: Player position (QB, RB, WR, etc.)
            n: Number of contracts to return

        Returns:
            DataFrame with top contracts
        """
        sql = """
        SELECT
            player_name,
            team_signed_with,
            start_year,
            years,
            total_value,
            average_salary,
            guarantee_at_signing
        FROM main_bronze.contracts
        WHERE position = ?
            AND total_value IS NOT NULL
        ORDER BY total_value DESC
        LIMIT ?
        """
        return self.query(sql, [position, n])

    def get_contracts_by_year(
        self, year: int, position: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get contracts signed in a specific year.

        Args:
            year: Start year of contract
            position: Optional position filter
        """
        sql = """
        SELECT
            player_name,
            position,
            team_signed_with,
            years,
            total_value,
            average_salary
        FROM main_bronze.contracts
        WHERE start_year = ?
        """
        if position:
            sql += " AND position = ?"
            params = [year, position]
        else:
            params = [year]

        sql += " ORDER BY total_value DESC"
        return self.query(sql, params)

    def get_position_summary(self) -> pd.DataFrame:
        """Get summary statistics by position."""
        sql = """
        SELECT
            position,
            COUNT(*) as contract_count,
            ROUND(AVG(total_value), 2) as avg_total_value,
            ROUND(AVG(average_salary), 2) as avg_annual_value,
            ROUND(AVG(years), 1) as avg_length,
            ROUND(MIN(total_value), 2) as min_value,
            ROUND(MAX(total_value), 2) as max_value,
            ROUND(AVG(guarantee_at_signing), 2) as avg_guarantee
        FROM main_bronze.contracts
        WHERE position IS NOT NULL
            AND position NOT IN ('', 'Pos')
        GROUP BY position
        ORDER BY avg_total_value DESC
        """
        return self.query(sql)

    def get_team_summary(self) -> pd.DataFrame:
        """Get team spending summary."""
        sql = """
        SELECT
            team_signed_with as team,
            COUNT(*) as total_contracts,
            ROUND(SUM(total_value), 2) as total_spent,
            ROUND(AVG(total_value), 2) as avg_contract_value,
            COUNT(DISTINCT position) as positions_signed
        FROM main_bronze.contracts
        WHERE team_signed_with IS NOT NULL
        GROUP BY team_signed_with
        ORDER BY total_spent DESC
        """
        return self.query(sql)

    def get_qb_market_trends(self) -> pd.DataFrame:
        """Get QB market trends over time."""
        sql = """
        SELECT
            start_year,
            COUNT(*) as num_contracts,
            ROUND(AVG(total_value), 2) as avg_total_value,
            ROUND(AVG(average_salary), 2) as avg_annual_value,
            ROUND(AVG(years), 1) as avg_length,
            ROUND(AVG(avg_percent_of_cap), 4) as avg_cap_percentage,
            ROUND(MAX(total_value), 2) as max_value,
            ROUND(MIN(total_value), 2) as min_value
        FROM main_bronze.contracts
        WHERE position = 'QB'
            AND start_year >= 2010
            AND total_value IS NOT NULL
        GROUP BY start_year
        ORDER BY start_year
        """
        return self.query(sql)

    def search_players(self, search_term: str) -> pd.DataFrame:
        """Search for players by name."""
        sql = """
        SELECT
            player_name,
            position,
            team_signed_with,
            start_year,
            total_value,
            years
        FROM main_bronze.contracts
        WHERE LOWER(player_name) LIKE LOWER(?)
        ORDER BY total_value DESC
        """
        return self.query(sql, [f"%{search_term}%"])

    def get_table_info(self) -> pd.DataFrame:
        """Get information about available tables."""
        sql = """
        SELECT
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
        """
        return self.query(sql)

    def get_column_info(self, table_name: str) -> pd.DataFrame:
        """Get column information for a specific table."""
        sql = """
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = ?
        ORDER BY ordinal_position
        """
        return self.query(sql, [table_name])

    def execute_dbt_model(self, model_name: str) -> None:
        """
        Execute a dbt model (requires dbt installed).

        Note: This runs a shell command, use with caution.
        """
        import subprocess
        import os

        dbt_dir = self.project_root / "dbt"
        if not dbt_dir.exists():
            logger.warning(f"dbt directory not found at {dbt_dir}")
            return

        try:
            cmd = f"cd {dbt_dir} && dbt run --select {model_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"dbt model {model_name} executed successfully")
            else:
                logger.error(f"dbt model execution failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to execute dbt model: {e}")


# Convenience functions for quick access


def get_connector(db_path: Optional[Union[str, Path]] = None) -> DuckDBConnector:
    """Get a DuckDBConnector instance."""
    return DuckDBConnector(db_path)


def quick_query(sql: str, db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Quick one-off query without managing connections."""
    with DuckDBConnector(db_path) as conn:
        return conn.query(sql)


if __name__ == "__main__":
    # Example usage
    print("Testing DuckDB Connector...")

    # Initialize connector
    db = DuckDBConnector()

    try:
        # Connect and run some tests
        with db:
            # Get table info
            print("\n📊 Available tables:")
            tables = db.get_table_info()
            print(tables.to_string(index=False))

            # Get QB market trends
            print("\n📈 QB Market Trends:")
            trends = db.get_qb_market_trends()
            print(trends.head().to_string(index=False))

            # Get top contracts
            print("\n🏆 Top 5 QB Contracts:")
            top_qb = db.get_top_contracts(position="QB", n=5)
            print(top_qb.to_string(index=False))

            # Search for a player
            print("\n🔍 Searching for 'Mahomes':")
            mahomes = db.search_players("mahomes")
            print(mahomes.to_string(index=False))

    except Exception as e:
        print(f"Error: {e}")
