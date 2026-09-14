# Singapore HDB Resale Market Analytics

An end-to-end analysis of **239,330 HDB resale transactions from January 2017 to August 2026**, using Python, SQL, DuckDB, and regression analysis to examine market trends, price drivers, and Town × Flat Type segments for further commercial research.

## Start here

- [Final opportunity findings](outputs/improved_opportunity/findings.md): the current segment screen, uncertainty estimates, and historical validation.
- [Exploratory findings](reports/findings.md): market overview, price drivers, regression results, and the earlier 2024–2025 opportunity matrix.
- [Data provenance](data/README.md): source, snapshot coverage, cleaning decisions, and licence.

## Main findings

January–August 2026 recorded **17,263 transactions**, 3.5% fewer than the same months of 2025. The final screen identifies:

| Category | Segment | 2026 YTD transactions | Volume growth | Adjusted price growth |
|---|---|---:|---:|---:|
| Priority | Punggol × 4 Room | 615 | 13.7% | 0.3% |
| Priority | Pasir Ris × 4 Room | 223 | 36.8% | 0.4% |
| Emerging | Pasir Ris × Executive | 133 | 35.7% | 0.9% |

These categories describe observed activity, not a forecast. In one historical test, Priority segments selected using 2023–2024 momentum subsequently declined 14.5% at the median, compared with an 11.1% decline among other eligible segments. The screen did not demonstrate forward separation in that test.

The broader exploratory analysis finds that floor area, remaining lease, storey, town, flat type, and transaction year explain approximately 90.7% of the in-sample variation in log resale prices. These are conditional associations, not causal effects or out-of-sample predictive accuracy.

## Method

The final screen compares January–August 2026 with January–August 2025 and retains 70 segments with at least 500 transactions known by August 2025 and at least 50 in each comparison period.

- **Priority:** at least 202 current-period transactions (the eligible-segment median), at least 5% volume growth, an approximate 95% count-growth interval above zero, and non-negative adjusted price growth.
- **Emerging:** below the same size threshold, at least 10% volume growth, and the same uncertainty and adjusted-price requirements.
- **Price adjustment:** segment-level log-price-per-sqm regressions control for floor area, remaining lease, storey, flat model, and calendar month, using HC3 robust standard errors. Unavailable estimates cannot qualify for Priority or Emerging.
- **Composition checks:** flag changes in lease, storey, area, and flat-model shares, including new or disappearing models.
- **Backtest:** apply the screen to January–August 2023 and 2024, then measure activity in the same months of 2025 without using future data to form the signal.

The [full segment table](outputs/improved_opportunity/segment_screen_2026_ytd.csv) includes other categories and excluded segments. The earlier notebook matrix uses different criteria and full-year 2024–2025 data; its nine Priority segments should not be confused with the final shortlist above.

## Reproduce the analysis

Tested with Python 3.10. Create a virtual environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell.

The raw snapshot and cleaned dataset are included. Regenerate the final outputs and run the checks:

```bash
python src/hdb_analysis/opportunity.py
python -W error::RuntimeWarning -m unittest discover -s tests -v
```

The analysis writes `segment_screen_2026_ytd.csv`, `backtest_detail.csv`, `backtest_summary.json`, and `findings.md` to `outputs/improved_opportunity/`. Its dates are deliberately fixed to the published snapshot; replacing the data with a newer file does not automatically advance the analysis window.

For the complete exploratory workflow, launch `jupyter lab` and run notebooks 01–08 in order, executing each from top to bottom. Notebook 02 rebuilds the cleaned dataset, notebook 03 creates the local DuckDB database, notebook 07 writes segment tables, and notebook 08 writes exploratory opportunity tables and the chart. The final screen is regenerated separately with the command above. No Tableau setup is required.

## Repository structure

```text
README.md                         Project overview and reproduction guide
requirements.txt                  Pinned direct Python dependencies
LICENSE                           MIT licence for project code
data/
  README.md                       Data provenance and licence
  raw/hdb_resale_raw.csv           Fixed source snapshot
  processed/hdb_resale_clean.csv   Cleaned transaction-level data
notebooks/                        Exploratory workflow, numbered 01–08
sql/                              Four reusable DuckDB query files
src/hdb_analysis/                 Final opportunity analysis and backtest
tests/                            Automated data, analysis, and SQL checks
reports/findings.md               Exploratory findings
outputs/
  hdb_*.csv                       Exploratory analytical tables
  improved_opportunity/           Final screen, backtest, and generated report
charts/hdb_opportunity_matrix.png  Exploratory 2025 opportunity matrix
```

`database/hdb.duckdb` is generated locally by notebook 03 and excluded from Git. The virtual environment, caches, and operating-system files are also excluded. Regenerating the analysis may update the tracked output files.

## Validation

The 12 automated checks cover required data fields, reconciled transaction counts, shortlist reproduction, backtest results, disappearing segments, missing comparison months, flat-model mix changes, date labels, and SQL comparisons of consecutive complete years. All eight notebooks have also been executed from top to bottom against the included snapshot.

## Interpretation limits

Completed transactions do not measure listing inventory or buyer enquiries. Growth may reflect changes in homes available for sale, and median price changes may reflect the mix of flats sold. Listing inventory, days on market, asking-to-sale discounts, and location features would be needed for a broader commercial demand model.

Count-growth intervals are approximate and apply to individual segments without a multiple-testing correction. A non-negative adjusted-price point estimate does not establish significant price growth; consult the report's confidence intervals. The backtest's Spearman p-value uses SciPy's asymptotic calculation, and adjacent growth rates share a middle year that can induce negative correlation. A single backtest cannot establish general predictive performance.

## Data attribution and licence

Contains information from HDB's [Resale flat prices based on registration date from Jan-2017 onwards](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view), published on data.gov.sg under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence). The fixed local snapshot covers January 2017–August 2026; its original download date was not recorded. See [data provenance](data/README.md) for details.

Project code is available under the [MIT Licence](LICENSE). This is an independent project and does not imply endorsement by HDB.
