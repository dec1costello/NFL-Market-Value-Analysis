{{ config(materialized='table') }}

WITH qb_contracts AS (
    SELECT * FROM {{ ref('contracts') }}
    WHERE position = 'QB'
)

SELECT
    rank,
    player_name,
    team_signed_with,
    age_at_signing,
    start_year,
    end_year,
    years,
    total_value,
    average_salary,
    avg_percent_of_cap,
    signing_bonus,
    guarantee_at_signing,
    practical_guarantee,
    two_year_cash_total,
    three_year_cash_total,
    -- Calculate guaranteed percentage
    ROUND(guarantee_at_signing / total_value * 100, 2) AS pct_guaranteed_at_signing,
    ROUND(practical_guarantee / total_value * 100, 2) AS pct_practical_guarantee,
    -- Calculate cash flow ratios
    ROUND(two_year_cash_total / total_value * 100, 2) AS pct_paid_in_2_years,
    ROUND(three_year_cash_total / total_value * 100, 2) AS pct_paid_in_3_years
FROM qb_contracts
ORDER BY rank