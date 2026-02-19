"""Simple tests for coverage."""

import sys
from pathlib import Path


def test_connector_import():
    """Test that connector can be imported."""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.utils.duckdb_connector import DuckDBConnector
    assert DuckDBConnector is not None


def test_connector_init():
    """Test that connector initializes."""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.utils.duckdb_connector import DuckDBConnector
    connector = DuckDBConnector()
    assert connector is not None
    assert connector.db_path is not None
