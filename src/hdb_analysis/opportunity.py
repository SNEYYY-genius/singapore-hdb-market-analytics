"""Improved HDB resale segment screening without Tableau.

The script reads the project's cleaned transaction file and produces:
  * a current Jan-Aug 2026 versus Jan-Aug 2025 segment screen;
  * composition-adjusted price changes with robust confidence intervals;
  * a leakage-free historical signal backtest; and
  * a concise findings report and machine-readable CSV outputs.

It intentionally does not modify the source dataset.
"""

from __future__ import annotations

import argparse
import calendar
import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr


REQUIRED_COLUMNS = {
    "month",
    "town",
    "flat_type",
    "floor_area_sqm",
    "flat_model",
    "storey_midpoint",
    "remaining_lease_years_numeric",
    "price_per_sqm",
    "resale_price",
}

MIN_HISTORY = 500
MIN_PERIOD = 50
MATERIAL_GROWTH = 0.05
EMERGING_GROWTH = 0.10


def rate_ratio_interval(current: float, base: float) -> tuple[float, float]:
    """Approximate 95% interval for equal-exposure Poisson count growth."""
    if current <= 0 or base <= 0:
        return math.nan, math.nan
    log_ratio = math.log(current / base)
    standard_error = math.sqrt((1.0 / current) + (1.0 / base))
    lower = math.exp(log_ratio - 1.96 * standard_error) - 1.0
    upper = math.exp(log_ratio + 1.96 * standard_error) - 1.0
    return lower, upper


def model_adjusted_growth(segment: pd.DataFrame, base_year: int, current_year: int) -> dict[str, float | str]:
    """Estimate a period effect on log price/sqm while controlling for sale mix."""
    work = segment.copy()
    work["current_period"] = (work["year"] == current_year).astype(int)
    work["month_number"] = work["month"].dt.month.astype(str)
    work["log_price_per_sqm"] = np.log(work["price_per_sqm"])
    model_counts = work["flat_model"].value_counts()
    work["flat_model_grouped"] = work["flat_model"].where(
        work["flat_model"].map(model_counts).ge(10),
        "Other",
    )

    try:
        result = smf.ols(
            "log_price_per_sqm ~ current_period + floor_area_sqm + "
            "remaining_lease_years_numeric + storey_midpoint + C(flat_model_grouped) + C(month_number)",
            data=work,
        ).fit()
        # HC3 is undefined for observations with unit leverage (e.g. singleton
        # categories). Mark that model unavailable instead of emitting infinities.
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            result = result.get_robustcov_results(cov_type="HC3", use_t=False)
        period_index = result.model.exog_names.index("current_period")
        coefficient = float(result.params[period_index])
        low, high = (float(value) for value in result.conf_int()[period_index])
        if not np.isfinite([coefficient, low, high]).all():
            raise ValueError("Non-finite adjusted price estimate")
        n = int(result.nobs)
        adjusted_r_squared = float(result.rsquared_adj)
        p_value = float(result.pvalues[period_index])
        return {
            "adjusted_price_model_status": "ok",
            "adjusted_price_growth": math.exp(coefficient) - 1.0,
            "adjusted_price_growth_ci_low": math.exp(low) - 1.0,
            "adjusted_price_growth_ci_high": math.exp(high) - 1.0,
            "adjusted_price_p_value": p_value,
            "adjusted_price_model_n": n,
            "adjusted_price_model_r2": adjusted_r_squared,
        }
    except (ValueError, RuntimeWarning, np.linalg.LinAlgError, OverflowError) as error:
        return {
            "adjusted_price_model_status": f"unavailable: {error}",
            "adjusted_price_growth": math.nan,
            "adjusted_price_growth_ci_low": math.nan,
            "adjusted_price_growth_ci_high": math.nan,
            "adjusted_price_p_value": math.nan,
            "adjusted_price_model_n": len(work),
            "adjusted_price_model_r2": math.nan,
        }


