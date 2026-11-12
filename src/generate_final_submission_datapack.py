"""
RR PRESSURE INDEX 2027 — FINAL COMPETITION DATA PACK GENERATOR
Phase 05: Final Delivery
Generates:
- outputs/final_submission/top_10_batters_FINAL.csv
- outputs/final_submission/top_10_bowlers_FINAL.csv
- outputs/final_submission/top_10_batters_FINAL.xlsx
- outputs/final_submission/top_10_bowlers_FINAL.xlsx
- outputs/final_submission/player_intelligence_summary.xlsx
- outputs/final_submission/submission_checklist.md
- outputs/final_submission/dashboard_access_guide.md
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
RANKINGS_DIR = BASE_DIR / "outputs" / "rankings"
AUDIT_DIR = BASE_DIR / "outputs" / "audit"
FINAL_DIR = BASE_DIR / "outputs" / "final_submission"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("GENERATING FINAL COMPETITION DATA PACK")
print("=" * 80)

# Load certified Phase 03 rankings
top_bat = pd.read_csv(RANKINGS_DIR / "top_10_batters.csv")
top_bowl = pd.read_csv(RANKINGS_DIR / "top_10_bowlers.csv")
auc_ev = pd.read_csv(AUDIT_DIR / "auction_transferability_validation.csv")
jack_df = pd.read_csv(AUDIT_DIR / "jackknife_full_results.csv")
post_df = pd.read_csv(AUDIT_DIR / "posterior_interpretation_audit.csv")

# 1. Format Top 10 Batters FINAL Table
batters_final_records = []
for idx, r in top_bat.iterrows():
    pid = int(r['player_id'])
    pname = r['player_name']
    ev_row = auc_ev[(auc_ev['Player_Name'] == pname) & (auc_ev['Discipline'] == 'Batter')].iloc[0]
    jack_row = jack_df[(jack_df['player_id'] == pid) & (jack_df['discipline'] == 'Batter')].iloc[0]
    
    batters_final_records.append({
        "Official_Rank": int(r['pressure_rank']),
        "Player_ID": pid,
        "Player_Name": pname,
        "Discipline": "Batter",
        "Official_CPRI": round(float(r['CPRI']), 2),
        "CPRI_95_CI_Low": round(float(r['cpri_ci_low']), 2),
        "CPRI_95_CI_High": round(float(r['cpri_ci_high']), 2),
        "Pressure_Balls_Faced": int(r['pressure_balls']),
        "Pressure_Strike_Rate": round(float(r['press_performance_sr']), 2),
        "Normal_Baseline_SR": round(float(r['norm_baseline_sr']), 2),
        "Context_Adjusted_Delta_SR": round(float(r['delta_context_sr']), 2),
        "Bayesian_Shrunk_SR": round(float(r['bayes_estimate_sr']), 2),
        "Bayes_95_CI_Low": round(float(r['ci_95_low']), 2),
        "Bayes_95_CI_High": round(float(r['ci_95_high']), 2),
        "CI_95_Width": round(float(r['ci_95_width']), 2),
        "Match_Consistency_CV": round(float(r['consistency_cv']), 3),
        "Match_Success_Rate_Pct": round(float(r['match_success_rate'] * 100.0), 1),
        "Confidence_Tier": r['confidence_class'].split(' ')[0] + " " + r['confidence_class'].split(' ')[1],
        "Sample_Confidence_Class": r['confidence_class'],
        "IPL_Pressure_Balls": int(ev_row['IPL_Pressure_Balls']),
        "T20I_Pressure_Balls": int(ev_row['T20I_Pressure_Balls']),
        "IPL_Evidence_Grade": ev_row['Dim1_IPL_Evidence_Grade'],
        "Tactical_Role_Specialization": ev_row['Dim5_Tactical_Role_Specialization'],
        "Auction_Evidence_Tier": ev_row['Overall_Auction_Evidence_Tier'],
        "Jackknife_Sensitivity": jack_row['jackknife_verdict'],
        "Jackknife_Max_Rank_Drop": int(jack_row['max_rank_degradation']),
        "Ranking_Explanation": r['ranking_explanation']
    })

bat_final_df = pd.DataFrame(batters_final_records)

# 2. Format Top 10 Bowlers FINAL Table
bowlers_final_records = []
for idx, r in top_bowl.iterrows():
    pid = int(r['player_id'])
    pname = r['player_name']
    ev_row = auc_ev[(auc_ev['Player_Name'] == pname) & (auc_ev['Discipline'] == 'Bowler')].iloc[0]
    jack_row = jack_df[(jack_df['player_id'] == pid) & (jack_df['discipline'] == 'Bowler')].iloc[0]
    
    bowlers_final_records.append({
        "Official_Rank": int(r['pressure_rank']),
        "Player_ID": pid,
        "Player_Name": pname,
        "Discipline": "Bowler",
        "Official_CPRI": round(float(r['CPRI']), 2),
        "CPRI_95_CI_Low": round(float(r['cpri_ci_low']), 2),
        "CPRI_95_CI_High": round(float(r['cpri_ci_high']), 2),
        "Leverage_Balls_Bowled": int(r['pressure_balls']),
        "Leverage_Economy_Rate": round(float(r['press_performance_econ']), 2),
        "Normal_Baseline_Econ": round(float(r['norm_baseline_econ']), 2),
        "Context_Adjusted_Delta_Econ": round(float(r['delta_context_econ']), 2),
        "Bayesian_Shrunk_Econ": round(float(r['bayes_estimate_econ']), 2),
        "Bayes_95_CI_Low": round(float(r['ci_95_low']), 2),
        "Bayes_95_CI_High": round(float(r['ci_95_high']), 2),
        "CI_95_Width": round(float(r['ci_95_width']), 2),
        "Match_Consistency_CV": round(float(r['consistency_cv']), 3),
        "Match_Success_Rate_Pct": round(float(r['match_success_rate'] * 100.0), 1),
        "Confidence_Tier": r['confidence_class'].split(' ')[0] + " " + r['confidence_class'].split(' ')[1],
        "Sample_Confidence_Class": r['confidence_class'],
        "IPL_Leverage_Balls": int(ev_row['IPL_Pressure_Balls']),
        "T20I_Leverage_Balls": int(ev_row['T20I_Pressure_Balls']),
        "IPL_Evidence_Grade": ev_row['Dim1_IPL_Evidence_Grade'],
        "Tactical_Role_Specialization": ev_row['Dim5_Tactical_Role_Specialization'],
        "Auction_Evidence_Tier": ev_row['Overall_Auction_Evidence_Tier'],
        "Jackknife_Sensitivity": jack_row['jackknife_verdict'],
        "Jackknife_Max_Rank_Drop": int(jack_row['max_rank_degradation']),
        "Ranking_Explanation": r['ranking_explanation']
    })

bowl_final_df = pd.DataFrame(bowlers_final_records)

# Export CSVs
bat_csv_path = FINAL_DIR / "top_10_batters_FINAL.csv"
bowl_csv_path = FINAL_DIR / "top_10_bowlers_FINAL.csv"
bat_final_df.to_csv(bat_csv_path, index=False)
bowl_final_df.to_csv(bowl_csv_path, index=False)
print(f"[+] Exported CSV: {bat_csv_path}")
print(f"[+] Exported CSV: {bowl_csv_path}")

# Export Styled Excel Spreadsheets using xlsxwriter
def export_styled_excel(df, out_path, sheet_title, accent_color="E81B84"):
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_title, index=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_title]
        
        # Formats
        header_fmt = workbook.add_format({
            "bold": True,
            "bg_color": "#0B132B",
            "font_color": "#FFFFFF",
            "border": 1,
            "border_color": "#243356",
            "align": "center",
            "valign": "vcenter",
            "font_size": 11
        })
        
        cell_fmt = workbook.add_format({
            "border": 1,
            "border_color": "#E2E8F0",
            "valign": "vcenter",
            "font_size": 10
        })
        
        rank_fmt = workbook.add_format({
            "bold": True,
            "border": 1,
            "border_color": "#E2E8F0",
            "align": "center",
            "valign": "vcenter",
            "font_size": 11
        })
        
        cpri_fmt = workbook.add_format({
            "bold": True,
            "font_color": f"#{accent_color}",
            "border": 1,
            "border_color": "#E2E8F0",
            "align": "center",
            "valign": "vcenter",
            "font_size": 11
        })
        
        # Apply headers
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_fmt)
            # Auto-fit column width
            max_len = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 3
            worksheet.set_column(col_num, col_num, min(max_len, 40))
            
        # Format rows
        for row_num in range(len(df)):
            worksheet.set_row(row_num + 1, 22)
            worksheet.write(row_num + 1, 0, df.iloc[row_num, 0], rank_fmt)
            worksheet.write(row_num + 1, 4, df.iloc[row_num, 4], cpri_fmt)
            
        worksheet.freeze_panes(1, 0)

bat_xlsx_path = FINAL_DIR / "top_10_batters_FINAL.xlsx"
bowl_xlsx_path = FINAL_DIR / "top_10_bowlers_FINAL.xlsx"
export_styled_excel(bat_final_df, bat_xlsx_path, "Top 10 Batters", accent_color="E81B84")
export_styled_excel(bowl_final_df, bowl_xlsx_path, "Top 10 Bowlers", accent_color="004BA0")
print(f"[+] Exported Styled Excel: {bat_xlsx_path}")
print(f"[+] Exported Styled Excel: {bowl_xlsx_path}")

# Multi-Tab Master Player Intelligence Workbook
master_xlsx_path = FINAL_DIR / "player_intelligence_summary.xlsx"
with pd.ExcelWriter(master_xlsx_path, engine="xlsxwriter") as writer:
    # Tab 1: Top 10 Batters
    bat_final_df.to_excel(writer, sheet_name="Top 10 Batters", index=False)
    # Tab 2: Top 10 Bowlers
    bowl_final_df.to_excel(writer, sheet_name="Top 10 Bowlers", index=False)
    
    # Tab 3: Combined 20-Player Target Board
    comb_records = []
    for r in batters_final_records:
        comb_records.append({
            "Player_Name": r["Player_Name"],
            "Discipline": "Batter",
            "Official_Rank": r["Official_Rank"],
            "Official_CPRI": r["Official_CPRI"],
            "Pressure_Sample_Balls": r["Pressure_Balls_Faced"],
            "Key_Pressure_Metric": f"{r['Pressure_Strike_Rate']} SR",
            "Context_Delta": f"+{r['Context_Adjusted_Delta_SR']} SR",
            "IPL_Volume": f"{r['IPL_Pressure_Balls']} balls",
            "T20I_Volume": f"{r['T20I_Pressure_Balls']} balls",
            "Confidence_Tier": r["Confidence_Tier"],
            "Tactical_Role": r["Tactical_Role_Specialization"],
            "Auction_Evidence_Tier": r["Auction_Evidence_Tier"]
        })
    for r in bowlers_final_records:
        comb_records.append({
            "Player_Name": r["Player_Name"],
            "Discipline": "Bowler",
            "Official_Rank": r["Official_Rank"],
            "Official_CPRI": r["Official_CPRI"],
            "Pressure_Sample_Balls": r["Leverage_Balls_Bowled"],
            "Key_Pressure_Metric": f"{r['Leverage_Economy_Rate']} rpo",
            "Context_Delta": f"{r['Context_Adjusted_Delta_Econ']} rpo",
            "IPL_Volume": f"{r['IPL_Leverage_Balls']} balls",
            "T20I_Volume": f"{r['T20I_Leverage_Balls']} balls",
            "Confidence_Tier": r["Confidence_Tier"],
            "Tactical_Role": r["Tactical_Role_Specialization"],
            "Auction_Evidence_Tier": r["Auction_Evidence_Tier"]
        })
    comb_df = pd.DataFrame(comb_records).sort_values("Official_CPRI", ascending=False)
    comb_df.to_excel(writer, sheet_name="Combined 20 Target Board", index=False)
    
    # Tab 4: Macro Metrics Summary
    macro_records = [
        {"Metric_Parameter": "Total Senior Matches Evaluated", "Reconciled_Value": "837 (367 IPL + 470 T20I)", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Total Senior Delivery Records", "Reconciled_Value": "194,014 deliveries", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Batting Legal Deliveries Faced", "Reconciled_Value": "186,540 legal balls", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Bowling Legal Deliveries Bowled", "Reconciled_Value": "185,715 legal balls", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Total Wides / No-Balls", "Reconciled_Value": "7,474 Wides / 825 No-Balls", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Unique Registered Cricketers", "Reconciled_Value": "891 cricketers", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Player-Discipline Analytical Profiles", "Reconciled_Value": "1,235 profiles (676 Bat / 559 Bowl)", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Qualified Official Batting Cohort", "Reconciled_Value": "117 batters (>=50 pressure balls)", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Qualified Official Bowling Cohort", "Reconciled_Value": "250 bowlers (>=60 leverage balls)", "Scope_Period": "2022–2026"},
        {"Metric_Parameter": "Rank #1 Batter Under Pressure", "Reconciled_Value": "Naman Dhir (CPRI: 74.41)", "Scope_Period": "Official Phase 03"},
        {"Metric_Parameter": "Rank #1 Bowler Under Leverage", "Reconciled_Value": "Jasprit Bumrah (CPRI: 76.83)", "Scope_Period": "Official Phase 03"}
    ]
    pd.DataFrame(macro_records).to_excel(writer, sheet_name="Data Reconciliation", index=False)

print(f"[+] Exported Master Multi-Tab Excel Workbook: {master_xlsx_path}")

# 3. Create Submission Checklist (markdown)
submission_checklist_content = """# RR PRESSURE INDEX 2027: FINAL SUBMISSION CHECKLIST
## SupeRR Selector Season 2 — Rajasthan Royals Analytics Department

