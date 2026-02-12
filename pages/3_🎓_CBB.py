import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from sklearn.linear_model import Ridge
import io
import time

# --- CONFIGURATION ---
API_KEY = 'rTQCNjitVG9Rs6LDYzuUVU4YbcpyVCA6mq2QSkPj8iTkxi3UBVbic+obsBlk7JCo' 
YEAR = 2026 
BASE_URL = 'https://api.collegebasketballdata.com'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'accept': 'application/json'}

KENPOM_HCA_DATA = {
    "West Virginia": 4.5, "TCU": 4.5, "Utah": 4.5, "New Mexico": 4.3, "Wake Forest": 4.2,
    "Texas Tech": 4.2, "Oklahoma": 4.1, "Utah St.": 4.1, "BYU": 4.1, "Rutgers": 4.0,
    "St. Bonaventure": 3.9, "Saint Louis": 3.9, "Nevada": 3.9, "Colorado": 3.9, "Evansville": 3.9,
    "Bradley": 3.9, "Kansas": 3.9, "Auburn": 3.9, "Oklahoma St.": 3.8, "Mississippi St.": 3.8,
    "Western Kentucky": 3.8, "Connecticut": 3.8, "Arkansas": 3.8, "Kansas St.": 3.7, "Iowa St.": 3.7,
    "Baylor": 3.7, "Colorado St.": 3.7, "Villanova": 3.7, "Cincinnati": 3.7, "Middle Tennessee": 3.7,
    "Tulsa": 3.7, "Missouri": 3.6, "Illinois St.": 3.6, "Tennessee": 3.6, "Charlotte": 3.6,
    "Kentucky": 3.6, "Maryland": 3.6, "Alabama": 3.6, "San Diego St.": 3.6, "Indiana St.": 3.6,
    "Texas": 3.6, "Utah Valley": 3.6, "UTEP": 3.6, "LSU": 3.6, "Georgia": 3.6,
    "Grand Canyon": 3.6, "Denver": 3.6, "Nebraska Omaha": 3.6, "Arizona": 3.6, "Loyola Chicago": 3.5,
    "Iowa": 3.5, "UAB": 3.5, "Clemson": 3.5, "North Carolina": 3.5, "South Dakota St.": 3.5,
    "Tennessee St.": 3.5, "Virginia": 3.5, "Marquette": 3.5, "UCF": 3.5, "New Mexico St.": 3.5,
    "Ohio": 3.5, "North Carolina Central": 3.5, "Penn St.": 3.5, "Purdue": 3.5, "Air Force": 3.5,
    "Nebraska": 3.4, "N.C. State": 3.4, "Memphis": 3.4, "Boise St.": 3.4, "Virginia Tech": 3.4,
    "Ohio St.": 3.4, "North Carolina A&T": 3.4, "Drake": 3.4, "Oregon": 3.4, "Wyoming": 3.4,
    "California": 3.3, "Howard": 3.3, "Xavier": 3.3, "Louisville": 3.3, "Milwaukee": 3.3,
    "Norfolk St.": 3.3, "Oregon St.": 3.3, "Creighton": 3.3, "Dayton": 3.3, "Southeast Missouri": 3.3,
    "St. Thomas": 3.3, "South Carolina": 3.3, "UCLA": 3.3, "La Salle": 3.3, "Massachusetts": 3.3,
    "USC": 3.3, "Stanford": 3.3, "St. John's": 3.3, "Duke": 3.3, "Washington St.": 3.2,
    "George Mason": 3.2, "Oral Roberts": 3.2, "Providence": 3.2, "East Carolina": 3.2, "Northern Iowa": 3.2,
    "SMU": 3.2, "Southern": 3.2, "FIU": 3.2, "Stephen F. Austin": 3.2, "William & Mary": 3.2,
    "North Texas": 3.2, "Missouri St.": 3.2, "Drexel": 3.2, "Syracuse": 3.2, "Indiana": 3.2,
    "Weber St.": 3.2, "Hampton": 3.2, "Louisiana Tech": 3.2, "Tarleton St.": 3.2, "Seton Hall": 3.1,
    "Michigan": 3.1, "Florida St.": 3.1, "Michigan St.": 3.1, "Florida Atlantic": 3.1, "Kansas City": 3.1,
    "Montana St.": 3.1, "South Dakota": 3.1, "Cleveland St.": 3.1, "Monmouth": 3.1, "Illinois": 3.1,
    "Marshall": 3.1, "Butler": 3.1, "Washington": 3.1, "Houston": 3.1, "Pittsburgh": 3.1,
    "Cal Baptist": 3.1, "UNLV": 3.1, "Saint Joseph's": 3.1, "Cal St. Bakersfield": 3.1, "Maryland Eastern Shore": 3.1,
    "Minnesota": 3.1, "Boston College": 3.0, "Alabama A&M": 3.0, "San Jose St.": 3.0, "DePaul": 3.0,
    "Texas A&M": 3.0, "Southern Illinois": 3.0, "Kennesaw St.": 3.0, "Arizona St.": 3.0, "South Carolina St.": 3.0,
    "Wichita St.": 3.0, "Coastal Carolina": 3.0, "Eastern Kentucky": 3.0, "Georgia St.": 3.0, "Northern Kentucky": 3.0,
    "Detroit Mercy": 3.0, "VCU": 3.0, "Vanderbilt": 3.0, "Delaware St.": 2.9, "Wright St.": 2.9,
    "Sam Houston St.": 2.9, "Wisconsin": 2.9, "Montana": 2.9, "UNC Wilmington": 2.9, "Duquesne": 2.9,
    "Jacksonville": 2.9, "Miami FL": 2.9, "Little Rock": 2.9, "Lamar": 2.9, "Liberty": 2.9,
    "Seattle": 2.9, "Florida": 2.9, "Eastern Michigan": 2.9, "Western Illinois": 2.9, "Miami OH": 2.9,
    "Morehead St.": 2.9, "Southern Utah": 2.9, "Temple": 2.9, "Siena": 2.9, "Old Dominion": 2.9,
    "Murray St.": 2.9, "North Dakota": 2.9, "Troy": 2.9, "UTSA": 2.9, "Western Carolina": 2.8,
    "Queens": 2.8, "Southern Miss": 2.8, "Notre Dame": 2.8, "Northern Arizona": 2.8, "Utah Tech": 2.8,
    "Portland St.": 2.8, "Alcorn St.": 2.8, "Charleston": 2.8, "Bowling Green": 2.8, "North Alabama": 2.8,
    "Abilene Christian": 2.8, "Mississippi": 2.8, "Bucknell": 2.8, "UNC Asheville": 2.8, "James Madison": 2.8,
    "Samford": 2.8, "Georgetown": 2.8, "Youngstown St.": 2.8, "Gonzaga": 2.8, "Lindenwood": 2.8,
    "Richmond": 2.8, "George Washington": 2.8, "Iona": 2.8, "Buffalo": 2.8, "Florida A&M": 2.8,
    "Georgia Tech": 2.8, "Green Bay": 2.8, "Morgan St.": 2.8, "Tennessee Tech": 2.8, "Bryant": 2.7,
    "Furman": 2.7, "Davidson": 2.7, "Northwestern": 2.7, "Northern Colorado": 2.7, "Southern Indiana": 2.7,
    "Robert Morris": 2.7, "Saint Mary's": 2.7, "Central Arkansas": 2.7, "Rhode Island": 2.7, "Valparaiso": 2.7,
    "Texas A&M Corpus Chris": 2.7, "South Florida": 2.7, "Austin Peay": 2.7, "IU Indy": 2.7, "Appalachian St.": 2.7,
    "Kent St.": 2.7, "McNeese": 2.7, "Binghamton": 2.7, "Cal Poly": 2.7, "North Dakota St.": 2.7,
    "Florida Gulf Coast": 2.7, "SIUE": 2.7, "Towson": 2.7, "Chattanooga": 2.7, "Idaho St.": 2.6,
    "Mercer": 2.6, "Jackson St.": 2.6, "Ball St.": 2.6, "West Georgia": 2.6, "High Point": 2.6,
    "North Florida": 2.6, "Nicholls": 2.6, "Campbell": 2.6, "Tulane": 2.6, "Idaho": 2.6,
    "Illinois Chicago": 2.6, "Belmont": 2.6, "Oakland": 2.6, "Akron": 2.6, "Western Michigan": 2.6,
    "Purdue Fort Wayne": 2.6, "Maine": 2.6, "Winthrop": 2.6, "Dartmouth": 2.6, "Elon": 2.6,
    "Chicago St.": 2.6, "East Tennessee St.": 2.5, "Tennessee Martin": 2.5, "Georgia Southern": 2.5, "Loyola Marymount": 2.5,
    "Niagara": 2.5, "Fresno St.": 2.5, "UT Rio Grande Valley": 2.5, "Texas Southern": 2.5, "Cornell": 2.5,
    "The Citadel": 2.5, "UT Arlington": 2.5, "San Francisco": 2.5, "Louisiana": 2.5, "Saint Peter's": 2.5,
    "Arkansas St.": 2.5, "Louisiana Monroe": 2.5, "Rice": 2.5, "Sacramento St.": 2.5, "Pacific": 2.5,
    "Mississippi Valley St.": 2.4, "Jacksonville St.": 2.4, "Incarnate Word": 2.4, "Texas St.": 2.4, "New Hampshire": 2.4,
    "Saint Francis": 2.4, "Mercyhurst": 2.4, "Delaware": 2.4, "Canisius": 2.4, "Bellarmine": 2.4,
    "Hawaii": 2.4, "Fordham": 2.4, "South Alabama": 2.4, "Stony Brook": 2.4, "USC Upstate": 2.4,
    "Prairie View A&M": 2.4, "Vermont": 2.4, "Fairfield": 2.4, "VMI": 2.3, "NJIT": 2.3,
    "Quinnipiac": 2.3, "New Orleans": 2.3, "Alabama St.": 2.3, "Central Michigan": 2.3, "Santa Clara": 2.3,
    "Eastern Illinois": 2.3, "UC Santa Barbara": 2.3, "Marist": 2.3, "Bethune Cookman": 2.3, "Northwestern St.": 2.3,
    "Coppin St.": 2.3, "Presbyterian": 2.3, "Penn": 2.3, "Longwood": 2.3, "UMass Lowell": 2.3,
    "Houston Christian": 2.3, "Lipscomb": 2.3, "Yale": 2.3, "UNC Greensboro": 2.3, "Toledo": 2.3,
    "Northern Illinois": 2.3, "CSUN": 2.3, "Eastern Washington": 2.3, "Stonehill": 2.2, "LIU": 2.2,
    "Le Moyne": 2.2, "Southeastern Louisiana": 2.2, "UC Riverside": 2.2, "Radford": 2.2, "Army": 2.2,
    "Boston University": 2.2, "Colgate": 2.2, "Wofford": 2.2, "Long Beach St.": 2.2, "Northeastern": 2.2,
    "New Haven": 2.2, "American": 2.2, "Rider": 2.2, "Sacred Heart": 2.2, "Lafayette": 2.1,
    "Cal St. Fullerton": 2.1, "UC Irvine": 2.1, "Stetson": 2.1, "East Texas A&M": 2.1, "Hofstra": 2.1,
    "Harvard": 2.1, "Princeton": 2.1, "Holy Cross": 2.1, "Lehigh": 2.1, "Albany": 2.1,
    "Pepperdine": 2.0, "Arkansas Pine Bluff": 2.0, "Mount St. Mary's": 2.0, "Wagner": 2.0, "Grambling St.": 2.0,
    "Charleston Southern": 2.0, "San Diego": 2.0, "Gardner Webb": 2.0, "Columbia": 2.0, "Merrimack": 1.9,
    "UC San Diego": 1.9, "Loyola MD": 1.9, "Brown": 1.8, "UMBC": 1.8, "Portland": 1.8,
    "Central Connecticut": 1.8, "Navy": 1.7, "UC Davis": 1.7, "Manhattan": 1.7, "Fairleigh Dickinson": 1.5
}

