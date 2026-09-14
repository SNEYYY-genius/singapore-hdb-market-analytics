-- Singapore HDB Resale Market Intelligence
-- 04: Growth Analysis
-- Purpose: Calculate town-level annual growth without treating partial years
--          as comparable with complete years.

WITH annual_town_stats AS (
    SELECT
        town,
        year,
        COUNT(*) AS transactions,
        COUNT(DISTINCT month) AS months_present,
        MEDIAN(price_per_sqm) AS median_price_per_sqm
    FROM resale_transactions
    GROUP BY town, year
),

with_previous_year AS (
    SELECT
        town,
        year,
        transactions,
        months_present,
        median_price_per_sqm,
        LAG(transactions) OVER (
            PARTITION BY town ORDER BY year
        ) AS previous_year_transactions,
        LAG(months_present) OVER (
            PARTITION BY town ORDER BY year
        ) AS previous_year_months_present,
        LAG(median_price_per_sqm) OVER (
            PARTITION BY town ORDER BY year
        ) AS previous_year_price_per_sqm
    FROM annual_town_stats
)

SELECT
    town,
    year,
    transactions,
    months_present,
    ROUND(median_price_per_sqm, 2) AS median_price_per_sqm,
    CASE
        WHEN months_present = 12 AND previous_year_months_present = 12
        THEN ROUND(
            100.0 * (transactions - previous_year_transactions)
            / NULLIF(previous_year_transactions, 0),
            2
        )
    END AS transaction_growth_pct,
    CASE
        WHEN months_present = 12 AND previous_year_months_present = 12
        THEN ROUND(
            100.0 * (median_price_per_sqm - previous_year_price_per_sqm)
            / NULLIF(previous_year_price_per_sqm, 0),
            2
        )
    END AS price_growth_pct,
    CASE
        WHEN months_present = 12 AND previous_year_months_present = 12
        THEN 'Comparable full years'
        ELSE 'Not comparable: partial or missing year'
    END AS comparison_status
FROM with_previous_year
ORDER BY town, year;
