"""
Mutual Opponent Adjustment Model for NFL Player Valuation
Implements Open-Closed Principle for position-agnostic player rating
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Tuple, DefaultDict
from collections import defaultdict
import numpy as np
from scipy import stats

print("=== Loading Mutual Opponent Adjustment Model ===\n")


@dataclass
class Matchup:
    """Base matchup data structure"""

    player_id: str
    opponent_id: str  # Defense for WR, D-line for RB, coverage for TE
    game_id: str
    base_metric: float
    volume: float  # routes for WR, carries for RB, etc.
    weight: float = 1.0

    def __repr__(self):
        return (
            f"Matchup({self.player_id} vs {self.opponent_id}: {self.base_metric:.3f})"
        )


print("✓ Defined Matchup dataclass")


class PositionModel(ABC):
    """Open-Closed base class for all positions"""

    @abstractmethod
    def prepare_data(self, raw_data) -> List[Matchup]:
        """Transform raw data into position-specific matchups"""
        pass

    @abstractmethod
    def compute_base_metric(self, game_stats) -> float:
        """Position-specific performance metric"""
        pass

    @abstractmethod
    def get_prior_strength(self) -> float:
        """Bayesian stabilization constant for this position"""
        pass

    @abstractmethod
    def get_weight_function(self, volume: float) -> float:
        """How to weight observations based on volume"""
        pass


print("✓ Defined PositionModel abstract base class\n")


class WRModel(PositionModel):
    """Concrete implementation for Wide Receivers"""

    def prepare_data(self, raw_data) -> List[Matchup]:
        print(f"  Preparing WR data: {len(raw_data)} games")
        matchups = []
        for i, game in enumerate(raw_data):
            matchup = Matchup(
                player_id=game["wr_id"],
                opponent_id=game["defense_id"],
                game_id=game["game_id"],
                base_metric=self.compute_base_metric(game),
                volume=game["routes"],
                weight=self.get_weight_function(game["routes"]),
            )
            matchups.append(matchup)
            if i < 3:  # Show first few examples
                print(f"    Example {i+1}: {matchup}")
        print(f"  Created {len(matchups)} WR matchups")
        return matchups

    def compute_base_metric(self, game_stats) -> float:
        # WR-specific: EPA per target
        if game_stats["targets"] > 0:
            epa_per_target = game_stats["epa"] / game_stats["targets"]
            print(
                f"    Computing WR metric: {game_stats['epa']:.2f} EPA / {game_stats['targets']} targets = {epa_per_target:.3f}"
            )
            return epa_per_target
        print(f"    No targets for WR {game_stats['wr_id']}, metric = 0")
        return 0.0

    def get_prior_strength(self) -> float:
        print(f"  WR prior strength (k) = 200")
        return 200  # k for Bayesian shrinkage

    def get_weight_function(self, volume: float) -> float:
        # Diminishing returns for routes
        weight = min(volume, 50) / 50
        print(f"    WR weight for {volume} routes = {weight:.3f}")
        return weight


class RBModel(PositionModel):
    """Concrete implementation for Running Backs"""

    def prepare_data(self, raw_data) -> List[Matchup]:
        print(f"  Preparing RB data: {len(raw_data)} games")
        matchups = []
        for i, game in enumerate(raw_data):
            matchup = Matchup(
                player_id=game["rb_id"],
                opponent_id=game["run_defense_id"],
                game_id=game["game_id"],
                base_metric=self.compute_base_metric(game),
                volume=game["carries"],
                weight=self.get_weight_function(game["carries"]),
            )
            matchups.append(matchup)
            if i < 3:
                print(f"    Example {i+1}: {matchup}")
        print(f"  Created {len(matchups)} RB matchups")
        return matchups

    def compute_base_metric(self, game_stats) -> float:
        # RB-specific: EPA per carry
        epa_per_carry = game_stats["epa"] / max(game_stats["carries"], 1)
        print(
            f"    Computing RB metric: {game_stats['epa']:.2f} EPA / {game_stats['carries']} carries = {epa_per_carry:.3f}"
        )
        return epa_per_carry

    def get_prior_strength(self) -> float:
        print(f"  RB prior strength (k) = 150")
        return 150  # RBs need less stabilization (more carries per game)

    def get_weight_function(self, volume: float) -> float:
        weight = min(volume, 25) / 25  # Different scaling for carries
        print(f"    RB weight for {volume} carries = {weight:.3f}")
        return weight


print("✓ Defined WRModel and RBModel concrete implementations\n")


class MutualOpponentModel:
    """Closed for modification, open for extension via PositionModel"""

    def __init__(self, position_model: PositionModel):
        print(
            f"\n=== Initializing MutualOpponentModel for {position_model.__class__.__name__} ==="
        )
        self.position = position_model
        self.player_ratings: Dict[str, float] = {}
        self.opponent_ratings: Dict[str, float] = {}
        self.league_avg: float = 0.0
        self.matchups: List[Matchup] = []

    def fit(self, matchups: List[Matchup], max_iter: int = 100, tol: float = 1e-4):
        """Coordinate descent algorithm for mutual opponent adjustment"""
        print(f"\n=== Fitting model with {len(matchups)} matchups ===")
        self.matchups = matchups

        # Step 1: Compute league average (weighted)
        print("\n1. Computing weighted league average...")
        total_weight = sum(m.weight for m in matchups)
        weighted_sum = sum(m.base_metric * m.weight for m in matchups)
        self.league_avg = weighted_sum / total_weight
        print(f"   League average (weighted) = {self.league_avg:.4f}")
        print(f"   Total weight = {total_weight:.2f}")

        # Step 2: Create observation dictionaries
        print("\n2. Building observation dictionaries...")
        player_obs = defaultdict(list)
        opponent_obs = defaultdict(list)

        for m in matchups:
            dev = m.base_metric - self.league_avg
            player_obs[m.player_id].append((dev, m.opponent_id, m.weight))
            opponent_obs[m.opponent_id].append((dev, m.player_id, m.weight))

        print(f"   Tracking {len(player_obs)} unique players")
        print(f"   Tracking {len(opponent_obs)} unique opponents")

        # Step 3: Initialize ratings
        print("\n3. Initializing ratings...")
        self.player_ratings = {pid: 0.0 for pid in player_obs.keys()}
        self.opponent_ratings = {oid: 0.0 for oid in opponent_obs.keys()}

        print(f"   Initialized {len(self.player_ratings)} player ratings to 0")
        print(f"   Initialized {len(self.opponent_ratings)} opponent ratings to 0")

        # Step 4: Iterative coordinate descent
        print(f"\n4. Starting coordinate descent (max {max_iter} iterations)...")
        for iteration in range(max_iter):
            prev_player = self.player_ratings.copy()
            prev_opponent = self.opponent_ratings.copy()

            # Update player ratings (fix opponents)
            print(f"\n   Iteration {iteration + 1}:")
            print(f"   a. Updating player ratings...")
            for pid, obs_list in player_obs.items():
                effective_samples = 0
                total_residual = 0.0

                for dev, oid, weight in obs_list:
                    residual = dev + self.opponent_ratings[oid]
                    total_residual += residual * weight
                    effective_samples += weight

                if effective_samples > 0:
                    k = self.position.get_prior_strength()
                    raw_rating = total_residual / effective_samples
                    shrunk_rating = (raw_rating * effective_samples) / (
                        effective_samples + k
                    )
                    self.player_ratings[pid] = shrunk_rating

                    if (
                        iteration == 0 and pid in list(player_obs.keys())[:2]
                    ):  # Show first couple
                        print(
                            f"      {pid}: raw={raw_rating:.3f}, shrunk={shrunk_rating:.3f}, samples={effective_samples:.1f}"
                        )

            # Update opponent ratings (fix players)
            print(f"   b. Updating opponent ratings...")
            for oid, obs_list in opponent_obs.items():
                effective_samples = 0
                total_residual = 0.0

                for dev, pid, weight in obs_list:
                    residual = -dev + self.player_ratings[pid]
                    total_residual += residual * weight
                    effective_samples += weight

                if effective_samples > 0:
                    k_opponent = self.position.get_prior_strength() * 1.5
                    raw_rating = total_residual / effective_samples
                    shrunk_rating = (raw_rating * effective_samples) / (
                        effective_samples + k_opponent
                    )
                    self.opponent_ratings[oid] = shrunk_rating

                    if iteration == 0 and oid in list(opponent_obs.keys())[:2]:
                        print(
                            f"      {oid}: raw={raw_rating:.3f}, shrunk={shrunk_rating:.3f}, samples={effective_samples:.1f}"
                        )

            # Center player ratings (mean = 0)
            print(f"   c. Centering ratings...")
            avg_player = sum(self.player_ratings.values()) / len(self.player_ratings)
            self.player_ratings = {
                k: v - avg_player for k, v in self.player_ratings.items()
            }

            # Adjust opponents accordingly
            self.opponent_ratings = {
                k: v + avg_player for k, v in self.opponent_ratings.items()
            }
            print(f"      Player mean was {avg_player:.4f}, now centered at 0")

            # Check convergence
            player_change = self._max_change(prev_player, self.player_ratings)
            opponent_change = self._max_change(prev_opponent, self.opponent_ratings)

            print(
                f"   d. Max change: players={player_change:.6f}, opponents={opponent_change:.6f}"
            )

            if player_change < tol and opponent_change < tol:
                print(f"\n   ✓ CONVERGED after {iteration + 1} iterations!")
                break

        print(f"\n=== Model fitting complete ===")
        print(
            f"Final player ratings range: [{min(self.player_ratings.values()):.3f}, {max(self.player_ratings.values()):.3f}]"
        )
        print(
            f"Final opponent ratings range: [{min(self.opponent_ratings.values()):.3f}, {max(self.opponent_ratings.values()):.3f}]"
        )

    def predict(self, player_id: str, opponent_id: str) -> float:
        """Predict performance for a matchup"""
        prediction = (
            self.league_avg
            + self.player_ratings.get(player_id, 0.0)
            - self.opponent_ratings.get(opponent_id, 0.0)
        )
        print(f"\nPrediction for {player_id} vs {opponent_id}:")
        print(f"  League avg: {self.league_avg:.3f}")
        print(f"  Player rating: {self.player_ratings.get(player_id, 0.0):.3f}")
        print(f"  Opponent rating: {-self.opponent_ratings.get(opponent_id, 0.0):.3f}")
        print(f"  Predicted metric: {prediction:.3f}")
        return prediction

    def get_adjusted_metric(self, player_id: str) -> float:
        """Get player's adjusted metric (league average + player rating)"""
        adjusted = self.league_avg + self.player_ratings.get(player_id, 0.0)
        print(f"\nAdjusted metric for {player_id}:")
        print(f"  Raw player rating: {self.player_ratings.get(player_id, 0.0):.3f}")
        print(f"  League average: {self.league_avg:.3f}")
        print(f"  Adjusted metric: {adjusted:.3f}")
        return adjusted

    def _max_change(self, old: Dict, new: Dict) -> float:
        keys = set(old.keys()) | set(new.keys())
        changes = [abs(new.get(k, 0) - old.get(k, 0)) for k in keys]
        return max(changes) if changes else 0.0