def get_team_name(team_obj):
    if isinstance(team_obj, dict): return team_obj.get('name', 'Unknown')
    return str(team_obj)

def utc_to_et(iso_date_str):
    if not iso_date_str: return datetime.now()
    try:
        date_str = iso_date_str.replace('Z', '+00:00')
        dt_utc = datetime.fromisoformat(date_str)
        dt_et = dt_utc.astimezone(timezone(timedelta(hours=-5)))
        return dt_et
    except ValueError:
        return datetime.now()

def get_kenpom_hca(api_name, default_hca):
    if api_name in KENPOM_HCA_DATA: return KENPOM_HCA_DATA[api_name]
    if "State" in api_name:
        try_name = api_name.replace("State", "St.")
        if try_name in KENPOM_HCA_DATA: return KENPOM_HCA_DATA[try_name]
    if "St." in api_name:
        try_name = api_name.replace("St.", "State")
        if try_name in KENPOM_HCA_DATA: return KENPOM_HCA_DATA[try_name]
    return default_hca 

@st.cache_data(ttl=86400) # This saves API calls for 24 hours!
def fetch_api_data(year):
    fallback_conferences = [{'abbreviation': 'ACC'}, {'abbreviation': 'B12'}, {'abbreviation': 'B10'}, {'abbreviation': 'SEC'}]
    conferences = []
    try:
        conf_resp = requests.get(f"{BASE_URL}/conferences", headers=HEADERS)
        if conf_resp.status_code == 200:
            conferences = conf_resp.json()
        else:
            conferences = fallback_conferences
    except:
        conferences = fallback_conferences

    all_games = []
    all_lines = []
    
    for conf in conferences:
        conf_abbr = conf.get('abbreviation')
        try:
            g_resp = requests.get(f"{BASE_URL}/games", headers=HEADERS, params={'season': year, 'conference': conf_abbr})
            if g_resp.status_code == 200: all_games.extend(g_resp.json())
            l_resp = requests.get(f"{BASE_URL}/lines", headers=HEADERS, params={'season': year, 'conference': conf_abbr})
            if l_resp.status_code == 200: all_lines.extend(l_resp.json())
        except:
            pass
        time.sleep(0.2) 

    unique_games = {g['id']: g for g in all_games}.values()
    unique_lines = {str(l.get('gameId')): l for l in all_lines}.values()
    return list(unique_games), list(unique_lines)

