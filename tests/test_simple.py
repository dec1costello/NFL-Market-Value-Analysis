"""Simple tests for coverage."""


def test_imports():
    """Test that imports work."""
    from src.utils.duckdb_connector import DuckDBConnector

    assert DuckDBConnector is not None


def test_paths():
    """Test that paths exist."""
    from pathlib import Path

    assert Path(__file__).parent.parent.exists()
