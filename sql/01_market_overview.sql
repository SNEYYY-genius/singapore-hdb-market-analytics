-- Singapore HDB Resale Market Intelligence
-- 01: Market Overview
-- Purpose: Establish headline KPIs for the HDB resale market

-- Q1: How many transactions are there?

SELECT COUNT(*) AS total_transactions
FROM resale_transactions;

-- Q2: What is the total transaction value?

SELECT
    SUM(resale_price) AS total_transaction_value
FROM resale_transactions;

-- Q3: What is the median resale price?

SELECT
    MEDIAN(resale_price) AS median_resale_price
FROM resale_transactions;

-- Q4: What is the median price per square metre?

SELECT
    ROUND(MEDIAN(price_per_sqm), 2) AS median_price_per_sqm
FROM resale_transactions;

-- Q5: How many towns are represented?

SELECT
    COUNT(DISTINCT town) AS number_of_towns
FROM resale_transactions;

-- Q6: How many transactions occur each year?

SELECT
    year,
    COUNT(*) AS total_transactions
FROM resale_transactions
GROUP BY year
ORDER BY year;