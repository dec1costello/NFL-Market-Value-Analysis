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

# /*
# Iterative logic (alternating least-squares / coordinate descent, 
# like ALS for matrix factorization or RAPM-style; converges quickly 
# to (regularized) least-squares solution; analogous
# to repeated Elo-style batch updates on all "matches"):
# */
#Initialize:
wr_dev = {wr: 0.0 for wr in wrs}
def_dev = {d: 0.0 for d in defs}
prior_w_wr = 30.0   # equiv. targets; tune 20-50 (higher = more regression to mean; Bayes-like shrinkage)
prior_w_def = 80.0  # defenses have more data; higher = less shrinkage on D ratings; tune 50-150
max_iters = 50
tol = 1e-6

#loop
for it in range(max_iters):
    max_delta = 0.0
    
    # Update WR devs (batch over their matchups)
    for wr in wrs:
        num = 0.0
        den = 0.0
        for m in wr_matchups[wr]:
            num += m['w'] * (m['obs_adj'] - def_dev[m['opp']])
            den += m['w']
        if den > 0:
            new_val = num / (den + prior_w_wr)  # shrinkage to 0
            max_delta = max(max_delta, abs(new_val - wr_dev[wr]))
            wr_dev[wr] = new_val
    
    # Update DEF devs
    for d in defs:
        num = 0.0
        den = 0.0
        for m in def_matchups[d]:
            num += m['w'] * (m['obs_adj'] - wr_dev[m['opp']])
            den += m['w']
        if den > 0:
            new_val = num / (den + prior_w_def)
            max_delta = max(max_delta, abs(new_val - def_dev[d]))
            def_dev[d] = new_val
    
    # Optional but recommended: center WR devs (weighted mean ~0); adjust defs to preserve fit
    total_w_wr = 0.0
    sum_w = 0.0
    for wr in wrs:
        w_total = sum(m['w'] for m in wr_matchups[wr])
        total_w_wr += w_total
        sum_w += wr_dev[wr] * w_total
    mean_wr = sum_w / total_w_wr if total_w_wr > 0 else 0.0
    for wr in wrs:
        wr_dev[wr] -= mean_wr
    for d in defs:
        def_dev[d] += mean_wr
    
    if max_delta < tol:
        break