def composition_shift(segment: pd.DataFrame, base_year: int, current_year: int) -> tuple[bool, str]:
    base = segment[segment["year"] == base_year]
    current = segment[segment["year"] == current_year]
    reasons: list[str] = []

    lease_change = current["remaining_lease_years_numeric"].median() - base["remaining_lease_years_numeric"].median()
    storey_change = current["storey_midpoint"].median() - base["storey_midpoint"].median()
    area_change = current["floor_area_sqm"].median() - base["floor_area_sqm"].median()

    if abs(lease_change) >= 3:
        reasons.append(f"median lease {lease_change:+.1f}y")
    if abs(storey_change) >= 3:
        reasons.append(f"median storey {storey_change:+.1f}")
    if abs(area_change) >= 5:
        reasons.append(f"median area {area_change:+.1f} sqm")

    base_mix = base["flat_model"].value_counts(normalize=True)
    current_mix = current["flat_model"].value_counts(normalize=True)
    model_share_change = float(current_mix.subtract(base_mix, fill_value=0).abs().max())
    if model_share_change >= 0.15:
        reasons.append(f"flat-model share shift {model_share_change:.0%}")

    return bool(reasons), "; ".join(reasons)


def validate_period_coverage(df: pd.DataFrame, years: tuple[int, ...], months: int) -> None:
    for year in years:
        present = set(df.loc[df["year"].eq(year), "month"].dt.month)
        if not set(range(1, months + 1)).issubset(present):
            raise ValueError(f"Incomplete January-{calendar.month_name[months]} coverage for {year}")


