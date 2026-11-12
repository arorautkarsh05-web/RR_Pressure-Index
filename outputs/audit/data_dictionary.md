# RR PRESSURE INDEX 2027 — Enterprise Data Dictionary
## SupeRR Selector Season 2 — Forensic Cricket Analytics Architecture

**Prepared by:** Lead Cricket Data Scientist & Data Engineering Architect  
**Evaluation Scope:** Senior Indian Premier League (IPL) and Men's T20 International (T20I) Matches (2022–2026)  
**Status:** Phase 01 Validated  

---

### Table of Contents
1. [Overview & Master Architecture](#1-overview--master-architecture)
2. [Dataset 1: competitions.csv](#2-dataset-1-competitionscsv)
3. [Dataset 2: teams.csv](#3-dataset-2-teamscsv)
4. [Dataset 3: matches.csv](#4-dataset-3-matchescsv)
5. [Dataset 4: playing_eleven.csv](#5-dataset-4-playing_elevencsv)
6. [Dataset 5: competition_team_player_mapping.csv](#6-dataset-5-competition_team_player_mappingcsv)
7. [Dataset 6: ball_by_ball.csv](#7-dataset-6-ball_by_ballcsv)
8. [Critical Forensic Annotations](#8-critical-forensic-annotations)

---

### 1. Overview & Master Architecture

The analytical ecosystem comprises six relational tables capturing metadata, tournament rosters, lineups, and granular ball-by-ball actions. 

| Table Name | Primary / Candidate Key | Rows | Columns | Scope Eligibility | Role in Pressure Engine |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `competitions.csv` | `comp_id` | 141 | 4 | 139 Included / 2 Excluded | Filter boundary for IPL & T20I |
| `teams.csv` | `(comp_id, team_id)` | 353 | 3 | 33 Eligible Teams (IPL + T20I) | Franchise & national team master |
| `matches.csv` | `match_id` | 883 | 22 | 853 Eligible (837 played, 16 abandoned) | Match situation & DLS target master |
| `playing_eleven.csv` | `(match_id, player_id)` | 28,381 | 9 | 1,002 Active Eligible Players | Squad selection & Impact sub registry |
| `competition_team_player_mapping.csv` | `(comp_id, team_id, player_id)` | 6,413 | 6 | 1,132 Eligible Players | Master player ID & name registry |
| `ball_by_ball.csv` | `(match_id, innings, innings_ball_num)` | 200,999 | 33 | 194,014 Eligible Deliveries | Ball-by-ball performance & pressure engine |

---

### 2. Dataset 1: `competitions.csv`

Registry table defining tournaments, match formats, and seasons.

| Column Name | Physical Type | Semantic Type | Null Count (%) | Allowed Values / Range | Cricketing / Business Definition | Forensic & Modeling Notes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `comp_id` | Integer | Primary Key | 0 (0.0%) | 1331 to 3568 | Unique surrogate identifier for tournament edition. | Core foreign key referenced by matches, teams, and rosters. |
| `comp_name` | String | Descriptor | 0 (0.0%) | Text strings | Official tournament edition title (e.g. "IPL 2024", "ICC Men's T20 World Cup 2024"). | Used to isolate IPL seasons (comp_ids: 1358, 1715, 2193, 2725, 3298). |
| `match_format`| String | Category | 0 (0.0%) | `'T20'`, `'T20I'` | Formal cricket classification. | 134 competitions are `'T20I'`. 7 are `'T20'` (5 IPL, 2 developmental). |
| `season` | String | Temporal | 0 (0.0%) | `2022` to `2026`, including `2022/23`, `2023/24`, `2024/25` | Competition operational season. | Captures multi-year international calendar cycles. |

---

### 3. Dataset 2: `teams.csv`

Registry of team entities per competition.

| Column Name | Physical Type | Semantic Type | Null Count (%) | Allowed Values / Range | Cricketing / Business Definition | Forensic & Modeling Notes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `comp_id` | Integer | Foreign Key | 0 (0.0%) | Valid `comp_id` | References tournament in `competitions.csv`. | Compound key with `team_id`. |
| `team_id` | Integer | Foreign Key | 0 (0.0%) | 1 to 4444 (38 unique) | Unique stable team identifier across all seasons. | 10 IPL teams, 23 senior T20I teams, 5 'A' developmental teams. |
| `team_name` | String | Descriptor | 0 (0.0%) | 38 unique team names | Standardized franchise or national federation title. | 100% consistent across datasets. No duplicate or variant naming found. |

---

### 4. Dataset 3: `matches.csv`

Match-level event metadata, venue parameters, conditions, and outcomes.

| Column Name | Physical Type | Semantic Type | Null Count (%) | Allowed Values / Range | Cricketing / Business Definition | Forensic & Modeling Notes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `match_id` | Integer | Primary Key | 0 (0.0%) | 13511 to 50359 | Unique surrogate identifier for each match. | 883 total matches; 853 in eligible scope (371 IPL, 482 T20I). |
| `comp_id` | Integer | Foreign Key | 0 (0.0%) | Valid `comp_id` | Foreign key referencing tournament. | All 883 matches map successfully to `competitions.csv`. |
| `match_number` | Integer | Metadata | 0 (0.0%) | 1 to 74 | Match sequential number in tournament fixture. | Useful for group stage vs playoff sequencing. |
| `match_date` | String/Date | Temporal | 0 (0.0%) | `2022-01-22` to `2026-11-01` | Calendar date of match commencement. | ISO-8601 YYYY-MM-DD. 100% within 2022+ scope. |
| `stage` | String | Category | 0 (0.0%) | League, Final, Qualifier, Eliminator, Semi Final, Super 4, Others | Tournament progression phase. | Crucial high-leverage context flag for playoff pressure. |
| `venue_id` | Integer | Identifier | 0 (0.0%) | 54 to 349 | Unique venue identifier. | Can be used for pitch/ground characterization. |
| `venue_country`| String | Geographic | 0 (0.0%) | India, Australia, West Indies, etc. | Host country where fixture was staged. | Context for subcontinental vs overseas pace/bounce conditions. |
| `home_team_id` | Integer | Foreign Key | 0 (0.0%) | Valid `team_id` | Designated home team entity ID. | Maps to `teams.csv`. |
| `home_team` | String | Descriptor | 0 (0.0%) | Text team name | Name of designated home team. | Matches `teams.csv` string. |
| `away_team_id` | Integer | Foreign Key | 0 (0.0%) | Valid `team_id` | Designated away team entity ID. | Maps to `teams.csv`. |
| `away_team` | String | Descriptor | 0 (0.0%) | Text team name | Name of designated away team. | Matches `teams.csv` string. |
| `home_team_captain_id` | Float | Identifier | 44 (4.98%) | Valid `player_id` | Player ID of home captain. | Null on missing match team sheets. |
| `away_team_captain_id` | Float | Identifier | 45 (5.10%) | Valid `player_id` | Player ID of away captain. | Null on missing match team sheets. |
| `toss_win_team_id` | Float | Identifier | 15 (1.70%) | Valid `team_id` | Team winning the pre-match coin toss. | Null on abandoned matches without toss. |
| `toss_opted` | String | Category | 15 (1.70%) | `'Batting'`, `'Fielding'` | Tactical decision opted by toss winning captain. | Chasing vs setting baseline context. |
| `man_of_the_match` | Integer | Identifier | 0 (0.0%) | 0 or valid `player_id` | Player adjudicated best performer (0 if no award). | Award tracking; 0 indicates abandoned or unawarded. |
| `first_inn_revised_overs` | Float | Metric | 858 (97.17%)| 5.0 to 19.0 | Revised overs allocation for Innings 1 under DLS. | Null for full 20-over regulation innings. |
| `second_inn_revised_overs`| Float | Metric | 858 (97.17%)| 5.0 to 19.0 | Revised overs allocation for Innings 2 under DLS. | Null for full 20-over regulation innings. |
| `revised_target` | Float | Metric | 860 (97.40%)| 41.0 to 207.0 | DLS-adjusted target for chasing team in Innings 2. | Essential for accurate chase pressure calculation in rain games. |
| `knock_out` | Integer | Flag | 0 (0.0%) | 0 or 1 | Indicator if match is a knockout elimination fixture. | High-stakes context weight. |
| `win_team_id` | Float | Foreign Key | 41 (4.64%) | Valid `team_id` | Team entity that won the match. | Null on ties (6 matches) and abandonments/no results (35 matches). |
| `result` | String | Text | 0 (0.0%) | Text outcome | Narrative outcome string (e.g. "India Won by 6 Wickets"). | Crucial for tie, super over, and abandonment identification. |

---

### 5. Dataset 4: `playing_eleven.csv`

Player lineup participation, captaincy, wicketkeeping, and impact substitutions.

| Column Name | Physical Type | Semantic Type | Null Count (%) | Allowed Values / Range | Cricketing / Business Definition | Forensic & Modeling Notes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `match_id` | Integer | Foreign Key | 0 (0.0%) | Valid `match_id` | Match in which player was registered. | Maps to `matches.csv`. |
| `team_id` | Integer | Foreign Key | 0 (0.0%) | Valid `team_id` | Team fielding the player. | Maps to `teams.csv`. |
| `player_id` | Integer | Foreign Key | 0 (0.0%) | Valid `player_id` | Unique player identifier. | Maps to `competition_team_player_mapping.csv`. |
| `batting_order` | Float | Sequence | 8,678 (30.58%)| 1.0 to 11.0 | Announced batting position in lineup feed. | High null rate in T20Is; use `ball_by_ball.csv` for actual batting order. |
| `is_played` | Boolean | Flag | 0 (0.0%) | `True`, `False` | Whether player took the field. | True for active Playing XI and activated Impact Players. |
| `is_captain` | Object/Bool | Flag | 8,667 (30.54%)| `True`, `False` | Designated team captain. | Leadership pressure context. |
| `is_wk` | Object/Bool | Flag | 8,667 (30.54%)| `True`, `False` | Designated wicketkeeper. | Fielding role attribution. |
| `is_impact` | Integer | Flag | 0 (0.0%) | 0 or 1 | Substituted onto field as Impact Player. | 558 instances in IPL 2023–2026. Tactical situational injection. |
| `is_impact_off`| Integer | Flag | 0 (0.0%) | 0 or 1 | Substituted off the field for an Impact Player. | 558 instances in IPL 2023–2026. |

---

### 6. Dataset 5: `competition_team_player_mapping.csv`

Tournament squad registry linking players to franchises and national squads.

| Column Name | Physical Type | Semantic Type | Null Count (%) | Allowed Values / Range | Cricketing / Business Definition | Forensic & Modeling Notes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `comp_id` | Integer | Foreign Key | 0 (0.0%) | Valid `comp_id` | Tournament edition identifier. | Maps to `competitions.csv`. |
| `comp_name` | String | Descriptor | 0 (0.0%) | Text string | Tournament title. | Matches `competitions.csv`. |
| `team_id` | Integer | Foreign Key | 0 (0.0%) | Valid `team_id` | Team identifier. | Maps to `teams.csv`. |
| `team_name` | String | Descriptor | 0 (0.0%) | Text string | Standardized team name. | Matches `teams.csv`. |
| `player_id` | Integer | Primary Key | 0 (0.0%) | 1 to 46830 | Canonical player ID. | Universal entity key across the entire project. |
| `player_name` | String | Descriptor | 0 (0.0%) | Text string | Official player name. | 100% harmonized; 0 spelling discrepancies found. |

---

### 7. Dataset 6: `ball_by_ball.csv`

Granular delivery-level event log capturing game state, ball dynamics, and outcomes.

| Column Name | Physical Type | Semantic Type | Null Count (%) | Allowed Values / Range | Cricketing / Business Definition | Forensic & Modeling Notes |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `match_id` | Integer | Foreign Key | 0 (0.0%) | Valid `match_id` | Match in which delivery occurred. | Maps to `matches.csv`. |
| `innings` | Integer | Identifier | 0 (0.0%) | 1, 2, 3, 4 | Innings sequence number. | 1 & 2 = Regulation; 3 & 4 = Super Over (38 balls). |
| `overid` | Integer | Sequence | 0 (0.0%) | 1 to 20 | Over index (1-based, 1 to 20). | Defines phase: Powerplay (1-6), Middle (7-15), Death (16-20). |
| `over_ball_num` | Integer | Sequence | 0 (0.0%) | 1 to 11 | Sequential ball number within the over. | Increments sequentially including illegal balls. |
| `innings_ball_num`| Integer | Sequence | 0 (0.0%) | 1 to 142 | Sequential delivery count in the innings. | Increments on every delivery (legal or illegal). |
| `batting_team_id`| Integer | Foreign Key | 0 (0.0%) | Valid `team_id` | Team batting on this delivery. | Maps to `teams.csv`. |
| `bowling_team_id`| Integer | Foreign Key | 0 (0.0%) | Valid `team_id` | Team bowling on this delivery. | Maps to `teams.csv`. |
| `striker_id` | Integer | Foreign Key | 0 (0.0%) | Valid `player_id` | Batter facing the delivery. | Canonical player key for batting metrics. |
| `striker_name` | String | Descriptor | 0 (0.0%) | Player name | Name of striker. | 100% consistent with Player Master. |
| `non_striker_id`| Float/Int | Foreign Key | 0 (0.0%) | Valid `player_id` | Batter at non-striker's crease. | Useful for partnership leverage tracking. |
| `non_striker_name`| String | Descriptor | 0 (0.0%) | Player name | Name of non-striker. | 100% consistent with Player Master. |
| `bowler_id` | Integer | Foreign Key | 0 (0.0%) | Valid `player_id` | Bowler delivering the ball. | Canonical player key for bowling metrics. |
| `bowler_name` | String | Descriptor | 0 (0.0%) | Player name | Name of bowler. | 100% consistent with Player Master. |
| `batting_type` | String | Category | 0 (0.0%) | `'RHB'`, `'LHB'` | Batting stance (Right/Left-hand). | Tactical matchup analysis (platoon splits). |
| `bowling_type` | String | Category | 0 (0.0%) | Fast, Fast-medium, Spin varieties | Bowling action/style classification. | Tactical matchup analysis. |
| `batting_order` | Integer | Sequence | 0 (0.0%) | 1 to 11 | Realized batting position of striker. | 100% complete; supersedes playing_eleven nulls. |
| `runs` | Integer | Metric | 0 (0.0%) | 0 to 6 | **Runs scored off the bat by the striker.** | **CRITICAL: Does NOT include extras.** Wides & byes have runs=0. |
| `is_four` | Boolean | Flag | 0 (0.0%) | `True`, `False` | Delivery resulted in a 4 off the bat. | Boundary pressure metric. |
| `is_six` | Boolean | Flag | 0 (0.0%) | `True`, `False` | Delivery resulted in a 6 off the bat. | Maximum boundary pressure metric. |
| `is_wicket` | Boolean | Flag | 0 (0.0%) | `True`, `False` | Delivery resulted in a dismissal. | 10,881 wickets. Leverage inflection point. |
| `dismissal_type_id`| Float | Identifier | 190,118 (94.59%)| 1.0 to 10.0 | Categorical ID for dismissal type. | Null on non-wicket deliveries. |
| `dismissal_type`| String | Category | 190,118 (94.59%)| Caught, Bowled, LBW, RunOut, Stump, Hit Wicket, Retire Out, Obstructing | Categorical description of wicket event. | Must distinguish bowler wickets from non-bowler wickets. |
| `dismissed_player_id`| Float | Foreign Key | 190,107 (94.58%)| Valid `player_id` | Player dismissed on this ball. | 1 row null on wicket (row 127899: Hardik Pandya Retire Out). |
| `extras_type` | String | Category | 189,167 (94.11%)| `wide`, `Overstep`, `byes`, `legbyes`, `other`, `Penalty` | Categorical classification of extra. | Essential for legal delivery flag and penalty addition. |
| `extras1_runs` | Integer | **Categorical Code**| 0 (0.0%) | 1 to 7 | **Enum code representing extras_type.** | **CRITICAL: 1=Overstep, 2=wide, 3=legbyes, 4=byes, 5=other, 6=None, 7=Penalty. NOT A RUN COUNT!** |
| `extras_2_runs` | Integer | Metric | 0 (0.0%) | 0, 1, 4 | Additional extra runs on rare no-ball events. | Non-zero in only 36 rows across the dataset. |
| `pace_or_spin` | String | Category | 0 (0.0%) | `'Pace'`, `'Spin'` | Broad classification of bowling craft. | Useful for pitch and phase adaptation analysis. |
| `bowl_speed` | Float | Metric | 0 (0.0%) | 0.0 to 157.0 km/h | Recorded radar speed of delivery (km/h). | 0.0 when radar telemetry is absent. |
| `stroke` | String | Category | 6,158 (3.06%) | Cover Drive, Pull, Cut, etc. | Batting shot classification. | Null when batter offered no shot or missed. |
| `delivery_style`| String | Category | 391 (0.19%) | Outswing, Inswing, Off Cutter, etc. | Specific delivery variation. | Tactical bowling execution metric. |
| `over_or_around`| String | Category | 407 (0.20%) | `'Over'`, `'Around'` | Bowling arm angle around wicket. | Matchup tactical context. |
| `on_or_off` | String | Category | 0 (0.0%) | `'On-side'`, `'Off-side'` | Sector trajectory of delivery. | Pitch dispersion mapping. |
| `delivery_ist_time`| String | Temporal | 0 (0.0%) | ISO-8601 Timestamp | Indian Standard Time timestamp. | Granular delivery progression tracker. |

---

### 8. Critical Forensic Annotations

1. **`extras1_runs` Misleading Label**: Summing this column will produce a catastrophic data error (+1.1M fake runs). It is an encoded integer surrogate for `extras_type`.
2. **Striker Runs vs Team Runs**: Team runs must be derived as:
   $$\text{team\_runs} = \text{runs} + \mathbf{1}_{\{\text{extras\_type} = \text{'wide'}\}} + \mathbf{1}_{\{\text{extras\_type} \in [\text{'Overstep'}, \text{'other'}]\}} + \text{extras\_2\_runs}$$
3. **Legal Ball Definition**:
   $$\text{is\_legal} = \mathbf{1}_{\{\text{extras\_type} \notin [\text{'wide'}, \text{'Overstep'}, \text{'other'}]\}}$$
4. **Bowler-Credited Wickets**:
   $$\text{is\_bowler\_wicket} = \text{is\_wicket} \land (\text{dismissal\_type} \in [\text{'Caught'}, \text{'Bowled'}, \text{'LBW'}, \text{'Stump'}, \text{'Hit Wicket'}])$$
   Run-outs (600), Retire Outs (6), and Obstructing the field (3) must never be credited to the bowler.
5. **Dismissal Typo Standardization**: Normalize `'Obstracting the field'` (2 instances) to `'Obstructing the field'` (1 instance).

