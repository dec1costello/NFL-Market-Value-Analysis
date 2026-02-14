# In src/financial_model/qb_eda.py
import pandas as pd
import os
from pathlib import Path

# Get the path to the project root (NFL-Market-Value-Analysis)
# This assumes qb_eda.py is in src/financial_model/
project_root = Path(__file__).parent.parent.parent  # Goes up 3 levels: financial_model/ -> src/ -> project root

contracts_path = project_root / 'data' / 'raw' / 'NFL_Contracts.csv'

print(f"Looking for file at: {contracts_path}")
print(f"File exists: {contracts_path.exists()}")

# Read the data
contracts_df = pd.read_csv(contracts_path)

# Rest of your EDA code...
print(contracts_df.head())
print(contracts_df.info())