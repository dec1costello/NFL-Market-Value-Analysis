"""
Test script to query bronze dbt model data from DuckDB
Run this after running 'dbt run' to ensure data is loaded
"""

import duckdb
import pandas as pd
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent.parent

# Path to DuckDB database (created by dbt)
db_path = project_root / 'nfl_contracts.duckdb'

print("="*60)
print("TESTING BRONZE LAYER - RAW CONTRACTS DATA")
print("="*60)
print(f"Database path: {db_path}")
print(f"Database exists: {db_path.exists()}")

# Connect to DuckDB
conn = duckdb.connect(str(db_path))

# First, let's see what tables are available
print("\n📊 AVAILABLE TABLES IN DATABASE")
print("-"*40)
tables = conn.execute("""
    SELECT 
        table_schema, 
        table_name, 
        table_type
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY table_schema, table_name
""").fetchdf()
print(tables.to_string(index=False))

# Test 1: Check if bronze table exists and get basic info
print("\n📊 TEST 1: Bronze table overview (using main_bronze schema)")
print("-"*40)

try:
    bronze_check = conn.execute("""
        SELECT 
            'main_bronze.contracts' as table_name,
            COUNT(*) as row_count,
            COUNT(DISTINCT position) as unique_positions
        FROM main_bronze.contracts
    """).fetchdf()
    print(bronze_check)
except Exception as e:
    print(f"Error querying main_bronze.contracts: {e}")
    
    # Try alternative schema names
    for schema in ['bronze', 'main_bronze', 'dbt_bronze']:
        try:
            print(f"\nTrying {schema}.contracts...")
            test = conn.execute(f"SELECT COUNT(*) as cnt FROM {schema}.contracts").fetchdf()
            print(f"✅ Found {schema}.contracts with {test.iloc[0,0]} rows")
            break
        except:
            print(f"❌ {schema}.contracts not found")

# Test 2: Sample of raw bronze data
print("\n📊 TEST 2: Sample of bronze data (first 5 rows)")
print("-"*40)

try:
    sample_data = conn.execute("""
        SELECT 
            rank,
            player_name,
            position,
            team_signed_with,
            years,
            total_value,
            average_salary
        FROM main_bronze.contracts
        LIMIT 5
    """).fetchdf()
    print(sample_data.to_string(index=False))
except Exception as e:
    print(f"Could not query data: {e}")

# Test 3: Position distribution in bronze
print("\n📊 TEST 3: Position distribution in bronze")
print("-"*40)

try:
    position_dist = conn.execute("""
        SELECT 
            position,
            COUNT(*) as contract_count,
            ROUND(AVG(total_value), 2) as avg_contract_value,
            ROUND(MIN(total_value), 2) as min_value,
            ROUND(MAX(total_value), 2) as max_value
        FROM main_bronze.contracts
        WHERE position IS NOT NULL 
            AND position != ''
            AND position != 'Pos'
        GROUP BY position
        ORDER BY contract_count DESC
        LIMIT 10
    """).fetchdf()
    print(position_dist.to_string(index=False))
except Exception as e:
    print(f"Could not get position distribution: {e}")

# Test 4: Year range of contracts
print("\n📊 TEST 4: Contract year range")
print("-"*40)

try:
    year_range = conn.execute("""
        SELECT 
            MIN(start_year) as earliest_year,
            MAX(start_year) as latest_year,
            COUNT(DISTINCT start_year) as unique_years
        FROM main_bronze.contracts
        WHERE start_year IS NOT NULL
    """).fetchdf()
    print(year_range.to_string(index=False))
except Exception as e:
    print(f"Could not get year range: {e}")

# Test 5: Check for data quality - nulls in key fields
print("\n📊 TEST 5: Data quality check - null values")
print("-"*40)

try:
    null_checks = conn.execute("""
        SELECT 
            SUM(CASE WHEN player_name IS NULL THEN 1 ELSE 0 END) as null_players,
            SUM(CASE WHEN position IS NULL THEN 1 ELSE 0 END) as null_positions,
            SUM(CASE WHEN total_value IS NULL THEN 1 ELSE 0 END) as null_values,
            SUM(CASE WHEN years IS NULL THEN 1 ELSE 0 END) as null_years,
            COUNT(*) as total_rows
        FROM main_bronze.contracts
    """).fetchdf()
    print(null_checks.to_string(index=False))
except Exception as e:
    print(f"Could not check nulls: {e}")

# Test 6: Top 5 contracts by value
print("\n📊 TEST 6: Top 5 contracts by total value")
print("-"*40)

try:
    top_contracts = conn.execute("""
        SELECT 
            player_name,
            position,
            team_signed_with,
            start_year,
            years,
            total_value,
            average_salary
        FROM main_bronze.contracts
        WHERE total_value IS NOT NULL
        ORDER BY total_value DESC
        LIMIT 5
    """).fetchdf()
    print(top_contracts.to_string(index=False))
except Exception as e:
    print(f"Could not get top contracts: {e}")

# Test 7: Quick validation against known QB data
print("\n📊 TEST 7: Quick QB validation")
print("-"*40)

try:
    qb_check = conn.execute("""
        SELECT 
            player_name,
            team_signed_with,
            start_year,
            years,
            total_value,
            average_salary
        FROM main_bronze.contracts
        WHERE position = 'QB'
            AND player_name IN ('Patrick Mahomes', 'Joe Burrow', 'Justin Herbert')
        ORDER BY total_value DESC
    """).fetchdf()
    print(qb_check.to_string(index=False))
except Exception as e:
    print(f"Could not validate QB data: {e}")

# Close connection
conn.close()

print("\n" + "="*60)
print("✅ Bronze layer tests complete!")
print("="*60)