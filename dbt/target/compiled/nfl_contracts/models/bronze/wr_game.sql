

WITH source AS (
    -- Read all game-level WR data from 2021-2025 (including week folders)
    SELECT * FROM read_csv_auto(
            '../data/raw/*/*/WR.csv',
            header=true,
            filename=true,
            hive_partitioning=true
        )
)

SELECT
    filename as source_file,
    
    -- Extract season and week from path
    REGEXP_EXTRACT(filename, '.*/(\\d{4})/\\d+/(.*)', 1) as season_year,
    REGEXP_EXTRACT(filename, '.*/\\d{4}/(\\d+)/.*', 1) as week_number,
    
    -- Player info
    TRIM(PlayerName) as player_name,
    TRIM(CAST(PlayerId AS VARCHAR)) as player_id,  -- Fixed: cast to string before trim
    TRIM(Pos) as position,
    TRIM(Team) as team,
    TRIM(PlayerOpponent) as opponent,
    
    -- Passing stats
    TRY_CAST(PassingYDS AS INTEGER) as passing_yards,
    TRY_CAST(PassingTD AS INTEGER) as passing_td,
    TRY_CAST(PassingInt AS INTEGER) as passing_int,
    
    -- Rushing stats
    TRY_CAST(RushingYDS AS INTEGER) as rushing_yards,
    TRY_CAST(RushingTD AS INTEGER) as rushing_td,
    
    -- Receiving stats
    TRY_CAST(ReceivingRec AS INTEGER) as receptions,
    TRY_CAST(ReceivingYDS AS INTEGER) as receiving_yards,
    TRY_CAST(ReceivingTD AS INTEGER) as receiving_td,
    
    -- Other stats
    TRY_CAST(RetTD AS INTEGER) as return_td,
    TRY_CAST(FumTD AS INTEGER) as fumble_return_td,
    TRY_CAST("2PT" AS INTEGER) as two_point_conversions,
    TRY_CAST(Fum AS INTEGER) as fumbles,
    TRY_CAST("FanPtsAgainst-pts" AS DOUBLE) as fantasy_points_against,
    
    -- Touches
    TRY_CAST(TouchCarries AS INTEGER) as carries,
    TRY_CAST(TouchReceptions AS INTEGER) as touch_receptions,
    TRY_CAST(Touches AS INTEGER) as total_touches,
    TRY_CAST(TargetsReceptions AS INTEGER) as targets_receptions,
    TRY_CAST(Targets AS INTEGER) as targets,
    TRY_CAST(ReceptionPercentage AS DOUBLE) as reception_pct,
    
    -- Red zone
    TRY_CAST(RzTarget AS INTEGER) as red_zone_targets,
    TRY_CAST(RzTouch AS INTEGER) as red_zone_touches,
    TRY_CAST(RzG2G AS INTEGER) as red_zone_goal_to_go,
    
    -- Rankings
    TRY_CAST(Rank AS INTEGER) as rank,
    TRY_CAST(TotalPoints AS DOUBLE) as total_points,
    
    -- Add ingestion timestamp
    CURRENT_TIMESTAMP as ingested_at
    
FROM source
WHERE position = 'WR'
  AND player_name IS NOT NULL
  AND player_name != 'PlayerName'  -- Filter out potential header rows