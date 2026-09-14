-- Singapore HDB Resale Market Intelligence
-- 03: Segment Analysis
-- Purpose: Compare HDB resale performance across Town × Flat Type segments

SELECT
    town,
    flat_type,
    COUNT(*) AS transactions,
    ROUND(MEDIAN(resale_price), 0) AS median_resale_price,
    ROUND(MEDIAN(price_per_sqm), 2) AS median_price_per_sqm,
    ROUND(SUM(resale_price), 0) AS total_transaction_value
FROM resale_transactions
GROUP BY town, flat_type
ORDER BY transactions DESC;

SELECT
    town,
    flat_type,
    COUNT(*) AS transactions,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY town),
        2
    ) AS town_transaction_share_pct,
    ROUND(MEDIAN(resale_price), 0) AS median_resale_price,
    ROUND(MEDIAN(price_per_sqm), 2) AS median_price_per_sqm
FROM resale_transactions
GROUP BY town, flat_type
ORDER BY town, transactions DESC;