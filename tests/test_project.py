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
