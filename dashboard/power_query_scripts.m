// ==============================================================================
// RR AUCTION INTELLIGENCE 2027 — POWER QUERY M-SCRIPTS
// Phase 04: Production Ingestion Pipeline
// Instructions: In Power BI Desktop, open 'Advanced Editor' for each query
//               and paste the corresponding M-code below.
// Base Directory: d:\RR_PRESSURE_INDEX_2027\outputs\dashboard\
// ==============================================================================

// ------------------------------------------------------------------------------
// PARAMETER: BaseSourceFolder
// ------------------------------------------------------------------------------
let
    BaseSourceFolder = "d:\RR_PRESSURE_INDEX_2027\outputs\dashboard\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    BaseSourceFolder

// ------------------------------------------------------------------------------
// 1. DimPlayer
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_player.csv"), [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"PlayerID", Int64.Type},
        {"PlayerName", type text},
        {"PrimaryDiscipline", type text},
        {"IsDualDiscipline", Int64.Type},
        {"BattingConfidenceTier", type text},
        {"BowlingConfidenceTier", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 2. DimCompetition
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_competition.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"CompID", Int64.Type},
        {"CompName", type text},
        {"MatchFormat", type text},
        {"Season", type text},
        {"CompetitionType", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 3. DimTeam
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_team.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"TeamID", Int64.Type},
        {"TeamName", type text},
        {"TeamCode", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 4. DimDate
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_date.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DateKey", Int64.Type},
        {"Date", type date},
        {"Year", Int64.Type},
        {"Month", Int64.Type},
        {"MonthName", type text},
        {"Quarter", type text},
        {"DayOfWeek", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 5. DimMatch
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_match.csv"), [Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"MatchID", Int64.Type},
        {"CompID", Int64.Type},
        {"DateKey", Int64.Type},
        {"MatchDate", type text},
        {"Stage", type text},
        {"IsKnockOut", Int64.Type},
        {"HomeTeamID", Int64.Type},
        {"AwayTeamID", Int64.Type},
        {"WinTeamID", Int64.Type},
        {"Result", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 6. DimContext
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_context.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"ContextID", Int64.Type},
        {"ContextName", type text},
        {"Innings", Int64.Type},
        {"PhaseName", type text},
        {"IsBatPressure", Int64.Type},
        {"IsBowlLeverage", Int64.Type},
        {"Description", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 7. DimRanking
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "dim_ranking.csv"), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"RankingID", Int64.Type},
        {"PlayerID", Int64.Type},
        {"PlayerName", type text},
        {"Discipline", type text},
        {"OfficialRank", Int64.Type},
        {"CPRI", type number},
        {"CPRI_CI_Low", type number},
        {"CPRI_CI_High", type number},
        {"ConfidenceClass", type text},
        {"OverallEvidenceTier", type text},
        {"RankingExplanation", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 8. FactDeliveryPressure
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "fact_delivery_pressure.csv"), [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DeliveryID", Int64.Type},
        {"MatchID", Int64.Type},
        {"Innings", Int64.Type},
        {"OverID", Int64.Type},
        {"StrikerID", Int64.Type},
        {"BowlerID", Int64.Type},
        {"BattingTeamID", Int64.Type},
        {"BowlingTeamID", Int64.Type},
        {"ContextID", Int64.Type},
        {"RunsBat", Int64.Type},
        {"BowlerRunsConceded", Int64.Type},
        {"IsFour", Int64.Type},
        {"IsSix", Int64.Type},
        {"IsWicket", Int64.Type},
        {"IsBowlerWicket", Int64.Type},
        {"IsLegalBatting", Int64.Type},
        {"IsLegalBowling", Int64.Type},
        {"IsBatPressure", Int64.Type},
        {"IsBowlLeverage", Int64.Type},
        {"PsiBat", type number},
        {"LambdaBowl", type number}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 9. FactPlayerMatchPerformance
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "fact_player_match_performance.csv"), [Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"PlayerMatchID", Int64.Type},
        {"MatchID", Int64.Type},
        {"PlayerID", Int64.Type},
        {"TeamID", Int64.Type},
        {"Discipline", type text},
        {"IsPressureState", Int64.Type},
        {"Balls", Int64.Type},
        {"Runs", Int64.Type},
        {"Outs", Int64.Type},
        {"Boundaries", Int64.Type},
        {"Dots", Int64.Type},
        {"RateMetric", type number}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 10. FactPlayerPressurePerformance
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(BaseSourceFolder & "fact_player_pressure_performance.csv"), [Delimiter=",", Columns=19, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"PlayerPressurePerfID", Int64.Type},
        {"PlayerID", Int64.Type},
        {"Discipline", type text},
        {"PressureBalls", Int64.Type},
        {"NormalBalls", Int64.Type},
        {"RawPressureMetric", type number},
        {"NormalBaselineMetric", type number},
        {"DeltaContextMetric", type number},
        {"BayesEstimate", type number},
        {"Bayes_CI_Low", type number},
        {"Bayes_CI_High", type number},
        {"Bayes_CI_Width", type number},
        {"BoundaryPct", type number},
        {"DotPct", type number},
        {"DismissalOrWktRate", type number},
        {"MatchCV", type number},
        {"MatchSuccessRate", type number},
        {"JackknifeWorstCaseMetric", type number},
        {"JackknifeSE", type number}
    })
in
    #"Changed Type"

