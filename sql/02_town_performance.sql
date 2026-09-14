-- Singapore HDB Resale Market Intelligence
-- 02: Town Performance
-- Purpose: Compare HDB resale activity and pricing across towns


SELECT
    town,
    COUNT(*) AS transactions,
    ROUND(MEDIAN(resale_price), 0) AS median_resale_price,
    ROUND(MEDIAN(price_per_sqm), 2) AS median_price_per_sqm,
    ROUND(SUM(resale_price), 0) AS total_transaction_value
FROM resale_transactions
GROUP BY town
ORDER BY transactions DESC;

SELECT
    town,
    COUNT(*) AS transactions,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share_pct,
    ROUND(MEDIAN(resale_price), 0) AS median_resale_price,
    ROUND(MEDIAN(price_per_sqm), 2) AS median_price_per_sqm,
    ROUND(SUM(resale_price), 0) AS total_transaction_value
FROM resale_transactions
GROUP BY town
ORDER BY transactions DESC;