"""
RR AUCTION INTELLIGENCE 2027 — POWER BI PROJECT (.PBIP) GENERATOR
Creates a native, opening-ready Microsoft Power BI Developer Project (.pbip)
with complete Tabular Object Model (model.bim), Star Schema relationships,
and all 30+ certified DAX measures across 9 display folders.
"""

import json
import os
import re
from pathlib import Path

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
DASHBOARD_DIR = BASE_DIR / "dashboard"
DATA_DIR = DASHBOARD_DIR / "data"

PBIP_FILE = DASHBOARD_DIR / "RR_Auction_Intelligence.pbip"
REPORT_DIR = DASHBOARD_DIR / "RR_Auction_Intelligence.Report"
DATASET_DIR = DASHBOARD_DIR / "RR_Auction_Intelligence.Dataset"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate Root .pbip File
pbip_content = {
    "version": "1.0",
    "artifacts": [
        {
            "report": {
                "path": "RR_Auction_Intelligence.Report"
            }
        }
    ],
    "settings": {
        "enableAutoRecovery": True
    }
}

with open(PBIP_FILE, "w", encoding="utf-8") as f:
    json.dump(pbip_content, f, indent=2)

# 2. Generate Report definition.pbir
pbir_content = {
    "version": "1.0",
    "datasetReference": {
        "byPath": {
            "path": "../RR_Auction_Intelligence.Dataset"
        },
        "byConnection": None
    }
}

with open(REPORT_DIR / "definition.pbir", "w", encoding="utf-8") as f:
    json.dump(pbir_content, f, indent=2)

# 3. Generate Dataset definition.pbism
pbism_content = {
    "version": "1.0"
}

with open(DATASET_DIR / "definition.pbism", "w", encoding="utf-8") as f:
    json.dump(pbism_content, f, indent=2)

# 4. Parse DAX Measures from dax_measures.dax
dax_path = DASHBOARD_DIR / "dax_measures.dax"
with open(dax_path, "r", encoding="utf-8") as f:
    dax_lines = f.readlines()

current_folder = "General"
measures_by_folder = []
current_measure = None
current_expr_lines = []

for line in dax_lines:
    stripped = line.strip()
    
    # Check section folder
    folder_match = re.match(r'^//\s*(\d+\.\s*[^=]+)$', stripped)
    if folder_match:
        current_folder = folder_match.group(1).strip()
        continue
    
    # Check measure definition
    m_match = re.match(r'^\[([^\]]+)\]\s*=\s*$', stripped)
    if m_match:
        if current_measure:
            measures_by_folder.append({
                "name": current_measure,
                "folder": current_folder,
                "expression": "\n".join(current_expr_lines).strip()
            })
        current_measure = m_match.group(1).strip()
        current_expr_lines = []
        continue
    
    if current_measure is not None:
        if stripped.startswith('// ---') or stripped.startswith('// ==='):
            continue
        current_expr_lines.append(line.rstrip('\r\n'))

if current_measure:
    measures_by_folder.append({
        "name": current_measure,
        "folder": current_folder,
        "expression": "\n".join(current_expr_lines).strip()
    })

print(f"[*] Parsed {len(measures_by_folder)} DAX measures from dax_measures.dax")

# 5. Build Complete Tabular Object Model (model.bim)
bim_measures = []
for m in measures_by_folder:
    bim_measures.append({
        "name": m["name"],
        "expression": m["expression"],
        "displayFolder": m["folder"],
        "description": m.get("description", "")
    })

# Format M Source Path helper
def m_csv_source(filename):
    clean_path = str(DATA_DIR / filename).replace("\\", "/")
    return f'let\n    Source = Csv.Document(File.Contents("{clean_path}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),\n    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\nin\n    Promoted'

