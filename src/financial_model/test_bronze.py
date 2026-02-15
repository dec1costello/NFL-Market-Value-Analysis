"""
Test script to query bronze dbt model data from DuckDB
Run this after running 'dbt run' to ensure data is loaded
"""

from src.utils.duckdb_connector import DuckDBConnector

print("=" * 60)
print("TESTING BRONZE LAYER - RAW CONTRACTS DATA")
print("=" * 60)

with DuckDBConnector() as db:
    # Check database exists
    print(f"Database path: {db.db_path}")
    print(f"Database exists: {db.db_path.exists()}")

    # Show available tables
    print("\n📊 AVAILABLE TABLES IN DATABASE")
    print("-" * 40)
    tables = db.get_table_info()
    print(tables.to_string(index=False))

    # Test 1: Bronze table overview
    print("\n📊 TEST 1: Bronze table overview")
    print("-" * 40)

    try:
        bronze_check = db.query("""
            SELECT
                COUNT(*) as row_count,
                COUNT(DISTINCT position) as unique_positions
            FROM main_bronze.contracts
        """)
        print(bronze_check.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Sample data
    print("\n📊 TEST 2: Sample of bronze data")
    print("-" * 40)

    try:
        sample = db.query("""
            SELECT
                rank, player_name, position, team_signed_with,
                years, total_value, average_salary
            FROM main_bronze.contracts
            LIMIT 5
        """)
        print(sample.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("✅ Bronze layer tests complete!")
print("=" * 60)