def run_analysis():
    st.title("🏀 AlphaPoint: CBB Projections")

    # --- SIMULATED SUBSCRIPTION GATE ---
    st.sidebar.subheader("User Account")
    user_status = st.sidebar.radio("Membership Tier", ["Guest", "Pro Subscriber"])
    
    # 1. SIDEBAR SETTINGS
    st.sidebar.subheader("Model Parameters")
    now_et = datetime.now(timezone(timedelta(hours=-5)))
    selected_date = st.sidebar.date_input("Target Date", now_et)
    today_str = selected_date.strftime('%Y-%m-%d')
    decay_alpha = st.sidebar.slider("Decay Alpha", 0.000, 0.100, 0.035, 0.001)
    
    hca_mode = st.sidebar.radio("HCA Data:", ["Manual Slider", "KenPom"])
    manual_hca = st.sidebar.slider("Global HCA", 2.0, 5.0, 3.2, 0.1) if hca_mode == "Manual Slider" else 3.2
    
    base_threshold = st.sidebar.number_input("Base Threshold", value=2.0)
    spread_factor = st.sidebar.slider("Volatility Factor", 0.00, 0.15, 0.05)

    # 2. RUN MODEL
    games_json, lines_json = fetch_api_data(YEAR)
    if not games_json:
        st.error("Data Load Failed.")
        return

    # Process games & build matrix
    todays_games = []
    game_meta = {}
    for g in games_json:
        h, a = get_team_name(g.get('homeTeam')), get_team_name(g.get('awayTeam'))
        dt_et = utc_to_et(g.get('startDate', ''))
        date_et = dt_et.strftime('%Y-%m-%d')
        game_meta[f"{h}_{a}"] = {'is_neutral': g.get('neutralSite', False), 'date_et': date_et}
        if date_et == today_str:
            g['et_datetime'] = dt_et
            todays_games.append(g)

    matchups = []
    target_dt_obj = datetime.strptime(today_str, '%Y-%m-%d')
    lines_map = {str(l.get('gameId', '')): l for l in lines_json if l.get('gameId')}

    for game in lines_json:
        lines = game.get('lines', [])
        if not lines: continue
        s = lines[0].get('spread')
        if s is None: continue
        h, a = get_team_name(game.get('homeTeam')), get_team_name(game.get('awayTeam'))
        meta = game_meta.get(f"{h}_{a}")
        if not meta: continue
        days_ago = (target_dt_obj - datetime.strptime(meta['date_et'], '%Y-%m-%d')).days
        if days_ago < 0: continue 
        
        weight = np.exp(-decay_alpha * days_ago)
        hca_to_remove = manual_hca if hca_mode == "Manual Slider" else get_kenpom_hca(h, 3.2)
        adj_margin = (-1 * float(s)) - (0 if meta['is_neutral'] else hca_to_remove)
        matchups.append({'Home': h, 'Away': a, 'Adjusted_Margin': adj_margin, 'Weight': weight})

    df = pd.DataFrame(matchups)
    X = pd.get_dummies(df['Home'], dtype=int).reindex(columns=sorted(list(set(df['Home']) | set(df['Away']))), fill_value=0).sub(
        pd.get_dummies(df['Away'], dtype=int).reindex(columns=sorted(list(set(df['Home']) | set(df['Away']))), fill_value=0)
    )
    clf = Ridge(alpha=1.0, fit_intercept=False).fit(X, df['Adjusted_Margin'], sample_weight=df['Weight'])
    market_ratings = pd.Series(clf.coef_, index=X.columns)

    # 3. DISPLAY
    ratings_df = pd.DataFrame({'Team': market_ratings.index, 'Rating': market_ratings.values}).sort_values('Rating', ascending=False)
    with st.expander("📊 Neutral Court Ratings"):
        st.dataframe(ratings_df.head(25), use_container_width=True)

    if not todays_games:
        st.info("No games today.")
    else:
        projections = []
        for g in todays_games:
            h, a = get_team_name(g.get('homeTeam')), get_team_name(g.get('awayTeam'))
            is_n = g.get('neutralSite', False)
            hca = 0.0 if is_n else (manual_hca if hca_mode == "Manual Slider" else get_kenpom_hca(h, 3.2))
            my_spread = -1 * ((market_ratings.get(h, 0) - market_ratings.get(a, 0)) + hca)
            
            vegas = None
            gid = str(g.get('id'))
            if gid in lines_map and lines_map[gid].get('lines'):
                vegas = float(lines_map[gid]['lines'][0].get('spread'))
            
            edge = vegas - my_spread if vegas is not None else 0.0
            thresh = base_threshold + (abs(vegas or 0) * spread_factor)
            
            # --- GATE THE PICK ---
            pick = "🔒 Subscribe to view"
            if user_status == "Pro Subscriber":
                if edge > thresh: pick = f"BET {h} ({edge:.1f})"
                elif edge < -thresh: pick = f"BET {a} ({abs(edge):.1f})"
                else: pick = "No Value"

            projections.append({'Time': g['et_datetime'].strftime('%I:%M %p'), 'Matchup': f"{a} @ {h}", 'My Spread': round(my_spread, 1), 'Vegas': vegas or "N/A", 'Pick': pick})
        
        st.dataframe(pd.DataFrame(projections), use_container_width=True)

if __name__ == "__main__":
    run_analysis()