def build_segment_screen(
    df: pd.DataFrame,
    base_year: int,
    current_year: int,
    months: int,
) -> pd.DataFrame:
    if not 1 <= months <= 12 or current_year <= base_year:
        raise ValueError("Use 1-12 months and a current year after the base year")
    validate_period_coverage(df, (base_year, current_year), months)
    comparison = df[
        df["year"].isin([base_year, current_year]) & (df["month"].dt.month <= months)
    ].copy()
    history_cutoff = pd.Timestamp(base_year, months, 1)
    history = df[df["month"] <= history_cutoff]

    history_counts = history.groupby(["town", "flat_type"]).size().rename("history_transactions")
    count_table = (
        comparison.groupby(["town", "flat_type", "year"])
        .size()
        .unstack("year", fill_value=0)
        .reindex(columns=[base_year, current_year], fill_value=0)
        .rename(columns={base_year: "transactions_base", current_year: "transactions_current"})
    )
    value_table = comparison.groupby(["town", "flat_type", "year"])["resale_price"].sum().unstack("year")
    price_table = comparison.groupby(["town", "flat_type", "year"])["price_per_sqm"].median().unstack("year")

    output = count_table.join(history_counts, how="left").reset_index()
    output["history_transactions"] = output["history_transactions"].fillna(0).astype(int)
    output["segment"] = output["town"].str.title() + " × " + output["flat_type"].str.title()
    output["transaction_value_current"] = [
        value_table.loc[(row.town, row.flat_type), current_year] if row.transactions_current else 0 for row in output.itertuples()
    ]
    output["median_price_per_sqm_base"] = [
        price_table.loc[(row.town, row.flat_type), base_year] for row in output.itertuples()
    ]
    output["median_price_per_sqm_current"] = [
        price_table.loc[(row.town, row.flat_type), current_year] for row in output.itertuples()
    ]
    output["transaction_growth"] = output["transactions_current"] / output["transactions_base"].replace(0, np.nan) - 1.0
    output["unadjusted_price_growth"] = (
        output["median_price_per_sqm_current"] / output["median_price_per_sqm_base"] - 1.0
    )

    intervals = [
        rate_ratio_interval(row.transactions_current, row.transactions_base) for row in output.itertuples()
    ]
    output[["transaction_growth_ci_low", "transaction_growth_ci_high"]] = pd.DataFrame(
        intervals, index=output.index
    )
    output["eligible"] = (
        (output["history_transactions"] >= MIN_HISTORY)
        & (output["transactions_base"] >= MIN_PERIOD)
        & (output["transactions_current"] >= MIN_PERIOD)
    )

    model_rows: list[dict[str, float | str | bool]] = []
    for row in output.itertuples():
        segment = comparison[(comparison["town"] == row.town) & (comparison["flat_type"] == row.flat_type)]
        if row.eligible:
            model_result = model_adjusted_growth(segment, base_year, current_year)
            shifted, shift_reason = composition_shift(segment, base_year, current_year)
        else:
            model_result = {
                "adjusted_price_model_status": "insufficient sample",
                "adjusted_price_growth": math.nan,
                "adjusted_price_growth_ci_low": math.nan,
                "adjusted_price_growth_ci_high": math.nan,
                "adjusted_price_p_value": math.nan,
                "adjusted_price_model_n": len(segment),
                "adjusted_price_model_r2": math.nan,
            }
            shifted, shift_reason = False, ""
        model_result.update({"composition_shift_flag": shifted, "composition_shift_reason": shift_reason})
        model_rows.append(model_result)
    output = pd.concat([output, pd.DataFrame(model_rows)], axis=1)

    # A multi-year same-month trend keeps seasonality comparable.
    start_year = current_year - 3
    recent = df[
        df["year"].isin([start_year, current_year]) & (df["month"].dt.month <= months)
    ]
    recent_counts = recent.groupby(["town", "flat_type", "year"]).size().unstack("year")
    cagr_map = {}
    for idx, values in recent_counts.iterrows():
        start = values.get(start_year, np.nan)
        end = values.get(current_year, np.nan)
        cagr_map[idx] = (end / start) ** (1 / 3) - 1 if start > 0 and end > 0 else math.nan
    output["three_year_transaction_cagr"] = [cagr_map.get((r.town, r.flat_type), math.nan) for r in output.itertuples()]

    eligible = output[output["eligible"]]
    size_cutoff = float(eligible["transactions_current"].median())
    output["large_segment"] = output["transactions_current"] >= size_cutoff
    output["material_volume_growth"] = output["transaction_growth"] >= MATERIAL_GROWTH
    output["volume_growth_supported"] = output["transaction_growth_ci_low"] > 0
    output["adjusted_price_nonnegative"] = output["adjusted_price_growth"] >= 0

    def classify(row: pd.Series) -> str:
        if not row["eligible"]:
            return "Insufficient sample"
        if (
            row["large_segment"]
            and row["material_volume_growth"]
            and row["volume_growth_supported"]
            and row["adjusted_price_nonnegative"]
        ):
            return "Priority"
        if (
            (not row["large_segment"])
            and row["transaction_growth"] >= EMERGING_GROWTH
            and row["volume_growth_supported"]
            and row["adjusted_price_nonnegative"]
        ):
            return "Emerging"
        if row["material_volume_growth"]:
            return "Watchlist"
        if row["large_segment"] and row["transaction_growth"] > -MATERIAL_GROWTH:
            return "Core stable"
        if row["large_segment"]:
            return "Large declining"
        return "Lower priority"

    output["category"] = output.apply(classify, axis=1)
    output["size_cutoff_transactions"] = size_cutoff
    output["comparison"] = f"Jan-{calendar.month_abbr[months]} {current_year} vs Jan-{calendar.month_abbr[months]} {base_year}"
    output["period_months"] = months

    category_order = {
        "Priority": 0,
        "Emerging": 1,
        "Watchlist": 2,
        "Core stable": 3,
        "Large declining": 4,
        "Lower priority": 5,
        "Insufficient sample": 6,
    }
    output["category_order"] = output["category"].map(category_order)
    output = output.sort_values(
        ["category_order", "transactions_current", "transaction_growth"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    return output


def backtest(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    validate_period_coverage(df, (2023, 2024, 2025), 8)
    signal = build_segment_screen(df, base_year=2023, current_year=2024, months=8)
    outcome = (
        df[df["year"].isin([2024, 2025]) & (df["month"].dt.month <= 8)]
        .groupby(["town", "flat_type", "year"])
        .size()
        .unstack("year", fill_value=0)
        .reindex(columns=[2024, 2025], fill_value=0)
    )
    outcome["next_year_growth"] = outcome[2025] / outcome[2024].replace(0, np.nan) - 1.0
    merged = signal.merge(outcome[["next_year_growth"]].reset_index(), on=["town", "flat_type"], how="left")
    tested = merged[merged["eligible"] & np.isfinite(merged["next_year_growth"])].copy()
    priority = tested[tested["category"] == "Priority"]
    non_priority = tested[tested["category"] != "Priority"]
    if len(tested) > 2 and tested["transaction_growth"].nunique() > 1 and tested["next_year_growth"].nunique() > 1:
        correlation, correlation_p = spearmanr(tested["transaction_growth"], tested["next_year_growth"])
    else:
        correlation, correlation_p = math.nan, math.nan
    summary: dict[str, float | int | str] = {
        "eligible_segments": int(len(tested)),
        "priority_segments": int(len(priority)),
        "priority_median_next_year_growth": float(priority["next_year_growth"].median()) if len(priority) else math.nan,
        "non_priority_median_next_year_growth": float(non_priority["next_year_growth"].median()) if len(non_priority) else math.nan,
        "priority_positive_next_year_share": float((priority["next_year_growth"] > 0).mean()) if len(priority) else math.nan,
        "all_positive_next_year_share": float((tested["next_year_growth"] > 0).mean()),
        "signal_outcome_spearman": float(correlation),
        "signal_outcome_spearman_p_value": float(correlation_p),
    }
    if len(priority) and summary["priority_median_next_year_growth"] > summary["non_priority_median_next_year_growth"]:
        conclusion = "The stricter signal showed some forward separation in this single backtest."
    else:
        conclusion = "The stricter signal did not show forward separation in this single backtest."
    summary["conclusion"] = conclusion
    return tested, summary


def pct(value: float) -> str:
    return "n.a." if not np.isfinite(value) else f"{value:.1%}"


def write_report(
    output_path: Path,
    df: pd.DataFrame,
    screen: pd.DataFrame,
    backtest_summary: dict[str, float | int | str],
) -> None:
    eligible = screen[screen["eligible"]]
    priorities = screen[screen["category"] == "Priority"]
    emerging = screen[screen["category"] == "Emerging"]
    total_base = int(df[(df["year"] == 2025) & (df["month"].dt.month <= 8)].shape[0])
    total_current = int(df[(df["year"] == 2026) & (df["month"].dt.month <= 8)].shape[0])
    total_growth = total_current / total_base - 1

    lines = [
        "# Singapore HDB Resale Market — Final Opportunity Findings",
        "",
        "This is the final screen for the fixed January 2017–August 2026 snapshot. The earlier [exploratory report](../../reports/exploratory_findings.md) uses a different period and classification method.",
        "",
        "## Executive result",
        "",
        f"The market recorded {total_current:,} transactions in January-August 2026, {pct(total_growth)} versus the same months of 2025.",
        f"The stricter screen retained {len(eligible)} adequately sampled segments and classified {len(priorities)} as Priority and {len(emerging)} as Emerging.",
        "",
        f"Priority requires at least {screen['size_cutoff_transactions'].iloc[0]:g} current-period transactions (the eligible-segment median), at least 5% transaction growth, a 95% count-growth interval above zero, and non-negative composition-adjusted price growth. Emerging applies below the same size threshold and requires at least 10% transaction growth, with the same uncertainty and adjusted-price criteria.",
        "",
        "## Current shortlist",
        "",
        "| Category | Segment | 2026 YTD transactions | Volume growth | 95% interval | Adjusted price growth | 95% interval | Three-year volume CAGR |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in screen[screen["category"].isin(["Priority", "Emerging"])].itertuples():
        lines.append(
            f"| {row.category} | {row.segment} | {int(row.transactions_current):,} | {pct(row.transaction_growth)} | "
            f"{pct(row.transaction_growth_ci_low)} to {pct(row.transaction_growth_ci_high)} | "
            f"{pct(row.adjusted_price_growth)} | {pct(row.adjusted_price_growth_ci_low)} to "
            f"{pct(row.adjusted_price_growth_ci_high)} | {pct(row.three_year_transaction_cagr)} |"
        )

    lines.extend([
        "",
        "## What changed from the original method",
        "",
        "- The comparison is January-August 2026 versus January-August 2025, using the latest matched-month window in the fixed snapshot.",
        f"- Eligibility uses at least {MIN_HISTORY} transactions known by August 2025 and at least {MIN_PERIOD} transactions in each comparison period.",
        f"- Material volume growth is at least {MATERIAL_GROWTH:.0%}; statistical support requires the approximate 95% rate-ratio interval to stay above zero.",
        "- Adjusted price growth comes from a segment-level log-price-per-sqm regression controlling for floor area, remaining lease, storey, flat model and calendar month, with HC3 robust standard errors.",
        "- Adjusted-price models with undefined robust uncertainty are marked unavailable in the CSV and cannot qualify for Priority or Emerging.",
        "- Count intervals are per-segment approximations; they do not correct for testing multiple segments. A non-negative adjusted price point estimate does not establish statistically significant price growth.",
        "- Composition flags identify material shifts in median lease, storey, area or flat-model shares.",
        "- Historical eligibility stops before the current period, preventing future-data leakage.",
        "",
        "## Historical validation",
        "",
        f"The backtest formed signals using January-August 2024 versus the same months of 2023 and measured what happened in January-August 2025. It covered {backtest_summary['eligible_segments']} eligible segments, including {backtest_summary['priority_segments']} Priority segments.",
        "",
        f"- Median subsequent volume growth for Priority: {pct(float(backtest_summary['priority_median_next_year_growth']))}",
        f"- Median subsequent volume growth for other eligible segments: {pct(float(backtest_summary['non_priority_median_next_year_growth']))}",
        f"- Priority segments with positive subsequent growth: {pct(float(backtest_summary['priority_positive_next_year_share']))}",
        f"- All eligible segments with positive subsequent growth: {pct(float(backtest_summary['all_positive_next_year_share']))}",
        f"- Spearman correlation between signal-year and subsequent growth: {float(backtest_summary['signal_outcome_spearman']):.2f} (p={float(backtest_summary['signal_outcome_spearman_p_value']):.3f})",
        "",
        str(backtest_summary["conclusion"]),
        "",
        "The Spearman p-value uses SciPy's asymptotic calculation. Adjacent growth rates share the middle year, which can itself induce negative correlation; this result does not establish a reversal mechanism. A single backtest is evidence, not proof. The category remains a commercial research screen rather than an investment-return forecast.",
        "",
        "## Remaining data gap",
        "",
        "The transaction file cannot distinguish buyer demand from flats available for sale. Listing inventory, days on market, asking-to-sale discount, MRT distance and amenity data are not present. Those variables should be added before interpreting transaction growth as demand or estimating lead-generation potential.",
        "",
        "## Data-quality checks",
        "",
        f"- Source rows: {len(df):,}",
        f"- Coverage: {df['month'].min():%B %Y} to {df['month'].max():%B %Y}",
        f"- Missing values in required analytical columns: {int(df[list(REQUIRED_COLUMNS)].isna().sum().sum()):,}",
        f"- Exact duplicate rows retained in source: {int(df.duplicated().sum()):,}",
        "- Identical published rows are retained because there is no unique transaction identifier to establish that they represent duplicate sales.",
        "",
        "Source: Housing & Development Board, [Resale flat prices based on registration date from Jan-2017 onwards](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view), under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence). See [data provenance](../../data/README.md).",
    ])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data" / "processed" / "hdb_resale_clean.csv",
        help="Cleaned transaction CSV (defaults to the project data directory)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "outputs" / "improved_opportunity",
        help="Directory for generated analysis files",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(
            f"Cleaned data not found at {args.input}. Run notebooks/02_data_cleaning.ipynb first "
            "or pass --input."
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input, parse_dates=["month"])
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Required analytical columns contain missing values")
    if (df["price_per_sqm"] <= 0).any() or (df["resale_price"] <= 0).any():
        raise ValueError("Price fields must be positive")

    df["year"] = df["month"].dt.year
    screen = build_segment_screen(df, base_year=2025, current_year=2026, months=8)
    backtest_detail, backtest_summary = backtest(df)

    screen.to_csv(args.output_dir / "segment_screen_2026_ytd.csv", index=False)
    backtest_detail.to_csv(args.output_dir / "backtest_detail.csv", index=False)
    (args.output_dir / "backtest_summary.json").write_text(
        json.dumps(backtest_summary, indent=2), encoding="utf-8"
    )
    write_report(args.output_dir / "findings.md", df, screen, backtest_summary)

    summary = {
        "source_rows": len(df),
        "source_start": df["month"].min().strftime("%Y-%m"),
        "source_end": df["month"].max().strftime("%Y-%m"),
        "eligible_segments": int(screen["eligible"].sum()),
        "category_counts": screen["category"].value_counts().to_dict(),
        "size_cutoff_transactions": int(screen.loc[screen["eligible"], "size_cutoff_transactions"].iloc[0]),
        "backtest": backtest_summary,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