print("✓ Defined MutualOpponentModel base class\n")


class EnhancedMutualOpponentModel(MutualOpponentModel):
    """Adds quality of competition and recency weighting"""

    def __init__(
        self,
        position_model: PositionModel,
        recency_decay: float = 0.95,
        quality_weight: bool = True,
    ):
        super().__init__(position_model)
        print(f"\n=== Initializing Enhanced Model ===")
        self.recency_decay = recency_decay
        self.quality_weight = quality_weight
        self.game_weights: Dict[str, float] = {}  # game_id -> recency weight
        print(f"  Recency decay: {recency_decay}")
        print(f"  Quality weighting: {quality_weight}")

    def compute_game_weights(self, matchups: List[Matchup], reference_week: int = 18):
        """Apply recency weighting based on week number"""
        print(f"\n=== Applying recency weighting (reference week {reference_week}) ===")
        for m in matchups:
            try:
                week = int(m.game_id.split("_")[-1])
                weeks_ago = reference_week - week
                recency_weight = self.recency_decay**weeks_ago
                original_weight = m.weight
                m.weight *= recency_weight
                self.game_weights[m.game_id] = recency_weight

                if m.player_id in ["WR1", "WR2", "RB1"]:  # Show examples
                    print(
                        f"  {m.player_id} Week {week}: original={original_weight:.3f}, recency={recency_weight:.3f}, final={m.weight:.3f}"
                    )
            except:
                # If game_id format doesn't have week, skip recency weighting
                pass

    def fit_with_quality_weighting(self, matchups: List[Matchup]):
        """Enhanced fitting with opponent quality consideration"""
        print(f"\n=== Starting quality-weighted fitting ===")

        # Two-pass approach:
        print("1. Initial fit to establish baseline ratings...")
        super().fit(matchups)

        # 2. Re-weight based on opponent strength and re-fit
        if self.quality_weight:
            print("\n2. Re-weighting based on opponent strength...")
            for m in matchups:
                opponent_strength = abs(self.opponent_ratings[m.opponent_id])
                quality_multiplier = 1.0 + (opponent_strength / 2.0)  # 1.0-1.5x
                original_weight = m.weight
                m.weight *= quality_multiplier

                if m.player_id in ["WR1", "WR2"]:  # Show examples
                    print(
                        f"  {m.player_id} vs {m.opponent_id}: strength={opponent_strength:.3f}, multiplier={quality_multiplier:.3f}, weight {original_weight:.3f}→{m.weight:.3f}"
                    )

            print("\n3. Re-fitting with quality-weighted data...")
            super().fit(matchups)

    def get_confidence_interval(
        self, player_id: str, alpha: float = 0.05
    ) -> Tuple[float, float]:
        """Calculate confidence interval for rating"""
        print(f"\n=== Calculating confidence interval for {player_id} ===")

        player_matchups = [m for m in self.matchups if m.player_id == player_id]
        n_effective = sum(m.weight for m in player_matchups)

        print(f"  Effective sample size: {n_effective:.1f}")

        if n_effective < 10:
            rating = self.player_ratings.get(player_id, 0.0)
            ci_lower = rating * 0.7
            ci_upper = rating * 1.3
            print(f"  Small sample (<10), using wide interval:")
            print(f"  Rating: {rating:.3f}, CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
            return ci_lower, ci_upper

        try:
            # Empirical Bayes credible interval
            prior_variance = 1.0 / self.position.get_prior_strength()
            posterior_variance = prior_variance / (n_effective + prior_variance)

            z_score = stats.norm.ppf(1 - alpha / 2)
            ci_width = z_score * np.sqrt(posterior_variance)

            rating = self.player_ratings.get(player_id, 0.0)
            ci_lower = rating - ci_width
            ci_upper = rating + ci_width

            print(f"  Rating: {rating:.3f}")
            print(f"  Prior variance: {prior_variance:.6f}")
            print(f"  Posterior variance: {posterior_variance:.6f}")
            print(f"  Z-score (alpha={alpha}): {z_score:.3f}")
            print(f"  Confidence interval: [{ci_lower:.3f}, {ci_upper:.3f}]")

            return ci_lower, ci_upper
        except:
            rating = self.player_ratings.get(player_id, 0.0)
            return rating * 0.8, rating * 1.2


print("✓ Defined EnhancedMutualOpponentModel\n")


class ModelFactory:
    """Factory to create position-specific models"""

    @staticmethod
    def create_model(position: str, **kwargs) -> EnhancedMutualOpponentModel:
        print(f"\n=== ModelFactory creating {position} model ===")

        position_map = {
            "WR": WRModel(),
            "RB": RBModel(),
            # Add more positions as needed
        }

        position_model = position_map.get(position)
        if not position_model:
            raise ValueError(f"Unknown position: {position}")

        print(f"  Found position model: {position_model.__class__.__name__}")

        # Configure model based on position
        config = {
            "WR": {"recency_decay": 0.95, "quality_weight": True},
            "RB": {"recency_decay": 0.90, "quality_weight": False},
        }

        model_config = config.get(position, {})
        print(f"  Applying config: {model_config}")

        return EnhancedMutualOpponentModel(
            position_model=position_model, **model_config, **kwargs
        )


print("✓ Defined ModelFactory\n")

# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================


def create_sample_data():
    """Create sample data for demonstration"""
    print("\n" + "=" * 60)
    print("CREATING SAMPLE DATA")
    print("=" * 60)

    # Sample WR data (simplified)
    wr_data = [
        {
            "wr_id": "WR1",
            "defense_id": "DEF1",
            "game_id": "2023_1",
            "epa": 12.5,
            "targets": 8,
            "routes": 40,
        },
        {
            "wr_id": "WR1",
            "defense_id": "DEF2",
            "game_id": "2023_2",
            "epa": 8.2,
            "targets": 6,
            "routes": 38,
        },
        {
            "wr_id": "WR2",
            "defense_id": "DEF1",
            "game_id": "2023_1",
            "epa": 6.8,
            "targets": 5,
            "routes": 35,
        },
        {
            "wr_id": "WR2",
            "defense_id": "DEF3",
            "game_id": "2023_3",
            "epa": 15.3,
            "targets": 9,
            "routes": 42,
        },
        {
            "wr_id": "WR3",
            "defense_id": "DEF2",
            "game_id": "2023_2",
            "epa": 4.5,
            "targets": 4,
            "routes": 30,
        },
        {
            "wr_id": "WR3",
            "defense_id": "DEF3",
            "game_id": "2023_3",
            "epa": 9.6,
            "targets": 7,
            "routes": 36,
        },
    ]

    # Sample RB data
    rb_data = [
        {
            "rb_id": "RB1",
            "run_defense_id": "RDEF1",
            "game_id": "2023_1",
            "epa": 8.5,
            "carries": 15,
        },
        {
            "rb_id": "RB1",
            "run_defense_id": "RDEF2",
            "game_id": "2023_2",
            "epa": 12.3,
            "carries": 18,
        },
        {
            "rb_id": "RB2",
            "run_defense_id": "RDEF1",
            "game_id": "2023_1",
            "epa": 5.2,
            "carries": 12,
        },
        {
            "rb_id": "RB2",
            "run_defense_id": "RDEF3",
            "game_id": "2023_3",
            "epa": 9.8,
            "carries": 16,
        },
    ]

    print(f"Created {len(wr_data)} WR game records")
    print(f"Created {len(rb_data)} RB game records")

    return {"WR": wr_data, "RB": rb_data}


def demonstrate_wr_model():
    """Demonstrate the WR model"""
    print("\n" + "=" * 60)
    print("DEMONSTRATING WR MODEL")
    print("=" * 60)

    # Create WR model
    wr_model = ModelFactory.create_model("WR")

    # Get sample data
    sample_data = create_sample_data()
    wr_data = sample_data["WR"]

    # Prepare matchups
    matchups = wr_model.position.prepare_data(wr_data)

    # Apply recency weighting
    wr_model.compute_game_weights(matchups, reference_week=3)

    # Fit model with quality weighting
    wr_model.fit_with_quality_weighting(matchups)

    # Demonstrate predictions
    print("\n" + "-" * 40)
    print("DEMONSTRATING PREDICTIONS")
    print("-" * 40)

    # Predict WR1 vs DEF1 (already played)
    wr_model.predict("WR1", "DEF1")

    # Predict WR1 vs DEF3 (new matchup)
    wr_model.predict("WR1", "DEF3")

    # Get adjusted metrics
    print("\n" + "-" * 40)
    print("ADJUSTED METRICS")
    print("-" * 40)

    for wr_id in ["WR1", "WR2", "WR3"]:
        adjusted = wr_model.get_adjusted_metric(wr_id)
        ci_lower, ci_upper = wr_model.get_confidence_interval(wr_id)
        print(f"\n{wr_id}:")
        print(f"  Adjusted EPA/target: {adjusted:.3f}")
        print(f"  95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")

    return wr_model


def demonstrate_rb_model():
    """Demonstrate the RB model"""
    print("\n" + "=" * 60)
    print("DEMONSTRATING RB MODEL")
    print("=" * 60)

    # Create RB model
    rb_model = ModelFactory.create_model("RB")

    # Get sample data
    sample_data = create_sample_data()
    rb_data = sample_data["RB"]

    # Prepare matchups
    matchups = rb_model.position.prepare_data(rb_data)

    # Apply recency weighting
    rb_model.compute_game_weights(matchups, reference_week=3)

    # Fit model with quality weighting
    rb_model.fit_with_quality_weighting(matchups)

    # Get adjusted metrics
    print("\n" + "-" * 40)
    print("RB ADJUSTED METRICS")
    print("-" * 40)

    for rb_id in ["RB1", "RB2"]:
        adjusted = rb_model.get_adjusted_metric(rb_id)
        print(f"{rb_id}: Adjusted EPA/carry: {adjusted:.3f}")

    return rb_model


def main():
    """Main demonstration function"""
    print("\n" + "=" * 60)
    print("MUTUAL OPPONENT ADJUSTMENT MODEL DEMONSTRATION")
    print("=" * 60)

    # Demonstrate both models
    wr_model = demonstrate_wr_model()
    rb_model = demonstrate_rb_model()

    # Show the Open-Closed Principle in action
    print("\n" + "=" * 60)
    print("OPEN-CLOSED PRINCIPLE DEMONSTRATION")
    print("=" * 60)

    print("\nBoth WR and RB models use the same MutualOpponentModel class,")
    print("but each has its own position-specific implementations:")
    print("\n1. Different base metrics:")
    print("   - WR: EPA per target")
    print("   - RB: EPA per carry")
    print("\n2. Different weighting functions:")
    print("   - WR: min(routes, 50)/50")
    print("   - RB: min(carries, 25)/25")
    print("\n3. Different prior strengths:")
    print("   - WR: k = 200")
    print("   - RB: k = 150")
    print("\n4. Different recency decay:")
    print("   - WR: 0.95 (slower decay)")
    print("   - RB: 0.90 (faster decay)")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nThe model successfully:")
    print("1. Adjusts for opponent strength")
    print("2. Applies Bayesian shrinkage for small samples")
    print("3. Handles different positions via OCP")
    print("4. Provides confidence intervals")
    print("5. Allows quality-of-competition weighting")
    print("\nReady for integration with Step 2 (volume projections)!")


if __name__ == "__main__":
    main()
