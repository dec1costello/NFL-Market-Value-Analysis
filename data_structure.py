import pandas as pd
from collections import defaultdict
# Assume df_raw columns: wr_id (str or int), def_id (e.g., 'team_2024'), observed (epa_per_targ), weight (targets), optionally game_id if per-game

df = df_raw[df_raw['weight'] >= min_per_game].copy() # or whatever].copy()
league_avg = (df['observed'] * df['weight']).sum() / df['weight'].sum()
df['obs_adj'] = df['observed'] - league_avg

# Group for fast lookups
wr_matchups = defaultdict(list)  # wr_id -> list of {'obs_adj': , 'w': , 'opp': def_id}
def_matchups = defaultdict(list)  # def_id -> list of {'obs_adj': , 'w': , 'opp': wr_id}

for _, row in df.iterrows():
    d = {'obs_adj': row['obs_adj'], 'w': row['weight'], 'opp': row['def_id']}
    wr_matchups[row['wr_id']].append(d)
    def_matchups[row['def_id']].append({'obs_adj': row['obs_adj'], 'w': row['weight'], 'opp': row['wr_id']})

wrs = list(wr_matchups.keys())
defs = list(def_matchups.keys())