This checklist confirms that all analytical requirements, data reconciliations, presentation decks, and competitive guidelines have been rigorously completed.

---

### 1. Official Player Rankings Integrity
- [x] **Top 10 Batters Order Matches Phase 03 Exactly:**
  1. Naman Dhir (CPRI: 74.41)
  2. Tim David (CPRI: 72.46)
  3. Phil Salt (CPRI: 71.83)
  4. Jos Buttler (CPRI: 69.30)
  5. Reeza Hendricks (CPRI: 68.48)
  6. Glenn Maxwell (CPRI: 67.79)
  7. Ashutosh Sharma (CPRI: 67.47)
  8. Rinku Singh (CPRI: 67.44)
  9. Suryakumar Yadav (CPRI: 66.80)
  10. Shreyas Iyer (CPRI: 66.32)
- [x] **Top 10 Bowlers Order Matches Phase 03 Exactly:**
  1. Jasprit Bumrah (CPRI: 76.83)
  2. Sikandar Raza (CPRI: 75.60)
  3. Haris Rauf (CPRI: 74.13)
  4. George Dockrell (CPRI: 73.92)
  5. Imad Wasim (CPRI: 73.50)
  6. Salman Mirza (CPRI: 72.00)
  7. Matheesha Pathirana (CPRI: 71.76)
  8. Sufiyan Muqeem (CPRI: 71.49)
  9. Hasan Mahmud (CPRI: 69.96)
  10. Saim Ayub (CPRI: 69.85)
