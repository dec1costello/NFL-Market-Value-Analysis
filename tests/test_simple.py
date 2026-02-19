"""Simple tests for coverage."""

import sys
from pathlib import Path
import tempfile
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.duckdb_connector import DuckDBConnector


def test_connector_import():
    """Test that connector can be imported."""
    from src.utils.duckdb_connector import DuckDBConnector
    assert DuckDBConnector is not None


def test_connector_init():
    """Test that connector initializes."""
    connector = DuckDBConnector()
    assert connector is not None
    assert connector.db_path is not None
    assert connector.db_path.name == "superbowl.duckdb"


def test_connector_custom_path():
    """Test connector with custom path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_path = Path(tmpdir) / "test.duckdb"
        connector = DuckDBConnector(custom_path)
        assert connector.db_path == custom_path


def test_connect_disconnect():
    """Test connect and disconnect methods."""
    connector = DuckDBConnector()
    connector.connect()
    assert connector.conn is not None
    connector.disconnect()
    assert connector.conn is None


def test_context_manager():
    """Test context manager works."""
    with DuckDBConnector() as connector:
        assert connector.conn is not None
        # Run a simple query
        result = connector.query("SELECT 1 as test")
        assert result is not None
    # Should be disconnected after context
    assert connector.conn is None


def test_get_table_info():
    """Test get_table_info method."""
    with DuckDBConnector() as connector:
        tables = connector.get_table_info()
        assert isinstance(tables, pd.DataFrame)
        # Should have at least some tables
        assert len(tables) > 0
