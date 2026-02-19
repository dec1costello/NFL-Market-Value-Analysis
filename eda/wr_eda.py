"""
WR EDA - Query and analyze wide receiver data from bronze layer
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import from src (after path is set)
from src.utils.duckdb_connector import DuckDBConnector  # noqa: E402

# Setup
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")
FIGS_DIR = project_root / "docs" / "figures" / "wr"
FIGS_DIR.mkdir(parents=True, exist_ok=True)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def main():
    """Main EDA function."""
    print_header("🏈 WIDE RECEIVER DATA EXPLORATION")

    with DuckDBConnector() as db:
        # 1. Check what tables we have
        print("\n📊 Available tables:")
        tables = db.get_table_info()
        print(
            tables[tables["table_name"].str.contains("wr", case=False)].to_string(
                index=False
            )
        )

        # 2. Seasonal data overview
        print_header("📅 SEASONAL WR DATA (2015-2025)")

        seasonal = db.query("""
            SELECT
                season_year,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(*) as total_records,
                AVG(receiving_yards) as avg_rec_yards,
                AVG(receptions) as avg_receptions,
                AVG(targets) as avg_targets,
                AVG(receiving_td) as avg_td
            FROM main_bronze.wr_season
            GROUP BY season_year
            ORDER BY season_year
        """)

        print("\nSeasonal summary by year:")
        print(seasonal.to_string(index=False))

        # Plot seasonal trends
        plt.figure(figsize=(12, 6))
        plt.plot(
            seasonal["season_year"],
            seasonal["avg_rec_yards"],
            marker="o",
            label="Avg Receiving Yards",
        )
        plt.plot(
            seasonal["season_year"],
            seasonal["avg_receptions"],
            marker="s",
            label="Avg Receptions",
        )
        plt.title("WR Seasonal Averages Over Time", fontsize=16, fontweight="bold")
        plt.xlabel("Year")
        plt.ylabel("Average")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(FIGS_DIR / "wr_seasonal_trends.png", dpi=300, bbox_inches="tight")
        plt.close()

        # 3. Top WR seasons
        print_header("🏆 TOP 10 WR SEASONS (by receiving yards)")

        top_seasons = db.query("""
            SELECT
                player_name,
                team,
                season_year,
                receiving_yards,
                receptions,
                receiving_td,
                targets
            FROM main_bronze.wr_season
            ORDER BY receiving_yards DESC
            LIMIT 10
        """)

        print(top_seasons.to_string(index=False))

        # 4. Game-level data (if available)
        try:
            print_header("🎮 GAME-LEVEL WR DATA (2021-2025)")

            # Check if game data exists
            game_check = db.query("SELECT COUNT(*) as cnt FROM main_bronze.wr_game")
            if game_check.iloc[0, 0] > 0:
                game_summary = db.query("""
                    SELECT
                        season_year,
                        COUNT(DISTINCT week_number) as weeks,
                        COUNT(DISTINCT player_id) as players,
                        AVG(receiving_yards) as avg_yards_per_game,
                        AVG(receptions) as avg_rec_per_game,
                        MAX(receiving_yards) as max_yards_game
                    FROM main_bronze.wr_game
                    GROUP BY season_year
                    ORDER BY season_year
                """)

                print("\nGame data summary by year:")
                print(game_summary.to_string(index=False))

                # Best single games
                top_games = db.query("""
                    SELECT
                        player_name,
                        team,
                        opponent,
                        season_year,
                        week_number,
                        receiving_yards,
                        receptions,
                        receiving_td
                    FROM main_bronze.wr_game
                    ORDER BY receiving_yards DESC
                    LIMIT 10
                """)

                print("\n🏆 TOP 10 WR GAMES (by receiving yards):")
                print(top_games.to_string(index=False))

            else:
                print("\nNo game-level data found yet.")

        except Exception as e:
            print(f"\nGame data not available: {e}")

        # 5. Compare 2023 players
        print_header("🔍 2023 WR LEADERS")

        # First, check what years we actually have
        years_available = db.query("""
            SELECT DISTINCT season_year
            FROM main_bronze.wr_season
            WHERE season_year IS NOT NULL AND season_year != ''
            ORDER BY season_year
        """)
        print(f"\nYears available in data: {years_available['season_year'].tolist()}")

        # Now get 2023 data with proper filtering
        wr_2023 = db.query("""
            SELECT
                player_name,
                team,
                receiving_yards,
                receptions,
                receiving_td,
                targets
            FROM main_bronze.wr_season
            WHERE season_year = '2023'  -- Use string comparison
                AND receiving_yards IS NOT NULL
            ORDER BY receiving_yards DESC
            LIMIT 15
        """)

        if len(wr_2023) > 0:
            print("\nTop 15 WRs of 2023:")
            print(wr_2023.to_string(index=False))
        else:
            print("\nNo 2023 data found. Trying alternative year format...")

            # Try numeric conversion if string doesn't work
            wr_2023 = db.query("""
                SELECT
                    player_name,
                    team,
                    receiving_yards,
                    receptions,
                    receiving_td,
                    targets
                FROM main_bronze.wr_season
                WHERE TRY_CAST(season_year AS INTEGER) = 2023
                    AND receiving_yards IS NOT NULL
                ORDER BY receiving_yards DESC
                LIMIT 15
            """)
            print(wr_2023.to_string(index=False))

        # 6. Create a bar chart of top 10 WRs all-time
        plt.figure(figsize=(14, 8))

        top_alltime = db.query("""
            SELECT
                player_name,
                SUM(receiving_yards) as career_yards,
                COUNT(DISTINCT season_year) as seasons,
                AVG(receiving_yards) as avg_per_season
            FROM main_bronze.wr_season
            GROUP BY player_name
            HAVING seasons >= 3
            ORDER BY career_yards DESC
            LIMIT 15
        """)

        plt.barh(top_alltime["player_name"], top_alltime["career_yards"] / 1000)
        plt.xlabel("Career Receiving Yards (Thousands)")
        plt.title(
            "Top 15 WRs by Career Receiving Yards", fontsize=16, fontweight="bold"
        )

        # Add value labels
        for i, (_, row) in enumerate(top_alltime.iterrows()):
            plt.text(
                row["career_yards"] / 1000 + 50,
                i,
                f"{row['career_yards']:,.0f} yds ({row['seasons']} seasons)",
                va="center",
            )

        plt.tight_layout()
        plt.savefig(FIGS_DIR / "top_wr_career_yards.png", dpi=300, bbox_inches="tight")
        plt.close()

        # 7. Save summary stats
        print_header("💾 SAVING SUMMARY")

        summary = {
            "Metric": [
                "Total WR seasons",
                "Unique WRs",
                "Years covered",
                "Avg yards per season",
                "Avg TDs per season",
                "Most yards in a season",
                "Most TDs in a season",
            ],
            "Value": [
                str(db.query("SELECT COUNT(*) FROM main_bronze.wr_season").iloc[0, 0]),
                str(
                    db.query(
                        "SELECT COUNT(DISTINCT player_id) FROM main_bronze.wr_season"
                    ).iloc[0, 0]
                ),
                f"{db.query('SELECT MIN(season_year) FROM main_bronze.wr_season').iloc[0, 0]}-{db.query('SELECT MAX(season_year) FROM main_bronze.wr_season').iloc[0, 0]}",
                f"{db.query('SELECT AVG(receiving_yards) FROM main_bronze.wr_season').iloc[0, 0]:.0f}",
                f"{db.query('SELECT AVG(receiving_td) FROM main_bronze.wr_season').iloc[0, 0]:.1f}",
                f"{db.query('SELECT MAX(receiving_yards) FROM main_bronze.wr_season').iloc[0, 0]:,.0f}",
                f"{db.query('SELECT MAX(receiving_td) FROM main_bronze.wr_season').iloc[0, 0]}",
            ],
        }

        pd.DataFrame(summary).to_csv(
            FIGS_DIR.parent / "wr_summary_stats.csv", index=False
        )
        print(f"\n✅ Summary saved to {FIGS_DIR.parent}/wr_summary_stats.csv")
        print(f"📁 Visualizations saved to: {FIGS_DIR}")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
    print("✅ WR EDA Complete!")
    print("=" * 60)
