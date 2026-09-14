from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from hdb_analysis.opportunity import (  # noqa: E402
    REQUIRED_COLUMNS,
    backtest,
    build_segment_screen,
    composition_shift,
)


DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hdb_resale_clean.csv"


class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.df = pd.read_csv(DATA_PATH, parse_dates=["month"])
        cls.df["year"] = cls.df["month"].dt.year

    def test_required_data_is_valid(self) -> None:
        self.assertTrue(REQUIRED_COLUMNS.issubset(self.df.columns))
        self.assertEqual(int(self.df[list(REQUIRED_COLUMNS)].isna().sum().sum()), 0)
        self.assertTrue(np.isfinite(self.df["price_per_sqm"]).all())
        self.assertTrue(self.df["price_per_sqm"].gt(0).all())
        self.assertTrue(self.df["resale_price"].gt(0).all())

    def test_current_screen_reconciles_to_source(self) -> None:
        screen = build_segment_screen(self.df, base_year=2025, current_year=2026, months=8)
        expected_2025 = len(self.df[(self.df["year"] == 2025) & (self.df["month"].dt.month <= 8)])
        expected_2026 = len(self.df[(self.df["year"] == 2026) & (self.df["month"].dt.month <= 8)])
        self.assertEqual(int(screen["transactions_base"].sum()), expected_2025)
        self.assertEqual(int(screen["transactions_current"].sum()), expected_2026)
        self.assertFalse(screen.duplicated(["town", "flat_type"]).any())
        self.assertEqual(int(screen["eligible"].sum()), 70)

    def test_current_high_confidence_shortlist(self) -> None:
        screen = build_segment_screen(self.df, base_year=2025, current_year=2026, months=8)
        priority = set(screen.loc[screen["category"] == "Priority", "segment"])
        emerging = set(screen.loc[screen["category"] == "Emerging", "segment"])
        self.assertEqual(priority, {"Punggol × 4 Room", "Pasir Ris × 4 Room"})
        self.assertEqual(emerging, {"Pasir Ris × Executive"})

    def test_backtest_has_no_forward_signal_claim(self) -> None:
        _, summary = backtest(self.df)
        self.assertLess(
            summary["priority_median_next_year_growth"],
            summary["non_priority_median_next_year_growth"],
        )
        self.assertLess(summary["signal_outcome_spearman"], 0)

    def test_new_and_disappearing_segments_have_zero_counts(self) -> None:
        sample = self.df.iloc[[0]].copy()
        sample["town"] = "NEW TOWN"
        sample["month"] = pd.Timestamp("2026-01-01")
        sample["year"] = 2026
        old = sample.copy()
        old["town"] = "OLD TOWN"
        old["month"] = pd.Timestamp("2025-01-01")
        old["year"] = 2025
        screen = build_segment_screen(pd.concat([self.df, sample, old]), 2025, 2026, 8).set_index("town")
        self.assertEqual(screen.loc["NEW TOWN", "transactions_base"], 0)
        self.assertEqual(screen.loc["NEW TOWN", "history_transactions"], 0)
        self.assertTrue(pd.isna(screen.loc["NEW TOWN", "transaction_growth"]))
        self.assertEqual(screen.loc["OLD TOWN", "transactions_current"], 0)
        self.assertEqual(screen.loc["OLD TOWN", "transaction_value_current"], 0)
        self.assertEqual(screen.loc["OLD TOWN", "transaction_growth"], -1)

    def test_backtest_rejects_missing_outcome_month(self) -> None:
        sample = self.df.loc[~self.df["month"].eq(pd.Timestamp("2025-08-01"))]
        with self.assertRaisesRegex(ValueError, "Incomplete.*2025"):
            backtest(sample)

    def test_model_share_change_includes_new_and_disappearing_models(self) -> None:
        sample = pd.DataFrame({
            "year": [2025, 2025, 2026, 2026],
            "flat_model": ["A", "A", "B", "B"],
            "remaining_lease_years_numeric": [60] * 4,
            "storey_midpoint": [5] * 4,
            "floor_area_sqm": [90] * 4,
        })
        flagged, reason = composition_shift(sample, 2025, 2026)
        self.assertTrue(flagged)
        self.assertIn("100%", reason)

    def test_missing_comparison_month_is_rejected(self) -> None:
        sample = self.df.loc[~self.df["month"].eq(pd.Timestamp("2026-08-01"))]
        with self.assertRaisesRegex(ValueError, "Incomplete.*2026"):
            build_segment_screen(sample, 2025, 2026, 8)

    def test_period_label_uses_requested_months(self) -> None:
        screen = build_segment_screen(self.df, 2024, 2025, 12)
        self.assertTrue(screen["comparison"].eq("Jan-Dec 2025 vs Jan-Dec 2024").all())

    def test_backtest_retains_segments_with_no_outcome_sales(self) -> None:
        remove = self.df["town"].eq("PUNGGOL") & self.df["flat_type"].eq("4 ROOM") & self.df["year"].eq(2025)
        detail, _ = backtest(self.df.loc[~remove])
        result = detail.loc[detail["town"].eq("PUNGGOL") & detail["flat_type"].eq("4 ROOM")]
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["next_year_growth"], -1)

    def test_sql_does_not_compare_nonconsecutive_years(self) -> None:
        source_df = self.df.loc[self.df["year"].isin([2023, 2025])]
        with duckdb.connect() as connection:
            connection.register("resale_transactions", source_df)
            result = connection.execute((PROJECT_ROOT / "sql/04_growth_analysis.sql").read_text()).fetchdf()
        self.assertTrue(result["transaction_growth_pct"].isna().all())
        self.assertTrue(result["price_growth_pct"].isna().all())

    def test_all_sql_files_execute(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.duckdb"
            connection = duckdb.connect(str(database_path))
            connection.register("source_df", self.df)
            connection.execute("CREATE TABLE resale_transactions AS SELECT * FROM source_df")
            for sql_path in sorted((PROJECT_ROOT / "sql").glob("*.sql")):
                statements = [statement.strip() for statement in sql_path.read_text().split(";") if statement.strip()]
                for statement in statements:
                    connection.execute(statement).fetchall()
            connection.close()


if __name__ == "__main__":
    unittest.main()
