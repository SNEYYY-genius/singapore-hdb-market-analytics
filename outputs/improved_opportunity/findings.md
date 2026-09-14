# Singapore HDB Resale Market — Final Opportunity Findings

This is the final screen for the fixed January 2017–August 2026 snapshot. The earlier [exploratory report](../../reports/findings.md) uses a different period and classification method.

## Executive result

The market recorded 17,263 transactions in January-August 2026, -3.5% versus the same months of 2025.
The stricter screen retained 70 adequately sampled segments and classified 2 as Priority and 1 as Emerging.

Priority requires at least 202 current-period transactions (the eligible-segment median), at least 5% transaction growth, a 95% count-growth interval above zero, and non-negative composition-adjusted price growth. Emerging applies below the same size threshold and requires at least 10% transaction growth, with the same uncertainty and adjusted-price criteria.

## Current shortlist

| Category | Segment | 2026 YTD transactions | Volume growth | 95% interval | Adjusted price growth | 95% interval | Three-year volume CAGR |
|---|---|---:|---:|---:|---:|---:|---:|
| Priority | Punggol × 4 Room | 615 | 13.7% | 1.3% to 27.6% | 0.3% | -0.4% to 1.0% | -6.1% |
| Priority | Pasir Ris × 4 Room | 223 | 36.8% | 11.8% to 67.4% | 0.4% | -0.8% to 1.6% | 6.2% |
| Emerging | Pasir Ris × Executive | 133 | 35.7% | 4.5% to 76.2% | 0.9% | -0.8% to 2.7% | 11.5% |

## What changed from the original method

- The comparison is January-August 2026 versus January-August 2025, using the latest matched-month window in the fixed snapshot.
- Eligibility uses at least 500 transactions known by August 2025 and at least 50 transactions in each comparison period.
- Material volume growth is at least 5%; statistical support requires the approximate 95% rate-ratio interval to stay above zero.
- Adjusted price growth comes from a segment-level log-price-per-sqm regression controlling for floor area, remaining lease, storey, flat model and calendar month, with HC3 robust standard errors.
- Adjusted-price models with undefined robust uncertainty are marked unavailable in the CSV and cannot qualify for Priority or Emerging.
- Count intervals are per-segment approximations; they do not correct for testing multiple segments. A non-negative adjusted price point estimate does not establish statistically significant price growth.
- Composition flags identify material shifts in median lease, storey, area or flat-model shares.
- Historical eligibility stops before the current period, preventing future-data leakage.

## Historical validation

The backtest formed signals using January-August 2024 versus the same months of 2023 and measured what happened in January-August 2025. It covered 71 eligible segments, including 14 Priority segments.

- Median subsequent volume growth for Priority: -14.5%
- Median subsequent volume growth for other eligible segments: -11.1%
- Priority segments with positive subsequent growth: 21.4%
- All eligible segments with positive subsequent growth: 26.8%
- Spearman correlation between signal-year and subsequent growth: -0.37 (p=0.002)

The stricter signal did not show forward separation in this single backtest.

The Spearman p-value uses SciPy's asymptotic calculation. Adjacent growth rates share the middle year, which can itself induce negative correlation; this result does not establish a reversal mechanism. A single backtest is evidence, not proof. The category remains a commercial research screen rather than an investment-return forecast.

## Remaining data gap

The transaction file cannot distinguish buyer demand from flats available for sale. Listing inventory, days on market, asking-to-sale discount, MRT distance and amenity data are not present. Those variables should be added before interpreting transaction growth as demand or estimating lead-generation potential.

## Data-quality checks

- Source rows: 239,330
- Coverage: January 2017 to August 2026
- Missing values in required analytical columns: 0
- Exact duplicate rows retained in source: 318
- Identical published rows are retained because there is no unique transaction identifier to establish that they represent duplicate sales.

Source: Housing & Development Board, [Resale flat prices based on registration date from Jan-2017 onwards](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view), under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence). See [data provenance](../../data/README.md).
