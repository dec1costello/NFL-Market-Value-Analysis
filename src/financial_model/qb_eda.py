"""
QB EDA using DuckDB connector
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.utils.duckdb_connector import DuckDBConnector

# Setup
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")
FIGS_DIR = Path(__file__).parent.parent.parent / "docs" / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)


def fmt_millions(v: float) -> str:
    """Format as millions."""
    return f"${v / 1_000_000:.2f}M"


print("=" * 60)
print("🏈 QB CONTRACT ANALYSIS")
print("=" * 60)

with DuckDBConnector() as db:
    # Load data
    qb_df = db.query("""
        SELECT player_name, team_signed_with, start_year, years,
               total_value, average_salary, guarantee_at_signing
        FROM main_bronze.contracts
        WHERE position = 'QB' AND total_value IS NOT NULL
        ORDER BY total_value DESC
    """)

    print(f"Loaded {len(qb_df):,} QB contracts")
    print(f"Years: {qb_df['start_year'].min()}-{qb_df['start_year'].max()}")

    # Add guarantee percentage
    qb_df["guarantee_pct"] = (
        qb_df["guarantee_at_signing"] / qb_df["total_value"] * 100
    ).round(1)

    # Basic stats
    print("\n📊 BASIC STATS")
    print("-" * 40)
    print(f"Avg value: {fmt_millions(qb_df['total_value'].mean())}")
    print(f"Median: {fmt_millions(qb_df['total_value'].median())}")
    print(f"Max: {fmt_millions(qb_df['total_value'].max())}")
    print(f"Avg length: {qb_df['years'].mean():.1f} years")
    print(f"Avg guarantee: {qb_df['guarantee_pct'].mean():.1f}%")

    # Top 10
    print("\n🏆 TOP 10")
    print("-" * 60)
    top10 = qb_df.head(10).copy()
    top10["total"] = top10["total_value"].apply(fmt_millions)
    top10["salary"] = top10["average_salary"].apply(fmt_millions)
    print(
        top10[
            [
                "player_name",
                "team_signed_with",
                "start_year",
                "years",
                "total",
                "salary",
            ]
        ].to_string(index=False)
    )

    # Save summary
    summary = {
        "Metric": ["Total", "Avg Value", "Median", "Max", "Avg Length"],
        "Value": [
            len(qb_df),
            fmt_millions(qb_df["total_value"].mean()),
            fmt_millions(qb_df["total_value"].median()),
            fmt_millions(qb_df["total_value"].max()),
            f"{qb_df['years'].mean():.1f} years",
        ],
    }
    pd.DataFrame(summary).to_csv(FIGS_DIR.parent / "qb_summary.csv", index=False)
    print("\n✅ Summary saved")

print("\n" + "=" * 60)
print("✅ Complete")
print("=" * 60)
