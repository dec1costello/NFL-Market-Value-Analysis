{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM read_csv_auto('{{ var("data_path", "../data/raw/NFL_Contracts.csv") }}', 
                                 header=False, 
                                 skip=2,
                                 delim=',',
                                 -- Name the columns explicitly to avoid confusion
                                 columns={
                                     'column00': 'VARCHAR',
                                     'column01': 'VARCHAR', 
                                     'column02': 'VARCHAR',
                                     'column03': 'VARCHAR',
                                     'column04': 'VARCHAR',
                                     'column05': 'VARCHAR',
                                     'column06': 'VARCHAR',
                                     'column07': 'VARCHAR',
                                     'column08': 'VARCHAR',
                                     'column09': 'VARCHAR',
                                     'column010': 'VARCHAR',
                                     'column011': 'VARCHAR',
                                     'column012': 'VARCHAR',
                                     'column013': 'VARCHAR',
                                     'column014': 'VARCHAR',
                                     'column015': 'VARCHAR'
                                 })
)

SELECT
    column00 AS rank,
    column01 AS player_name,
    column02 AS position,
    TRIM(column03) AS team_signed_with,
    TRY_CAST(column04 AS INTEGER) AS age_at_signing,
    TRY_CAST(column05 AS INTEGER) AS start_year,
    TRY_CAST(column06 AS INTEGER) AS end_year,
    TRY_CAST(column07 AS INTEGER) AS years,
    TRY_CAST(REPLACE(REPLACE(column08, '$', ''), ',', '') AS DECIMAL(18,2)) AS total_value,
    TRY_CAST(REPLACE(REPLACE(column09, '$', ''), ',', '') AS DECIMAL(18,2)) AS average_salary,
    TRY_CAST(REPLACE(column010, '%', '') AS DECIMAL(5,2)) / 100 AS avg_percent_of_cap,
    TRY_CAST(REPLACE(REPLACE(column011, '$', ''), ',', '') AS DECIMAL(18,2)) AS signing_bonus,
    TRY_CAST(REPLACE(REPLACE(column012, '$', ''), ',', '') AS DECIMAL(18,2)) AS guarantee_at_signing,
    TRY_CAST(REPLACE(REPLACE(column013, '$', ''), ',', '') AS DECIMAL(18,2)) AS practical_guarantee,
    TRY_CAST(REPLACE(REPLACE(column014, '$', ''), ',', '') AS DECIMAL(18,2)) AS two_year_cash_total,
    TRY_CAST(REPLACE(REPLACE(column015, '$', ''), ',', '') AS DECIMAL(18,2)) AS three_year_cash_total
FROM source
WHERE column01 IS NOT NULL 
  AND column01 != 'Player'