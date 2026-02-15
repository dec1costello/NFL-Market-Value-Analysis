"""
QB EDA using DuckDB connector - analyzes quarterback contracts from bronze layer
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# This import now works because of the editable install
from src.utils.duckdb_connector import DuckDBConnector

# Set style for better visuals
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Create figures directory
FIGS_DIR = Path(__file__).parent.parent.parent / "docs" / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)


def print_section_header(title: str, char: str = "=", width: int = 60):
    """Print a formatted section header."""
    print("\n" + char * width)
    print(f"{title:^{width}}")
    print(char * width)


def format_currency_millions(value: float) -> str:
    """Format a number as millions with $ sign."""
    return f"${value/1_000_000:.2f}M"


print_section_header("🏈 QB CONTRACT ANALYSIS")

with DuckDBConnector() as db:
    # Database connection test
    print_section_header("📊 Database Connection Test", "-")
    tables = db.get_table_info()
    print(f"Found {len(tables)} tables in database")

    # Load QB data
    print_section_header("📊 Loading QB Contracts from Bronze Layer", "-")

    qb_df = db.query("""
        SELECT
            rank,
            player_name,
            team_signed_with,
            age_at_signing,
            start_year,
            end_year,
            years,
            total_value,
            average_salary,
            avg_percent_of_cap,
            signing_bonus,
            guarantee_at_signing,
            practical_guarantee,
            two_year_cash_total,
            three_year_cash_total
        FROM main_bronze.contracts
        WHERE position = 'QB'
            AND player_name IS NOT NULL
            AND total_value IS NOT NULL
        ORDER BY total_value DESC
    """)

    print(f"Loaded {len(qb_df):,} QB contracts")
    print(f"Date range: {qb_df['start_year'].min()} - {qb_df['start_year'].max()}")

    # Calculate derived metrics
    qb_df["guarantee_pct"] = (
        qb_df["guarantee_at_signing"] / qb_df["total_value"] * 100
    ).round(1)

    # 1. Basic Statistics
    print_section_header("📊 BASIC STATISTICS", "-")
    stats = {
        "Total QB Contracts": f"{len(qb_df):,}",
        "Average Contract Value": format_currency_millions(qb_df["total_value"].mean()),
        "Median Contract Value": format_currency_millions(
            qb_df["total_value"].median()
        ),
        "Max Contract Value": format_currency_millions(qb_df["total_value"].max()),
        "Min Contract Value": format_currency_millions(qb_df["total_value"].min()),
        "Average Contract Length": f"{qb_df['years'].mean():.1f} years",
        "Average Guarantee %": f"{qb_df['guarantee_pct'].mean():.1f}%",
    }

    for key, value in stats.items():
        print(f"{key:<25}: {value}")

    # 2. Top 10 QB Contracts
    print_section_header("🏆 TOP 10 QB CONTRACTS BY TOTAL VALUE", "-")

    top_10_cols = [
        "player_name",
        "team_signed_with",
        "start_year",
        "years",
        "total_value",
        "average_salary",
    ]
    top_10 = qb_df[top_10_cols].head(10).copy()

    # Format for display
    display_df = top_10.copy()
    display_df["total_value"] = display_df["total_value"].apply(
        lambda x: f"${x/1_000_000:.2f}M"
    )
    display_df["average_salary"] = display_df["average_salary"].apply(
        lambda x: f"${x/1_000_000:.2f}M"
    )

    print(display_df.to_string(index=False))

    # 3. Visualizations
    print_section_header("📈 Generating Visualizations", "-")

    # Figure 1: QB Contract Values Over Time
    plt.figure(figsize=(12, 6))

    yearly_avg = (
        qb_df.groupby("start_year")["total_value"]
        .agg(["mean", "max", "count"])
        .reset_index()
    )

    for col in ["mean", "max"]:
        yearly_avg[col] = yearly_avg[col] / 1_000_000

    plt.plot(
        yearly_avg["start_year"],
        yearly_avg["mean"],
        marker="o",
        label="Average",
        linewidth=2,
    )
    plt.plot(
        yearly_avg["start_year"],
        yearly_avg["max"],
        marker="s",
        label="Maximum",
        linewidth=2,
    )

    plt.title("QB Contract Values Over Time", fontsize=16, fontweight="bold")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Contract Value ($ Millions)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Add annotation for number of contracts
    for _, row in yearly_avg.iterrows():
        plt.annotate(
            f"n={int(row['count'])}",
            (row["start_year"], row["mean"]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(FIGS_DIR / "qb_values_over_time.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 2: Contract Length Distribution
    plt.figure(figsize=(10, 6))

    length_dist = qb_df["years"].value_counts().sort_index()
    bars = plt.bar(length_dist.index, length_dist.values, alpha=0.7, color="steelblue")

    plt.title("QB Contract Length Distribution", fontsize=16, fontweight="bold")
    plt.xlabel("Contract Length (Years)", fontsize=12)
    plt.ylabel("Number of Contracts", fontsize=12)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
        )

    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "qb_length_distribution.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 3: Guaranteed Money Analysis
    plt.figure(figsize=(12, 6))

    bins = [0, 30, 50, 70, 100]
    labels = ["<30%", "30-50%", "50-70%", ">70%"]
    qb_df["guarantee_tier"] = pd.cut(qb_df["guarantee_pct"], bins=bins, labels=labels)

    guarantee_dist = qb_df["guarantee_tier"].value_counts().sort_index()

    plt.pie(
        guarantee_dist.values,
        labels=guarantee_dist.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("husl", 4),
    )
    plt.title("QB Contracts by Guarantee Percentage", fontsize=16, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "qb_guarantee_pie.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 4: Top Teams by QB Spending
    plt.figure(figsize=(12, 8))

    team_spending = (
        qb_df.groupby("team_signed_with")
        .agg(
            total_spent=("total_value", "sum"), contract_count=("player_name", "count")
        )
        .reset_index()
    )

    team_spending["total_spent_millions"] = team_spending["total_spent"] / 1_000_000
    team_spending = team_spending.nlargest(15, "total_spent_millions")

    plt.barh(
        team_spending["team_signed_with"],
        team_spending["total_spent_millions"],
        alpha=0.7,
    )
    plt.title(
        "Top 15 Teams by Total QB Contract Spending", fontsize=16, fontweight="bold"
    )
    plt.xlabel("Total Spending ($ Millions)", fontsize=12)
    plt.ylabel("Team", fontsize=12)

    for _, row in team_spending.iterrows():
        plt.text(
            row["total_spent_millions"] + 5,
            row.name,
            f"${row['total_spent_millions']:.0f}M " f"(n={int(row['contract_count'])})",
            va="center",
            fontsize=9,
        )

    plt.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "qb_team_spending.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4. Export summary to CSV
    print_section_header("💾 Saving Summary Data", "-")

    summary_data = {
        "Metric": [
            "Total QB Contracts",
            "Avg Value",
            "Median Value",
            "Max Value",
            "Avg Length",
            "Avg Guarantee %",
            "Most Common Length",
            "Highest Paid QB",
            "Year with Most Contracts",
        ],
        "Value": [
            f"{len(qb_df):,}",
            format_currency_millions(qb_df["total_value"].mean()),
            format_currency_millions(qb_df["total_value"].median()),
            format_currency_millions(qb_df["total_value"].max()),
            f"{qb_df['years'].mean():.1f} years",
            f"{qb_df['guarantee_pct'].mean():.1f}%",
            f"{qb_df['years'].mode()[0]} years",
            qb_df.loc[qb_df["total_value"].idxmax(), "player_name"],
            str(qb_df["start_year"].value_counts().idxmax()),
        ],
    }

    summary = pd.DataFrame(summary_data)
    summary_path = FIGS_DIR.parent / "qb_summary_stats.csv"
    summary.to_csv(summary_path, index=False)
    print(f"✅ Summary saved to {summary_path}")

    # 5. Quick insights
    print_section_header("🔍 KEY INSIGHTS", "-")

    most_common_year = qb_df["start_year"].value_counts().idxmax()
    most_contracts = qb_df["start_year"].value_counts().max()

    # Safely get 2010 and 2023 averages (handle missing years)
    avg_2010 = qb_df[qb_df["start_year"] == 2010]["total_value"].mean()
    avg_2023 = qb_df[qb_df["start_year"] == 2023]["total_value"].mean()

    if not pd.isna(avg_2010) and not pd.isna(avg_2023):
        print(
            f"• QB contracts grew from {format_currency_millions(avg_2010)} "
            f"in 2010 to {format_currency_millions(avg_2023)} in 2023"
        )

    print(
        f"• {most_common_year} saw the most QB contracts " f"signed ({most_contracts})"
    )
    print(f"• {qb_df['years'].mode()[0]}-year contracts " "are most common")
    print(
        f"• Average guarantee is {qb_df['guarantee_pct'].mean():.1f}% " "of total value"
    )

    print(f"\n📁 Visualizations saved to: {FIGS_DIR}")

print_section_header("✅ QB EDA Complete!")
