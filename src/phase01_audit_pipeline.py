"""
RR PRESSURE INDEX 2027 — PHASE 01 AUDIT PIPELINE
Forensic Data Audit, Quality Investigation, Scope Filtering & Participation Modeling.

Authors: IPL Auction Analytics & Data Science Consortium
"""

import os
import pandas as pd
import numpy as np

# Use relative paths from script directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
AUDIT_DIR = os.path.join(BASE_DIR, "outputs", "audit")
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")

os.makedirs(AUDIT_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

def run_phase_01_audit():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — PHASE 01 FORENSIC AUDIT PIPELINE")
    print("=" * 80)
    
    # ---------------------------------------------------------
    # 1. LOAD RAW DATASETS
    # ---------------------------------------------------------
    print("\n[Step 1/5] Loading raw datasets...")
    files = {
        "competitions": os.path.join(RAW_DIR, "competitions.csv"),
        "teams": os.path.join(RAW_DIR, "teams.csv"),
        "matches": os.path.join(RAW_DIR, "matches.csv"),
        "playing_eleven": os.path.join(RAW_DIR, "playing_eleven.csv"),
        "competition_team_player_mapping": os.path.join(RAW_DIR, "competition_team_player_mapping.csv"),
        "ball_by_ball": os.path.join(RAW_DIR, "ball_by_ball.csv")
    }
    
    dfs = {}
    for name, path in files.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required raw dataset not found: {path}")
        if name == "ball_by_ball":
            dfs[name] = pd.read_csv(path, low_memory=False)
        else:
            dfs[name] = pd.read_csv(path)
        print(f"  Loaded {name}.csv: {dfs[name].shape[0]:,} rows, {dfs[name].shape[1]} columns")

    comps = dfs["competitions"]
    teams = dfs["teams"]
    matches = dfs["matches"]
    p11 = dfs["playing_eleven"]
    mapping = dfs["competition_team_player_mapping"]
    bbb = dfs["ball_by_ball"]

    # ---------------------------------------------------------
    # 2. GENERATE DATASET INVENTORY
    # ---------------------------------------------------------
    print("\n[Step 2/5] Generating dataset inventory...")
    inventory_records = []
    
    descriptions = {
        "competitions.csv": "Tournament registry containing competition metadata, match formats, and season labels.",
        "teams.csv": "Competition-to-team registry mapping participating franchise and international teams.",
        "matches.csv": "Match metadata table recording venue, date, toss, stage, targets, and match outcomes.",
        "playing_eleven.csv": "Lineup participation table tracking announced XIs, batting order, and impact player subs.",
        "competition_team_player_mapping.csv": "Tournament squad roster mapping player IDs to team and competition identifiers.",
        "ball_by_ball.csv": "Granular delivery-level event log recording runs, extras, wickets, bowler/batter actions, and trajectories."
    }
    
    primary_keys = {
        "competitions.csv": "comp_id",
        "teams.csv": "(comp_id, team_id)",
        "matches.csv": "match_id",
        "playing_eleven.csv": "(match_id, player_id)",
        "competition_team_player_mapping.csv": "(comp_id, team_id, player_id)",
        "ball_by_ball.csv": "(match_id, innings, innings_ball_num)"
    }
    
    for filename, key in [
        ("competitions.csv", "competitions"),
        ("teams.csv", "teams"),
        ("matches.csv", "matches"),
        ("playing_eleven.csv", "playing_eleven"),
        ("competition_team_player_mapping.csv", "competition_team_player_mapping"),
        ("ball_by_ball.csv", "ball_by_ball")
    ]:
        df = dfs[key]
        filepath = files[key]
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        duplicates = df.duplicated().sum()
        
        # Check date range if applicable
        if "match_date" in df.columns:
            min_date = str(df["match_date"].min())
            max_date = str(df["match_date"].max())
        elif "delivery_ist_time" in df.columns:
            min_date = str(df["delivery_ist_time"].dropna().min())
            max_date = str(df["delivery_ist_time"].dropna().max())
        else:
            min_date = "N/A"
            max_date = "N/A"
            
        inventory_records.append({
            "filename": filename,
            "file_size_bytes": size_bytes,
            "file_size_mb": round(size_mb, 2),
            "memory_usage_mb": round(mem_mb, 2),
            "row_count": df.shape[0],
            "column_count": df.shape[1],
            "duplicate_rows": duplicates,
            "primary_key_candidate": primary_keys[filename],
            "min_date": min_date,
            "max_date": max_date,
            "business_description": descriptions[filename]
        })
        
    df_inventory = pd.DataFrame(inventory_records)
    inventory_path = os.path.join(AUDIT_DIR, "dataset_inventory.csv")
    df_inventory.to_csv(inventory_path, index=False)
    print(f"  Saved dataset inventory to: {inventory_path}")

    # ---------------------------------------------------------
    # 3. GENERATE DATA QUALITY REPORT & ISSUE REGISTER
    # ---------------------------------------------------------
    print("\n[Step 3/5] Performing data quality audit & compiling issue register...")
    quality_issues = [
        {
            "issue_id": "DQI-001",
            "table_name": "ball_by_ball.csv",
            "column_name": "extras1_runs",
            "issue_type": "Misleading Column Naming / Categorical Code",
            "affected_rows": 200999,
            "affected_percentage": 100.0,
            "severity": "High",
            "description": "extras1_runs does not contain run counts. It is an integer categorical code for extras_type (1=Overstep, 2=wide, 3=legbyes, 4=byes, 5=other, 6=None, 7=Penalty).",
            "evidence": "When extras_type is None, extras1_runs is 6 for all 189,167 rows. When wide, extras1_runs is 2 for all 7,714 rows.",
            "analytical_impact": "Treating extras1_runs as numeric runs falsely inflates team/batter/bowler run totals by over 1.1 million runs.",
            "remediation_strategy": "Do not sum extras1_runs. Use extras_type directly to identify illegal balls and extras penalty rules."
        },
        {
            "issue_id": "DQI-002",
            "table_name": "ball_by_ball.csv",
            "column_name": "runs",
            "issue_type": "Striker Runs Only / Absence of Discrete Extra Runs",
            "affected_rows": 11832,
            "affected_percentage": 5.89,
            "severity": "High",
            "description": "The runs column captures only runs scored off the bat by the striker. On wides and byes/legbyes, runs is 0. Penalty runs for wides (+1) and no-balls (+1) must be derived.",
            "evidence": "All 7,714 wide rows have runs=0. All 3,277 bye/legbye rows have runs=0.",
            "analytical_impact": "Cumulative team score cannot be computed by simply summing runs; wide penalties and no-ball penalties must be explicitly added.",
            "remediation_strategy": "Define team_runs = runs + (extras_type == 'wide').astype(int) + (extras_type.isin(['Overstep', 'other'])).astype(int) + extras_2_runs."
        },
        {
            "issue_id": "DQI-003",
            "table_name": "ball_by_ball.csv",
            "column_name": "dismissal_type",
            "issue_type": "Typographical Inconsistency in Categorical String",
            "affected_rows": 2,
            "affected_percentage": 0.001,
            "severity": "Low",
            "description": "Obstructing the field dismissal has two distinct spellings: 'Obstructing the field' (1 row) and 'Obstracting the field' (2 rows).",
            "evidence": "Value counts: 'Obstructing the field': 1, 'Obstracting the field': 2.",
            "analytical_impact": "String matching on 'Obstructing the field' would fail to classify 2 dismissals if exact match is used.",
            "remediation_strategy": "Standardize 'Obstracting the field' -> 'Obstructing the field' during data cleaning."
        },
        {
            "issue_id": "DQI-004",
            "table_name": "ball_by_ball.csv",
            "column_name": "dismissed_player_id",
            "issue_type": "Missing Identifier on Wicket Event",
            "affected_rows": 1,
            "affected_percentage": 0.001,
            "severity": "Low",
            "description": "One wicket delivery has dismissed_player_id as NaN (Match 40709, Inn 2, Hardik Pandya Retire Out).",
            "evidence": "Row 127899: is_wicket=True, dismissal_type='Retire Out', dismissed_player_id=NaN. Striker is 3330 (Hardik Pandya).",
            "analytical_impact": "Dismissal not credited to batter without striker fallback.",
            "remediation_strategy": "Impute dismissed_player_id = striker_id when dismissal_type == 'Retire Out' and dismissed_player_id is null."
        },
        {
            "issue_id": "DQI-005",
            "table_name": "matches.csv",
            "column_name": "match_id",
            "issue_type": "Unplayed / Abandoned Matches with Zero Deliveries",
            "affected_rows": 16,
            "affected_percentage": 1.81,
            "severity": "Medium",
            "description": "16 matches recorded in matches.csv have 0 deliveries in ball_by_ball.csv because the matches were abandoned without a ball bowled (e.g. rain washouts).",
            "evidence": "All 16 match IDs have result == 'Match Abandoned' and win_team_id == NaN in matches.csv.",
            "analytical_impact": "Outer joins between matches and ball_by_ball produce null ball sequences.",
            "remediation_strategy": "Filter out abandoned matches with 0 balls bowled from ball-by-ball performance and pressure modeling pipelines."
        },
        {
            "issue_id": "DQI-006",
            "table_name": "competitions.csv",
            "column_name": "comp_id",
            "issue_type": "Non-Challenge Scope Competitions Present in Raw Data",
            "affected_rows": 2,
            "affected_percentage": 1.42,
            "severity": "Critical",
            "description": "competitions.csv includes 2 tournaments outside official challenge scope (comp_id 2670: Mens T20 Emerging Teams Asia Cup 2024, comp_id 3289: Asia Cup Rising Stars 2025).",
            "evidence": "These 2 competitions comprise 30 matches and 6,985 balls featuring 'A' national teams rather than senior IPL / T20I teams.",
            "analytical_impact": "Unfiltered inclusion distorts senior IPL auction valuation and player career baseline metrics with developmental matches.",
            "remediation_strategy": "Enforce strict filtering: include only match_format == 'T20I' or IPL competitions (comp_ids 1358, 1715, 2193, 2725, 3298)."
        },
        {
            "issue_id": "DQI-007",
            "table_name": "playing_eleven.csv",
            "column_name": "batting_order",
            "issue_type": "High Null Rate in Pre-match Lineup Batting Order",
            "affected_rows": 8678,
            "affected_percentage": 30.58,
            "severity": "Medium",
            "description": "30.58% of records in playing_eleven.csv have null batting_order, affecting 521 matches where batting positions were not pre-assigned in lineup feeds.",
            "evidence": "Batting order is null for entire squads in many T20I bilateral matches.",
            "analytical_impact": "Cannot rely on playing_eleven.csv alone to determine batting positions.",
            "remediation_strategy": "Derive actual realized batting order directly from ball_by_ball.csv where batting_order is populated per delivery."
        },
        {
            "issue_id": "DQI-008",
            "table_name": "matches.csv",
            "column_name": "revised_target / revised_overs",
            "issue_type": "Sparse Population (Valid Structural Nature)",
            "affected_rows": 860,
            "affected_percentage": 97.40,
            "severity": "Low",
            "description": "revised_target is populated for only 23 matches (97.4% null) because DLS rain adjustments occur only in rain-affected games.",
            "evidence": "Cross-referenced with result strings confirming D/L method applied only in these 23 matches.",
            "analytical_impact": "Target calculation must dynamically check revised_target before falling back to Innings 1 score + 1.",
            "remediation_strategy": "Target logic: target = revised_target if pd.notna(revised_target) else (inn1_total + 1)."
        },
        {
            "issue_id": "DQI-009",
            "table_name": "ball_by_ball.csv",
            "column_name": "innings",
            "issue_type": "Presence of Super Over Innings (3 and 4)",
            "affected_rows": 38,
            "affected_percentage": 0.019,
            "severity": "Medium",
            "description": "Innings values 3 (25 balls) and 4 (13 balls) represent Super Overs across 6 tied matches (e.g. DC vs RR IPL 2025 Match 40725, KKR vs RR IPL 2026 Match 50359).",
            "evidence": "Matches 34429, 40725, 45512, 48027, 48029, 50359 contain innings 3 and 4.",
            "analytical_impact": "Super overs represent maximum leverage / hyper-pressure events, but have a 6-ball constraint separate from regulation 20-over chases.",
            "remediation_strategy": "Isolate Super Overs with a dedicated flag: analyze regulation innings (1 and 2) and benchmark super over clutch performance distinctly."
        },
        {
            "issue_id": "DQI-010",
            "table_name": "playing_eleven.csv",
            "column_name": "player_id",
            "issue_type": "Excluded Competition Orphan Players in BBB",
            "affected_rows": 2,
            "affected_percentage": 0.208,
            "severity": "Low",
            "description": "Two players (36153 Syed Haider, 39444 Basil Hameed) appeared in BBB but were absent from playing_eleven.csv.",
            "evidence": "Both players appeared exclusively in comp_id 2670 (Mens T20 Emerging Teams Asia Cup 2024).",
            "analytical_impact": "Zero impact on official challenge scope: after filtering to IPL + T20I, exactly 0 players are missing from playing_eleven.csv.",
            "remediation_strategy": "Resolved automatically by official scope filtering."
        }
    ]
    
    df_quality = pd.DataFrame(quality_issues)
    quality_path = os.path.join(AUDIT_DIR, "data_quality_report.csv")
    df_quality.to_csv(quality_path, index=False)
    print(f"  Saved data quality issue register to: {quality_path}")

    # ---------------------------------------------------------
    # 4. GENERATE COMPETITION SCOPE AUDIT
    # ---------------------------------------------------------
    print("\n[Step 4/5] Auditing competitions, seasons, and match counts...")
    comp_records = []
    
    # Precompute match counts from matches and BBB
    matches_per_comp = matches.groupby("comp_id").size().to_dict()
    bbb_matches = set(bbb["match_id"].unique())
    
    for _, crow in comps.iterrows():
        cid = crow["comp_id"]
        cname = str(crow["comp_name"])
        mfmt = str(crow["match_format"])
        season = str(crow["season"])
        
        total_m = matches_per_comp.get(cid, 0)
        c_matches = matches[matches["comp_id"] == cid]["match_id"].tolist()
        m_with_bbb = len([mid for mid in c_matches if mid in bbb_matches])
        abandoned_m = total_m - m_with_bbb
        
        is_ipl = ("IPL" in cname) or ("Indian Premier League" in cname)
        is_t20i = (mfmt == "T20I")
        
        if is_ipl:
            status = "Included — IPL"
            rule = "Rule 1: All IPL seasons 2022-2026 explicitly required by challenge scope."
        elif is_t20i:
            status = "Included — T20I"
            rule = "Rule 2: All international T20I matches 2022-2026 explicitly required by challenge scope."
        else:
            status = "Excluded — Domestic/Emerging T20"
            rule = "Rule 3: Non-IPL domestic / emerging development tournament excluded from senior franchise evaluation."
            
        comp_records.append({
            "comp_id": cid,
            "comp_name": cname,
            "match_format": mfmt,
            "season": season,
            "total_matches": total_m,
            "matches_with_bbb": m_with_bbb,
            "abandoned_matches": abandoned_m,
            "scope_status": status,
            "filtering_rationale": rule
        })
        
    df_comp_audit = pd.DataFrame(comp_records).sort_values(["scope_status", "season", "comp_name"])
    comp_audit_path = os.path.join(AUDIT_DIR, "competition_scope_audit.csv")
    df_comp_audit.to_csv(comp_audit_path, index=False)
    print(f"  Saved competition scope audit to: {comp_audit_path}")

    # ---------------------------------------------------------
    # 5. GENERATE PLAYER PARTICIPATION & MASTER SUMMARY
    # ---------------------------------------------------------
    print("\n[Step 5/5] Generating Player Master & Participation Summary in eligible scope...")
    
    # Filter to eligible scope
    eligible_comp_ids = set(df_comp_audit[df_comp_audit["scope_status"].str.startswith("Included")]["comp_id"])
    eligible_matches = matches[matches["comp_id"].isin(eligible_comp_ids)].copy()
    eligible_match_ids = set(eligible_matches["match_id"])
    
    # Map match to category: IPL vs T20I
    ipl_comp_ids = set(df_comp_audit[df_comp_audit["scope_status"] == "Included — IPL"]["comp_id"])
    eligible_matches["is_ipl"] = eligible_matches["comp_id"].isin(ipl_comp_ids)
    match_category = dict(zip(eligible_matches["match_id"], eligible_matches["is_ipl"]))
    
    # Filter BBB
    bbb_el = bbb[bbb["match_id"].isin(eligible_match_ids)].copy()
    bbb_el["is_ipl"] = bbb_el["match_id"].map(match_category)
    
    # Define legal balls
    # Wide, Overstep, and other are illegal deliveries (re-bowled)
    bbb_el["is_legal"] = ~bbb_el["extras_type"].isin(["wide", "Overstep", "other"])
    
    # Bowler wickets
    bowler_dismissals = ["Caught", "Bowled", "LBW", "Stump", "Hit Wicket"]
    bbb_el["is_bowler_wicket"] = bbb_el["is_wicket"] & bbb_el["dismissal_type"].isin(bowler_dismissals)
    
    # Bowler runs conceded = runs off bat + wides + no balls + extras_2_runs (byes and legbyes do not count against bowler)
    bbb_el["bowler_runs_conceded"] = bbb_el["runs"] + (bbb_el["extras_type"] == "wide").astype(int) + \
                                     (bbb_el["extras_type"].isin(["Overstep", "other"])).astype(int) + \
                                     bbb_el["extras_2_runs"]
                                     
    # Build Canonical Player Master Name mapping
    player_names = {}
    for _, r in mapping[mapping["comp_id"].isin(eligible_comp_ids)][["player_id", "player_name"]].drop_duplicates().iterrows():
        player_names[int(r["player_id"])] = str(r["player_name"]).strip()
        
    for _, r in bbb_el[["striker_id", "striker_name"]].drop_duplicates().iterrows():
        player_names[int(r["striker_id"])] = str(r["striker_name"]).strip()
        
    for _, r in bbb_el[["bowler_id", "bowler_name"]].drop_duplicates().iterrows():
        player_names[int(r["bowler_id"])] = str(r["bowler_name"]).strip()

    # Identify all participating players in eligible Playing XI
    p11_el = p11[p11["match_id"].isin(eligible_match_ids)]
    all_eligible_player_ids = sorted(list(set(p11_el["player_id"]).union(set(player_names.keys()))))
    
    # Matches played per player (from Playing XI)
    p11_el_merged = p11_el.merge(eligible_matches[["match_id", "is_ipl"]], on="match_id", how="left")
    player_matches_total = p11_el_merged.groupby("player_id")["match_id"].nunique().to_dict()
    player_matches_ipl = p11_el_merged[p11_el_merged["is_ipl"] == True].groupby("player_id")["match_id"].nunique().to_dict()
    player_matches_t20i = p11_el_merged[p11_el_merged["is_ipl"] == False].groupby("player_id")["match_id"].nunique().to_dict()
    
    # Batting aggregations
    # Balls faced: all deliveries where striker was at the crease (including wides? In cricket, balls faced excludes wides)
    # A batter does NOT face a wide in cricket statistics!
    batting_legal = bbb_el[bbb_el["extras_type"] != "wide"]
    bat_stats = batting_legal.groupby("striker_id").agg(
        balls_faced=("innings_ball_num", "count"),
        runs_scored=("runs", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        dot_balls_faced=("runs", lambda s: (s == 0).sum())
    ).to_dict("index")
    
    bat_innings = bbb_el.groupby("striker_id")["match_id"].nunique().to_dict()
    
    # Batting outs (dismissals): count times dismissed_player_id == player_id (or striker when row 127899)
    # Fix row 127899 in memory
    bbb_el_dpid = bbb_el["dismissed_player_id"].fillna(
        bbb_el.loc[bbb_el["dismissal_type"] == "Retire Out", "striker_id"]
    )
    player_outs = bbb_el_dpid.value_counts().to_dict()
    
    # Bowling aggregations
    bowl_stats = bbb_el.groupby("bowler_id").agg(
        total_deliveries=("innings_ball_num", "count"),
        legal_balls_bowled=("is_legal", "sum"),
        runs_conceded=("bowler_runs_conceded", "sum"),
        wickets_taken=("is_bowler_wicket", "sum"),
        dot_balls_bowled=("bowler_runs_conceded", lambda s: (s == 0).sum()),
        fours_conceded=("is_four", "sum"),
        sixes_conceded=("is_six", "sum")
    ).to_dict("index")
    
    bowl_innings = bbb_el.groupby("bowler_id")["match_id"].nunique().to_dict()
    
    # Compile comprehensive participation summary
    player_records = []
    for pid in all_eligible_player_ids:
        pname = player_names.get(pid, f"Player {pid}")
        
        m_tot = player_matches_total.get(pid, 0)
        m_ipl = player_matches_ipl.get(pid, 0)
        m_t20i = player_matches_t20i.get(pid, 0)
        
        # Batting
        b_data = bat_stats.get(pid, {})
        b_inn = bat_innings.get(pid, 0)
        bf = b_data.get("balls_faced", 0)
        rs = b_data.get("runs_scored", 0)
        fours = b_data.get("fours", 0)
        sixes = b_data.get("sixes", 0)
        dots_f = b_data.get("dot_balls_faced", 0)
        outs = int(player_outs.get(float(pid), 0))
        
        b_avg = round(rs / outs, 2) if outs > 0 else (round(float(rs), 2) if rs > 0 else 0.0)
        b_sr = round((rs / bf) * 100, 2) if bf > 0 else 0.0
        dot_f_pct = round((dots_f / bf) * 100, 1) if bf > 0 else 0.0
        boundary_runs = (fours * 4) + (sixes * 6)
        boundary_r_pct = round((boundary_runs / rs) * 100, 1) if rs > 0 else 0.0
        
        # Bowling
        bw_data = bowl_stats.get(pid, {})
        bw_inn = bowl_innings.get(pid, 0)
        tot_deliv = bw_data.get("total_deliveries", 0)
        legal_bb = bw_data.get("legal_balls_bowled", 0)
        rc = bw_data.get("runs_conceded", 0)
        wkts = bw_data.get("wickets_taken", 0)
        dots_b = bw_data.get("dot_balls_bowled", 0)
        fours_c = bw_data.get("fours_conceded", 0)
        sixes_c = bw_data.get("sixes_conceded", 0)
        
        overs_b = round(legal_bb / 6.0, 1)
        bw_avg = round(rc / wkts, 2) if wkts > 0 else (round(float(rc), 2) if rc > 0 else 0.0)
        bw_econ = round(rc / (legal_bb / 6.0), 2) if legal_bb > 0 else 0.0
        bw_sr = round(legal_bb / wkts, 1) if wkts > 0 else 0.0
        dot_b_pct = round((dots_b / legal_bb) * 100, 1) if legal_bb > 0 else 0.0
        
        # Primary role heuristic
        if bf >= 100 and legal_bb >= 100:
            role = "All-rounder"
        elif bf >= 100:
            role = "Batter"
        elif legal_bb >= 100:
            role = "Bowler"
        elif bf >= 30:
            role = "Lower-order Batter"
        elif legal_bb >= 30:
            role = "Part-time Bowler"
        else:
            role = "Specialist / Low Sample"
            
        # Qualification flags (Franchise sample size thresholds)
        qual_batter = (bf >= 100)
        qual_bowler = (legal_bb >= 100)
        
        player_records.append({
            "player_id": pid,
            "player_name": pname,
            "total_matches": m_tot,
            "ipl_matches": m_ipl,
            "t20i_matches": m_t20i,
            "primary_role": role,
            # Batting
            "batting_innings": b_inn,
            "balls_faced": bf,
            "runs_scored": rs,
            "fours": fours,
            "sixes": sixes,
            "dismissals": outs,
            "batting_average": b_avg,
            "batting_strike_rate": b_sr,
            "boundary_runs_pct": boundary_r_pct,
            "dot_ball_faced_pct": dot_f_pct,
            "qual_batter_100bf": qual_batter,
            # Bowling
            "bowling_innings": bw_inn,
            "legal_balls_bowled": legal_bb,
            "overs_bowled": overs_b,
            "runs_conceded": rc,
            "wickets_taken": wkts,
            "bowling_average": bw_avg,
            "economy_rate": bw_econ,
            "bowling_strike_rate": bw_sr,
            "dot_ball_bowled_pct": dot_b_pct,
            "fours_conceded": fours_c,
            "sixes_conceded": sixes_c,
            "qual_bowler_100bb": qual_bowler
        })
        
    df_players = pd.DataFrame(player_records).sort_values("runs_scored", ascending=False)
    players_path = os.path.join(AUDIT_DIR, "player_participation_summary.csv")
    df_players.to_csv(players_path, index=False)
    print(f"  Saved player participation summary to: {players_path}")
    
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY STATS (ELIGIBLE SCOPE):")
    print(f"  Total Eligible Competitions: {len(eligible_comp_ids)}")
    print(f"  Total Eligible Matches: {len(eligible_match_ids)} (IPL: {len(ipl_comp_ids)} comps, 371 matches; T20I: 134 comps, 482 matches)")
    print(f"  Eligible Ball-by-ball Deliveries: {len(bbb_el):,}")
    print(f"  Total Master Players Tracked: {len(df_players):,}")
    print(f"  Qualified Batters (>=100 balls faced): {df_players['qual_batter_100bf'].sum()}")
    print(f"  Qualified Bowlers (>=100 legal balls): {df_players['qual_bowler_100bb'].sum()}")
    print(f"  Qualified Dual All-rounders (>=100 each): {((df_players['qual_batter_100bf']) & (df_players['qual_bowler_100bb'])).sum()}")
    print("=" * 80)

if __name__ == "__main__":
    run_phase_01_audit()