# Table schema definitions
tables_def = [
    {
        "name": "DimPlayer",
        "file": "dim_player.csv",
        "columns": [
            {"name": "PlayerID", "dataType": "int64", "isKey": True},
            {"name": "PlayerName", "dataType": "string"},
            {"name": "PrimaryRole", "dataType": "string"},
            {"name": "BattingStyle", "dataType": "string"},
            {"name": "BowlingStyle", "dataType": "string"},
            {"name": "Country", "dataType": "string"},
            {"name": "IsBatterQualified", "dataType": "boolean"},
            {"name": "IsBowlerQualified", "dataType": "boolean"}
        ]
    },
    {
        "name": "DimMatch",
        "file": "dim_match.csv",
        "columns": [
            {"name": "MatchID", "dataType": "int64", "isKey": True},
            {"name": "MatchDate", "dataType": "dateTime"},
            {"name": "CompetitionID", "dataType": "int64"},
            {"name": "CompetitionName", "dataType": "string"},
            {"name": "CompetitionType", "dataType": "string"},
            {"name": "Season", "dataType": "int64"},
            {"name": "Venue", "dataType": "string"},
            {"name": "City", "dataType": "string"},
            {"name": "Team1ID", "dataType": "int64"},
            {"name": "Team2ID", "dataType": "int64"},
            {"name": "TossWinnerID", "dataType": "int64"},
            {"name": "TossDecision", "dataType": "string"},
            {"name": "MatchWinnerID", "dataType": "int64"},
            {"name": "WinMarginRuns", "dataType": "int64"},
            {"name": "WinMarginWickets", "dataType": "int64"}
        ]
    },
    {
        "name": "DimCompetition",
        "file": "dim_competition.csv",
        "columns": [
            {"name": "CompetitionID", "dataType": "int64", "isKey": True},
            {"name": "CompetitionName", "dataType": "string"},
            {"name": "CompetitionType", "dataType": "string"},
            {"name": "Format", "dataType": "string"},
            {"name": "IsSeniorMenT20", "dataType": "boolean"}
        ]
    },
    {
        "name": "DimTeam",
        "file": "dim_team.csv",
        "columns": [
            {"name": "TeamID", "dataType": "int64", "isKey": True},
            {"name": "TeamName", "dataType": "string"},
            {"name": "TeamCode", "dataType": "string"},
            {"name": "IsFranchise", "dataType": "boolean"}
        ]
    },
    {
        "name": "DimContext",
        "file": "dim_context.csv",
        "columns": [
            {"name": "ContextClusterID", "dataType": "int64", "isKey": True},
            {"name": "InningsPhase", "dataType": "string"},
            {"name": "RequiredRunRateTier", "dataType": "string"},
            {"name": "WicketsDownTier", "dataType": "string"},
            {"name": "ExpectedStrikeRate", "dataType": "double"},
            {"name": "ExpectedEconomyRate", "dataType": "double"},
            {"name": "ExpectedBoundaryPct", "dataType": "double"},
            {"name": "ExpectedDotPct", "dataType": "double"},
            {"name": "ExpectedWicketProb", "dataType": "double"}
        ]
    },
    {
        "name": "DimDate",
        "file": "dim_date.csv",
        "columns": [
            {"name": "DateKey", "dataType": "int64", "isKey": True},
            {"name": "Date", "dataType": "dateTime"},
            {"name": "Year", "dataType": "int64"},
            {"name": "Quarter", "dataType": "int64"},
            {"name": "Month", "dataType": "int64"},
            {"name": "MonthName", "dataType": "string"},
            {"name": "DayOfWeek", "dataType": "int64"},
            {"name": "DayName", "dataType": "string"}
        ]
    },
    {
        "name": "DimRanking",
        "file": "dim_ranking.csv",
        "columns": [
            {"name": "RankingID", "dataType": "int64", "isKey": True},
            {"name": "PlayerID", "dataType": "int64"},
            {"name": "Discipline", "dataType": "string"},
            {"name": "OfficialRank", "dataType": "int64"},
            {"name": "CPRIScore", "dataType": "double"},
            {"name": "EvidenceTier", "dataType": "string"},
            {"name": "ConfidenceBand", "dataType": "string"},
            {"name": "RankingExplanation", "dataType": "string"}
        ]
    },
    {
        "name": "FactDeliveryPressure",
        "file": "fact_delivery_pressure.csv",
        "columns": [
            {"name": "DeliveryID", "dataType": "int64", "isKey": True},
            {"name": "MatchID", "dataType": "int64"},
            {"name": "DateKey", "dataType": "int64"},
            {"name": "Innings", "dataType": "int64"},
            {"name": "Over", "dataType": "int64"},
            {"name": "BallNumber", "dataType": "int64"},
            {"name": "StrikerID", "dataType": "int64"},
            {"name": "NonStrikerID", "dataType": "int64"},
            {"name": "BowlerID", "dataType": "int64"},
            {"name": "ContextClusterID", "dataType": "int64"},
            {"name": "RunsBatter", "dataType": "int64"},
            {"name": "ExtrasRuns", "dataType": "int64"},
            {"name": "RunsBowlerTotal", "dataType": "int64"},
            {"name": "IsLegalBatting", "dataType": "boolean"},
            {"name": "IsLegalBowling", "dataType": "boolean"},
            {"name": "IsDotBall", "dataType": "boolean"},
            {"name": "IsBoundary", "dataType": "boolean"},
            {"name": "IsDismissal", "dataType": "boolean"},
            {"name": "PressureIndexBat", "dataType": "double"},
            {"name": "PressureIndexBowl", "dataType": "double"},
            {"name": "IsPressureBatting", "dataType": "boolean"},
            {"name": "IsPressureBowling", "dataType": "boolean"},
            {"name": "WinProbabilityPre", "dataType": "double"},
            {"name": "WinProbabilityAdded", "dataType": "double"}
        ]
    },
    {
        "name": "FactPlayerMatchPerformance",
        "file": "fact_player_match_performance.csv",
        "columns": [
            {"name": "PlayerMatchID", "dataType": "int64", "isKey": True},
            {"name": "PlayerID", "dataType": "int64"},
            {"name": "MatchID", "dataType": "int64"},
            {"name": "CompetitionID", "dataType": "int64"},
            {"name": "RunsScoredTotal", "dataType": "int64"},
            {"name": "BallsFacedTotal", "dataType": "int64"},
            {"name": "PressureRunsScored", "dataType": "int64"},
            {"name": "PressureBallsFaced", "dataType": "int64"},
            {"name": "PressureStrikeRate", "dataType": "double"},
            {"name": "WicketsTakenTotal", "dataType": "int64"},
            {"name": "OversBowledTotal", "dataType": "double"},
            {"name": "RunsConcededTotal", "dataType": "int64"},
            {"name": "PressureBallsBowled", "dataType": "int64"},
            {"name": "PressureRunsConceded", "dataType": "int64"},
            {"name": "PressureEconomyRate", "dataType": "double"}
        ]
    },
    {
        "name": "FactPlayerPressurePerformance",
        "file": "fact_player_pressure_performance.csv",
        "columns": [
            {"name": "PlayerPressureID", "dataType": "int64", "isKey": True},
            {"name": "PlayerID", "dataType": "int64"},
            {"name": "CompetitionID", "dataType": "int64"},
            {"name": "RankingID", "dataType": "int64"},
            {"name": "TotalBallsFaced", "dataType": "int64"},
            {"name": "TotalRunsScored", "dataType": "int64"},
            {"name": "NormalStrikeRate", "dataType": "double"},
            {"name": "PressureBallsFaced", "dataType": "int64"},
            {"name": "PressureRunsScored", "dataType": "int64"},
            {"name": "PressureStrikeRate", "dataType": "double"},
            {"name": "DeltaStrikeRate", "dataType": "double"},
            {"name": "BayesianShrunkStrikeRate", "dataType": "double"},
            {"name": "BayesianCILower", "dataType": "double"},
            {"name": "BayesianCIUpper", "dataType": "double"},
            {"name": "TotalBallsBowled", "dataType": "int64"},
            {"name": "TotalRunsConceded", "dataType": "int64"},
            {"name": "NormalEconomyRate", "dataType": "double"},
            {"name": "PressureBallsBowled", "dataType": "int64"},
            {"name": "PressureRunsConceded", "dataType": "int64"},
            {"name": "PressureEconomyRate", "dataType": "double"},
            {"name": "DeltaEconomyRate", "dataType": "double"},
            {"name": "BayesianShrunkEconomy", "dataType": "double"},
            {"name": "MatchConsistencyCV", "dataType": "double"},
            {"name": "JackknifeWorstCaseMetric", "dataType": "double"},
            {"name": "JackknifeMaxRankDrop", "dataType": "int64"}
        ]
    }
]

