# Singapore HDB Resale Market Analytics

An end-to-end analysis of 239,330 HDB resale transactions from January 2017 to August 2026. The project examines market trends, price drivers, and Town × Flat Type segments that may warrant commercial attention for a property marketplace or property-services business.

The raw data is an August 2026 snapshot of HDB's [Resale flat prices based on registration date from Jan-2017 onwards](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view) dataset on data.gov.sg. The snapshot is kept fixed so the published results remain reproducible even as the official dataset receives newer transactions.

## Questions answered

1. How have HDB resale transaction activity and prices changed?
2. Which towns and flat segments represent the largest markets?
3. Which observed property characteristics are associated with resale prices?
4. Which segments show current, statistically supported transaction momentum?
5. Does recent segment momentum predict the following year's activity?

## Current result

January–August 2026 recorded 17,263 transactions, 3.5% fewer than the same months of 2025.

The improved screen compares matched months, prevents future-data leakage, requires material growth, tests count uncertainty, and adjusts price changes for the mix of flats sold. It identifies:

| Category | Segment | 2026 YTD transactions | Volume growth | Adjusted price growth |
|---|---|---:|---:|---:|
| Priority | Punggol × 4 Room | 615 | 13.7% | 0.3% |
| Priority | Pasir Ris × 4 Room | 223 | 36.8% | 0.4% |
| Emerging | Pasir Ris × Executive | 133 | 35.7% | 0.9% |

These labels describe current market activity. They are not forecasts or investment recommendations. A historical test found no forward persistence: segments classified as Priority from 2023–2024 momentum subsequently declined 14.5% at the median, compared with an 11.1% decline among other eligible segments.

## Improved opportunity method

- Compare January–August 2026 with January–August 2025, avoiding full-year versus partial-year distortion.
- Require at least 500 historical transactions known by August 2025 and 50 transactions in each comparison period.
- Treat transaction growth as material at 5% or more.
- Require an approximate 95% count-growth interval above zero for Priority and Emerging segments.
- Estimate composition-adjusted price growth within each segment, controlling for floor area, remaining lease, storey, flat model, and calendar month.
- Flag large changes in the composition of flats sold.
- Backtest the classification using only information available when each signal would have been formed.

Run the reproducible analysis from the repository root:

```bash
.venv/bin/python src/hdb_analysis/opportunity.py
```

Generated files are written to `outputs/improved_opportunity/`:

- `segment_screen_2026_ytd.csv`
- `backtest_detail.csv`
- `backtest_summary.json`
- `findings.md`

## Setup

Python 3.10 or newer is recommended. Create and activate a virtual environment, then install the direct dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The repository includes the raw snapshot and the cleaned dataset used for the published results. To rebuild the cleaned file, run `notebooks/02_data_cleaning.ipynb`; to reproduce the full exploratory workflow, run notebooks 01 through 08 in order. The improved, tested opportunity screen is the final result and can be regenerated independently with the command above.

## Validation

Run the automated data, analysis, backtest, and SQL checks:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests verify that:

- required fields are present and valid;
- segment totals reconcile with the transaction file;
- the current shortlist is reproducible;
- the backtest conclusion is not accidentally reversed; and
- every SQL file executes successfully in DuckDB.

## Repository structure

```text
data/                 Raw and processed transaction data
notebooks/            Audit, cleaning, exploration, and regression notebooks
reports/              Exploratory findings from the notebook workflow
sql/                  Reusable DuckDB queries
src/hdb_analysis/     Reproducible opportunity analysis
tests/                Automated project checks
outputs/              Generated analytical tables and reports
charts/               Generated figures
```

The authoritative final opportunity conclusions are in `outputs/improved_opportunity/findings.md`. The material under `reports/` documents the earlier exploratory workflow and is retained for analysis traceability.

## Interpretation limits

The dataset contains completed transactions, not listings or buyer enquiries. Transaction growth may reflect more homes becoming available rather than stronger buyer demand. A commercial demand model would additionally need listing inventory, days on market, asking-to-sale discounts, lead or enquiry data, and location features such as MRT and amenity access.

Regression coefficients represent conditional associations, not causal effects. The segment screen should support further research rather than predict returns, revenue, or profitability.
