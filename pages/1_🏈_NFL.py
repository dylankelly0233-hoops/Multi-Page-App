import streamlit as st
import nflreadpy as nfl
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="AlphaPoint NFL", layout="wide", page_icon="🏈")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stDataFrame { border: 1px solid #303030; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏈 AlphaPoint: NFL Live Betting Board")
st.markdown("""
Apply custom QB changes or update Vegas lines. Projections update instantly.
""")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("👤 User Account")
    user_status = st.radio("Membership Tier", ["Guest", "Pro Subscriber"])
    
    st.divider()
    st.header("⚙️ Model Configuration")
    current_season = st.number_input("Season", value=2025)
    current_week = st.number_input("Week", value=19) 
    
    st.divider()
    st.subheader("Decay Parameters")
    qb_decay = st.slider("QB Decay (Talent)", 0.90, 0.999, 0.99)
    team_decay = st.slider("Team Decay (Recency)", 0.80, 0.99, 0.95)
    
    st.divider()
    st.subheader("Betting Rules")
    edge_threshold = st.number_input("Std. Edge Required", value=2.0)
    key_val_threshold = st.number_input("Key Number Edge (3/7)", value=1.5)

# --- CACHED DATA LOADING ---
@st.cache_data(ttl=86400) # Only fetch once every 24 hours
def load_nfl_data(seasons):
    schedule = nfl.load_schedules(seasons=seasons).to_pandas()
    stats = nfl.load_player_stats(seasons=seasons).to_pandas()
    if 'team' not in stats.columns: 
        stats['team'] = stats['recent_team']
    return schedule, stats

# --- MAIN APP LOGIC ---
try:
    # 1. LOAD & PREP
    schedule, stats = load_nfl_data([current_season-1, current_season])
    
    # Filter Valid Games for Training
    games = schedule[
        (schedule['game_type'].isin(['REG', 'POST'])) &
        (schedule['spread_line'].notnull()) &
        (schedule['total_line'].notnull()) &
        (schedule['result'].notnull())
    ].copy()
    
    current_slate = schedule[
        (schedule['season'] == current_season) & 
        (schedule['week'] == current_week)
    ].copy()

    games['market_line'] = -games['spread_line']
    current_slate['market_line'] = -current_slate['spread_line']

    # 2. MAP STARTERS
    passers = stats[stats['attempts'] > 0].sort_values('attempts', ascending=False)
    starters = passers.groupby(['season', 'week', 'team']).head(1)
    starter_map = {}
    for _, row in starters.iterrows():
        starter_map[(row['season'], row['week'], row['team'])] = row['player_display_name']

    def assign_starters(row):
        h = starter_map.get((row['season'], row['week'], row['home_team']))
        a = starter_map.get((row['season'], row['week'], row['away_team']))
        return pd.Series([h, a])

    games[['home_qb', 'away_qb']] = games.apply(assign_starters, axis=1)
    games = games.dropna(subset=['home_qb', 'away_qb']).copy()

    sorted_games = games.sort_values(['season', 'week'])
    last_qb_map = {}
    for _, row in sorted_games.iterrows():
        last_qb_map[row['home_team']] = row['home_qb']
        last_qb_map[row['away_team']] = row['away_qb']

    # --- REGRESSION ---
    games['weight'] = games.apply(lambda x: qb_decay ** ((current_season - x['season']) * 52 + (current_week - x['week'])), axis=1)
    
    h_team = pd.get_dummies(games['home_team'], dtype=int)
    a_team = pd.get_dummies(games['away_team'], dtype=int)
    h_qb = pd.get_dummies(games['home_qb'], dtype=int)
    a_qb = pd.get_dummies(games['away_qb'], dtype=int)
    
    all_teams = sorted(list(set(h_team.columns).union(a_team.columns)))
    all_qbs = set(h_qb.columns).union(a_qb.columns)
    
    h_team = h_team.reindex(columns=all_teams, fill_value=0)
    a_team = a_team.reindex(columns=all_teams, fill_value=0)
    h_qb = h_qb.reindex(columns=all_qbs, fill_value=0)
    a_qb = a_qb.reindex(columns=all_qbs, fill_value=0)

    # MODEL 1: SPREAD
    X_spread = pd.concat([h_team.sub(a_team), h_qb.sub(a_qb)], axis=1)
    X_spread['HFA'] = 1
    clf_qbs = Ridge(alpha=1.5, fit_intercept=False).fit(X_spread, games['market_line'], sample_weight=games['weight'])
    
    coefs = pd.Series(clf_qbs.coef_, index=X_spread.columns)
    qb_dict = (coefs[list(all_qbs)] - coefs[list(all_qbs)].mean()).to_dict()

    games_s2 = games[games['season'] == current_season].copy()
    games_s2['roster_line'] = games_s2.apply(lambda r: r['market_line'] - (qb_dict.get(r['home_qb'], 0) - qb_dict.get(r['away_qb'], 0)), axis=1)
    games_s2['s2_weight'] = games_s2.apply(lambda x: team_decay ** (current_week - x['week']), axis=1)
    
    h_s2 = pd.get_dummies(games_s2['home_team'], dtype=int).reindex(columns=all_teams, fill_value=0)
    a_s2 = pd.get_dummies(games_s2['away_team'], dtype=int).reindex(columns=all_teams, fill_value=0)
    X_s2 = h_s2.sub(a_s2)
    X_s2['HFA'] = 1
    clf_teams = Ridge(alpha=1.0, fit_intercept=False).fit(X_s2, games_s2['roster_line'], sample_weight=games_s2['s2_weight'])
    
    hfa_final = clf_teams.coef_[list(X_s2.columns).index('HFA')]
    team_dict = pd.Series(clf_teams.coef_, index=X_s2.columns).drop('HFA').to_dict()

    # MODEL 2: TOTALS
    X_total = pd.concat([h_team.add(a_team), h_qb.add(a_qb)], axis=1)
    clf_total = Ridge(alpha=1.5, fit_intercept=True).fit(X_total, games['total_line'], sample_weight=games['weight'])
    base_total_int = clf_total.intercept_
    ou_qb_dict = pd.Series(clf_total.coef_, index=X_total.columns)[list(all_qbs)].to_dict()
    ou_team_dict = pd.Series(clf_total.coef_, index=X_total.columns)[list(all_teams)].to_dict()

    # --- DASHBOARD ---
    st.subheader("1. Matchup Settings")
    input_data = []
    for _, game in current_slate.iterrows():
        input_data.append({
            "Away Team": game['away_team'], "Away QB": last_qb_map.get(game['away_team'], "(Generic Backup)"),
            "Home Team": game['home_team'], "Home QB": last_qb_map.get(game['home_team'], "(Generic Backup)"),
            "Vegas (Home)": game['market_line'] or 0.0, "Vegas Total": game['total_line'] or 45.0
        })
    
    qb_options = sorted(list(qb_dict.keys()))
    qb_options.insert(0, "(Generic Backup)")

    edited_df = st.data_editor(pd.DataFrame(input_data), column_config={
        "Away QB": st.column_config.SelectboxColumn("Away QB", options=qb_options),
        "Home QB": st.column_config.SelectboxColumn("Home QB", options=qb_options),
    }, hide_index=True)

    # RESULTS
    st.subheader("2. Live Projections")
    res = []
    for _, row in edited_df.iterrows():
        # Spread
        m_line = (team_dict.get(row['Home Team'], 0) + qb_dict.get(row['Home QB'], 0) + hfa_final) - (team_dict.get(row['Away Team'], 0) + qb_dict.get(row['Away QB'], 0))
        edge = m_line - row['Vegas (Home)']
        
        # Totals
        m_total = base_total_int + ou_team_dict.get(row['Home Team'], 0) + ou_team_dict.get(row['Away Team'], 0) + ou_qb_dict.get(row['Home QB'], 0) + ou_qb_dict.get(row['Away QB'], 0)
        t_edge = m_total - row['Vegas Total']

        # Pick Logic (Subscription Gated)
        pick, t_pick = "🔒 Pro Required", "🔒 Pro Required"
        if user_status == "Pro Subscriber":
            pick = "PASS"
            if edge < -edge_threshold: pick = f"BET {row['Home Team']}"
            elif edge > edge_threshold: pick = f"BET {row['Away Team']}"
            
            t_pick = "PASS"
            if t_edge > edge_threshold: t_pick = "BET OVER"
            elif t_edge < -edge_threshold: t_pick = "BET UNDER"

        res.append({
            "Matchup": f"{row['Away Team']} @ {row['Home Team']}",
            "Model Line": round(m_line, 1), "Vegas": row['Vegas (Home)'], "Edge": round(edge, 1), "SIGNAL": pick,
            "Model Total": round(m_total, 1), "V_Total": row['Vegas Total'], "T_Edge": round(t_edge, 1), "TOTAL PICK": t_pick
        })

    st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)

    # RATINGS
    with st.expander("3. View Team Power Ratings"):
        p_data = [{"Team": t, "QB": last_qb_map.get(t, "(Generic Backup)")} for t in all_teams]
        p_df = pd.DataFrame(p_data)
        p_df['Team Rtg'] = p_df['Team'].map(team_dict)
        p_df['QB Rtg'] = p_df['QB'].map(qb_dict).fillna(0)
        p_df['Total'] = p_df['Team Rtg'] + p_df['QB Rtg']
        st.dataframe(p_df.sort_values('Total'), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Waiting for Data... {e}")
