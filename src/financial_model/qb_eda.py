import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent.parent

# Path to your contracts data
contracts_path = project_root / 'data' / 'raw' / 'NFL_Contracts.csv'

print(f"Loading file from: {contracts_path}")

# Try to read with different options to handle the messy headers
# Option 1: Skip the first few rows if they're not actual data
# contracts_df = pd.read_csv(contracts_path, skiprows=2)  # Adjust skiprows as needed

# Option 2: Read with no header and then assign proper column names
contracts_df = pd.read_csv(contracts_path, header=None)

# Let's see what the first few rows look like
print("\nFirst 5 rows of raw data:")
print(contracts_df.head(10))

# Look at the shape
print(f"\nDataset shape: {contracts_df.shape}")

# Check what might be the header row (usually the row with actual column names)
print("\nPossible header row (row 0):")
print(contracts_df.iloc[0].tolist())

print("\nPossible data start (row 1):")
print(contracts_df.iloc[1].tolist())

print("\nPossible data start (row 2):")
print(contracts_df.iloc[2].tolist())

# You might want to skip the first few rows and use row 2 as header
# contracts_df = pd.read_csv(contracts_path, skiprows=2, header=0)

# Or you might want to assign custom column names
custom_columns = ['rank', 'player', 'team', 'position', 'contract_value', 
                  'guaranteed', 'average_per_year', 'years', 'signing_bonus',
                  'gtd_at_signing', 'other_bonus', 'cap_hit_2024', 
                  'cap_hit_2025', 'cap_hit_2026', 'total_value', 'notes']

# Read with custom column names (adjust based on what you see in the data)
# contracts_df = pd.read_csv(contracts_path, skiprows=1, names=custom_columns)

print("\n✅ Script completed successfully!")