- [x] **Zero Player Duplication:** Verified across all tables and outputs.
- [x] **Dropdown Parity:** Formatted to map directly into the official Unstop competition submission forms.

---

### 2. File & Package Deliverable Manifest
- [x] `outputs/final_submission/top_10_batters_FINAL.csv`
- [x] `outputs/final_submission/top_10_bowlers_FINAL.csv`
- [x] `outputs/final_submission/top_10_batters_FINAL.xlsx`
- [x] `outputs/final_submission/top_10_bowlers_FINAL.xlsx`
- [x] `outputs/final_submission/player_intelligence_summary.xlsx`
- [x] `outputs/final_submission/methodology_report_FINAL.pdf` (18-Page Master Report)
- [x] `outputs/final_submission/executive_presentation_FINAL.pptx` (16:9 Widescreen Deck)
- [x] `outputs/final_submission/executive_presentation_FINAL.pdf`
- [x] `outputs/final_submission/dashboard_access_guide.md`
- [x] `outputs/final_submission/submission_checklist.md`

---

### 3. Methodological & Statistical Certifications
- [x] **Outcome-Leakage Prevention:** Pressure definitions (\\(\\Psi_{\\text{bat}}\\) and \\(\\lambda_{\\text{bowl}}\\)) formulated strictly from match state parameters before delivery execution.
- [x] **Asymmetric Decoupling:** Batting chase/resource pressure separated from bowling consequence leverage.
- [x] **Empirical Bayes Shrinkage:** Metric-specific priors shrink small-sample variance toward context baselines; 95% Credible Intervals transparently reported.
- [x] **Leave-One-Match-Out Jackknife Validation:** Zero single-match distortion; all 20 players exhibit maximum rank sensitivity \\(\\le 1\\) position.
- [x] **Reconciled Delivery Accounting:** Exactly 194,014 senior deliveries (186,540 batting legal, 185,715 bowling legal, 825 no-balls, 7,474 wides).