# Create _Measures table
measures_table = {
    "name": "_Measures",
    "columns": [
        {
            "name": "RowKey",
            "dataType": "int64",
            "isHidden": True
        }
    ],
    "partitions": [
        {
            "name": "_Measures-Partition",
            "mode": "import",
            "source": {
                "type": "m",
                "expression": 'let\n    Source = #table({"RowKey"}, {{1}})\nin\n    Source'
            }
        }
    ],
    "measures": bim_measures
}

model_tables = [measures_table]

for td in tables_def:
    t_obj = {
        "name": td["name"],
        "columns": td["columns"],
        "partitions": [
            {
                "name": f"{td['name']}-Partition",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": m_csv_source(td["file"])
                }
            }
        ]
    }
    model_tables.append(t_obj)

# Build Relationships
model_relationships = [
    # FactDeliveryPressure
    {
        "name": "Rel_Match_Delivery",
        "fromTable": "FactDeliveryPressure",
        "fromColumn": "MatchID",
        "toTable": "DimMatch",
        "toColumn": "MatchID",
        "isActive": True
    },
    {
        "name": "Rel_Striker_Delivery",
        "fromTable": "FactDeliveryPressure",
        "fromColumn": "StrikerID",
        "toTable": "DimPlayer",
        "toColumn": "PlayerID",
        "isActive": True
    },
    {
        "name": "Rel_Bowler_Delivery_InactiveRolePlaying",
        "fromTable": "FactDeliveryPressure",
        "fromColumn": "BowlerID",
        "toTable": "DimPlayer",
        "toColumn": "PlayerID",
        "isActive": False
    },
    {
        "name": "Rel_Context_Delivery",
        "fromTable": "FactDeliveryPressure",
        "fromColumn": "ContextClusterID",
        "toTable": "DimContext",
        "toColumn": "ContextClusterID",
        "isActive": True
    },
    {
        "name": "Rel_Date_Delivery",
        "fromTable": "FactDeliveryPressure",
        "fromColumn": "DateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "isActive": True
    },
    # FactPlayerPressurePerformance
    {
        "name": "Rel_Player_PressurePerf",
        "fromTable": "FactPlayerPressurePerformance",
        "fromColumn": "PlayerID",
        "toTable": "DimPlayer",
        "toColumn": "PlayerID",
        "isActive": True
    },
    {
        "name": "Rel_Comp_PressurePerf",
        "fromTable": "FactPlayerPressurePerformance",
        "fromColumn": "CompetitionID",
        "toTable": "DimCompetition",
        "toColumn": "CompetitionID",
        "isActive": True
    },
    {
        "name": "Rel_Ranking_PressurePerf",
        "fromTable": "FactPlayerPressurePerformance",
        "fromColumn": "RankingID",
        "toTable": "DimRanking",
        "toColumn": "RankingID",
        "isActive": True
    },
    # FactPlayerMatchPerformance
    {
        "name": "Rel_Player_MatchPerf",
        "fromTable": "FactPlayerMatchPerformance",
        "fromColumn": "PlayerID",
        "toTable": "DimPlayer",
        "toColumn": "PlayerID",
        "isActive": True
    },
    {
        "name": "Rel_Match_MatchPerf",
        "fromTable": "FactPlayerMatchPerformance",
        "fromColumn": "MatchID",
        "toTable": "DimMatch",
        "toColumn": "MatchID",
        "isActive": True
    }
]

model_bim = {
    "name": "RR_Auction_Intelligence_2027",
    "compatibilityLevel": 1567,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {
            "legacyRedirects": True,
            "returnErrorValuesAsNull": True
        },
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "tables": model_tables,
        "relationships": model_relationships,
        "annotations": [
            {
                "name": "PBI_QueryOrder",
                "value": json.dumps(["_Measures"] + [td["name"] for td in tables_def])
            }
        ]
    }
}

with open(DATASET_DIR / "model.bim", "w", encoding="utf-8") as f:
    json.dump(model_bim, f, indent=2)

print(f"[+] Successfully generated Power BI Project file: {PBIP_FILE}")
print(f"[+] Successfully generated Report definition: {REPORT_DIR / 'definition.pbir'}")
print(f"[+] Successfully generated Dataset definition: {DATASET_DIR / 'definition.pbism'}")
print(f"[+] Successfully generated Tabular Object Model: {DATASET_DIR / 'model.bim'} ({os.path.getsize(DATASET_DIR / 'model.bim'):,} bytes)")
