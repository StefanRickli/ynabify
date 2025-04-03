from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from ynabify.exceptions import ParseError
from ynabify.parser.raiffeisen_csv import RaiffeisenCsv


class TestCanParse:
    def test_should_reject_nonexisting_path(self) -> None:
        assert not RaiffeisenCsv.can_parse(Path("foobar1234.xlsx"))

    def test_should_reject_non_csv_extension(self) -> None:
        assert not RaiffeisenCsv.can_parse(Path("tests/data/raiffeisen_csv/foreign_file_extension.txt"))

    def test_should_reject_missing_columns(self) -> None:
        assert not RaiffeisenCsv.can_parse(Path("tests/data/raiffeisen_csv/empty_csv.csv"))


example_path = Path("tests/data/raiffeisen_csv/example_bill.csv").resolve()


class TestGetTransactions:
    def test_should_instantiate(self) -> None:
        # Expect no exception
        RaiffeisenCsv(example_path)

    def test_should_reject_unparseable_file(self) -> None:
        with pytest.raises(ParseError):
            RaiffeisenCsv(Path("tests/data/raiffeisen_csv/foreign_file_extension.txt"))

    def test_should_load_file_with_correct_columns(self) -> None:
        cut = RaiffeisenCsv(example_path)
        assert all(col in cut._df.columns for col in ("IBAN", "Booked At", "Text", "Credit/Debit Amount"))  # noqa: SLF001

    def test_should_return_DataFrame_with_sensible_columns(self) -> None:  # noqa: N802
        cut = RaiffeisenCsv(example_path)
        df = cut.get_transactions()["CH1234567890123456789"]
        assert "Date" in df.columns
        assert "Payee" in df.columns
        assert "Memo" in df.columns
        assert "Inflow" in df.columns
        assert "Outflow" in df.columns

    def test_should_return_empty_DataFrame(self) -> None:  # noqa: N802
        cut = RaiffeisenCsv(Path("tests/data/raiffeisen_csv/empty_bill.csv"))
        df = cut.get_transactions()["main"]
        assert df.empty
        assert "Date" in df.columns
        assert "Payee" in df.columns
        assert "Memo" in df.columns
        assert "Inflow" in df.columns
        assert "Outflow" in df.columns

    def test_should_return_n_transactions(self) -> None:
        transactions = RaiffeisenCsv(example_path).get_transactions()
        assert len(transactions["CH1234567890123456789"]) == 4
        assert len(transactions["CH1234567890123456788"]) == 1

    def test_should_return_datetime_in_date_column(self) -> None:
        cut = RaiffeisenCsv(example_path)
        df = cut.get_transactions()["CH1234567890123456789"]
        assert not df.empty
        assert all(isinstance(row["Date"], pd.Timestamp) for _, row in df.iterrows())

    def test_should_return_nonempty_memos(self) -> None:
        cut = RaiffeisenCsv(example_path)
        df = cut.get_transactions()["CH1234567890123456789"]
        assert not df.empty
        assert all(df["Memo"])

    def test_should_return_decimals_in_inflow_outflow(self) -> None:
        cut = RaiffeisenCsv(example_path)
        df = cut.get_transactions()["CH1234567890123456789"]
        assert not df.empty
        assert all(isinstance(x, Decimal) for x in df["Inflow"])
        assert all(isinstance(x, Decimal) for x in df["Outflow"])

    def test_should_return_both_positive_inflow_and_outflow(self) -> None:
        cut = RaiffeisenCsv(example_path)
        df = cut.get_transactions()["CH1234567890123456789"]
        assert not df.empty
        assert all(df["Inflow"] >= 0)
        assert all(df["Outflow"] >= 0)