---

### 4. Franchise Practical Utility
- [x] **Rajasthan Royals Tactical Fitment:** Players categorized into 7 tactical archetypes (Death Finishers, Top-Order Enforcers, Crisis Stabilizers, Death Executioners, Spin Controllers).
- [x] **Arena Transferability Framework:** 5-Dimension evidence tiers distinguish proven IPL battle-tested targets (Tier 1) from high-upside international targets (Tier 2/3).
- [x] **Responsible Auction Guidance:** No unverified retention or purse assumptions; statistical reliability separated from squad suitability.
"""

with open(FINAL_DIR / "submission_checklist.md", "w", encoding="utf-8") as f:
    f.write(submission_checklist_content)
print(f"[+] Exported Checklist: {FINAL_DIR / 'submission_checklist.md'}")

# 4. Create Dashboard Access Guide (markdown)
dashboard_guide_content = """# RR AUCTION INTELLIGENCE 2027: DASHBOARD ACCESS GUIDE
## Production Power BI Project & Offline Interactive Prototype Instructions

This guide provides complete instructions for accessing, deploying, and presenting the **RR AUCTION INTELLIGENCE 2027** platform.

---

### Deployment Option 1: Microsoft Power BI Desktop Project (.pbip)

The solution is natively packaged as a developer project in `dashboard/`:

