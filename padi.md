
# Adjusted Efficiency Metric (for wrs for example)

**Mutual-Opponent Adjusted EPA per Target (or YPRR)**  
*Step 1 of the Stat-to-Dollar NFL Wide Receiver Valuation Model*

## Overview

This module produces a **schedule-strength-adjusted efficiency metric** for NFL wide receivers. It solves for each WR’s true talent level relative to the defensive units they actually faced, using a closed system of qualified starters only.

The result is an **adjusted EPA per target** (or Yards per Route Run) that answers:  
> “How would this WR have performed against a league-average defense?”

This metric serves as the **foundation** for all subsequent steps: age-curve snap projections → contract dollar valuation.

## Why Mutual-Opponent Adjustment Is the Best Ranking Method for WRs

Wide receivers **do not face each other head-to-head**. They compete indirectly by facing the same defensive secondaries.  

A WR who posts elite production against top-tier defenses (high negative `def_dev`) deserves a larger upward adjustment than one who posts similar raw numbers against weak secondaries.

This approach:
- Mirrors **Adjusted Plus-Minus (RAPM)** and **Elo-style rating systems** adapted to continuous efficiency outcomes.
- Creates a **closed system** of starters (no arbitrary replacement level).
- Avoids bias from easy/hard schedules.
- Produces stable, mutually-consistent ratings via iterative coordinate descent (alternating least squares).
- Naturally shrinks low-sample WRs toward the mean (Bayesian-style regularization via priors).

This is superior to simple opponent-adjusted averages or raw percentiles for contract valuation because it explicitly models the strength of the defenses faced.

## Input Data Requirements

### `df_raw` expected columns

| Column                | Type    | Description                                      | Required |
|-----------------------|---------|--------------------------------------------------|----------|
| `wr_id`               | str/int | Unique WR identifier (player_id or name+season)  | Yes      |
| `def_id`              | str     | Defensive unit (e.g., "KC_2024", "team_year")    | Yes      |
| `observed`            | float   | EPA per target **or** Yards per Route Run        | Yes      |
| `weight`              | int     | Number of targets (or routes) in the matchup     | Yes      |
| `season` (optional)   | int     | Year for multi-year runs                         | Recommended |
| `game_id` (optional)  | str     | For per-game granularity                         | Optional |

Minimum volume filter applied: ≥50 targets or ≥250 routes per WR (configurable).

## Output DataFrame

Final output per WR (one row per qualified WR):

| Column                     | Type  | Description                                                                 |
|----------------------------|-------|-----------------------------------------------------------------------------|
| `wr_id`                    | str   | WR identifier                                                               |
| `adjusted_epa_per_target`  | float | **Primary metric** = league_avg + wr_dev                                    |
| `wr_dev`                   | float | Solved deviation from average (positive = above expected given opponents)   |
| `raw_epa_per_target`       | float | Unadjusted observed value                                                   |
| `targets`                  | int   | Total targets (sample size)                                                 |
| `league_avg`               | float | League-wide weighted average (stored for reference)                         |
| `percentile`               | float | Percentile rank among qualified WRs (0–100)                                 |
| `num_matchups`             | int   | Number of defensive units faced                                             |






```mermaid


flowchart TD

%% ======================
%% DATA PREP
%% ======================

subgraph DATA["Data Preparation"]
A[Load df_raw<br/>WR–Defense matchups]
B[Filter qualified starters]
C[Compute league average<br/>weighted EPA/target]
D[obs_adj = observed − league_avg]
A --> B --> C --> D
end

%% ======================
%% MATCHUP STRUCTURE
%% ======================

subgraph STRUCTURE["Matchup Structure"]
E[Build matchup dictionaries]
F[wr_matchups]
G[def_matchups]
E --> F
E --> G
end

%% ======================
%% INITIALIZATION
%% ======================

subgraph INIT["Initialization"]
H[Initialize ratings]
I[wr_dev = 0]
J[def_dev = 0]
K[Set priors + tolerance]
H --> I
H --> J
H --> K
end

%% ======================
%% ITERATIVE SOLVER
%% ======================

subgraph SOLVER["Iterative Coordinate Descent"]
L[Start iteration loop]
M[Update WR deviations]
N[Shrink using WR prior]
O[Update DEF deviations]
P[Shrink using DEF prior]
Q[Center WR ratings<br/>adjust DEF ratings]
R{Converged?}

L --> M --> N --> O --> P --> Q --> R
R -- No --> L
end

%% ======================
%% OUTPUT
%% ======================

subgraph OUTPUT["Model Output"]
S[Final WR + DEF ratings]
T[Prediction:<br/>league_avg + WR − DEF]
U[WR Adjusted Metric:<br/>league_avg + WR_dev]
S --> T
S --> U
end

%% FLOW CONNECTIONS
D --> E
F --> H
G --> H
K --> L
R -- Yes --> S

%% Styling
style DATA fill:#eef7ff,stroke:#4a90e2
style STRUCTURE fill:#f4faff,stroke:#6aa9ff
style INIT fill:#eefaf0,stroke:#2e8b57
style SOLVER fill:#fff8e6,stroke:#d4a017
style OUTPUT fill:#f3f0ff,stroke:#7a5cff


```