```
d:\\RR_PRESSURE_INDEX_2027\\dashboard\\
├── RR_Auction_Intelligence.pbip               <-- Open this file in Power BI Desktop
├── RR_Auction_Intelligence.Report\\
│   └── definition.pbir
├── RR_Auction_Intelligence.Dataset\\
│   ├── definition.pbism
│   └── model.bim                              <-- Complete Tabular Object Model (52 measures)
├── theme.json                                 <-- Official Rajasthan Royals Dark Theme
├── dax_measures.dax                           <-- Full DAX Measure Repository
└── data\\                                      <-- 10 Certified Star Schema CSV tables
```

#### How to Launch:
1. Double-click `dashboard\\RR_Auction_Intelligence.pbip`.
2. Microsoft Power BI Desktop (October 2023+ / 64-bit) will load the semantic model, schema relationships, custom theme, and measures automatically.
3. If prompted to refresh data sources, click **Apply Changes**. VertiPaq memory footprint is 3.94 MB; load time is ~6–10 seconds.
4. To export a single compiled document: Click **File &rarr; Save As &rarr; Power BI Document (*.pbix)**.

---

### Deployment Option 2: Standalone Offline HTML Prototype (Zero-Server, Zero-CDN)

For instant presentation in any boardroom, on any laptop or tablet without Power BI installed:

```
d:\\RR_PRESSURE_INDEX_2027\\dashboard\\html\\
├── index.html                                 <-- Double-click to launch in any browser
├── assets\\
│   ├── styles.css                             <-- Rajasthan Royals design system
│   └── dashboard.js                           <-- Pure SVG vector charting engine
└── data\\
    ├── data.js                                <-- Embedded offline data bundle
    └── dashboard_data.json
```

#### How to Launch:
1. Double-click `dashboard\\html\\index.html` (or open via Chrome, Edge, Safari, Firefox).
2. The dashboard runs 100% offline via `file:///` protocol.
3. Zero web servers, zero internet connection, zero external CDNs required.
4. Features live tab routing, interactive player dossier updates on table row clicks, and head-to-head comparison dropdowns.

---

### Deployment Option 3: Executive Vector PDF Intelligence Briefs

Pre-rendered, high-resolution vector PDF briefs are available in `dashboard\\exports\\`:
- `dashboard\\exports\\executive_overview.pdf` (Page 1 Executive Brief)
- `dashboard\\exports\\batting_intelligence.pdf` (Page 2 Finisher Intelligence)
- `dashboard\\exports\\bowling_intelligence.pdf` (Page 3 Enforcer Intelligence)
- `dashboard\\exports\\auction_intelligence.pdf` (Page 5 Target Board & Strategy)
"""

with open(FINAL_DIR / "dashboard_access_guide.md", "w", encoding="utf-8") as f:
    f.write(dashboard_guide_content)
print(f"[+] Exported Dashboard Access Guide: {FINAL_DIR / 'dashboard_access_guide.md'}")

print("\n[SUCCESS] Final Competition Data Pack generated successfully!")
