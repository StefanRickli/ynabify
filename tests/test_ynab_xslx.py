from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from ynabify.exceptions import ParseError
from ynabify.parser.ynab_xlsx import YnabXlsx


class TestCanParse:
    def test_should_reject_nonexisting_path(self) -> None:
        assert YnabXlsx.can_parse(Path("foobar1234.xlsx")) is False

    def test_should_reject_non_xlsx_extension(self) -> None:
        assert YnabXlsx.can_parse(Path("tests/data/ynab_xlsx/foreign_file_extension.txt")) is False

    def test_should_reject_missing_columns(self) -> None:
        assert YnabXlsx.can_parse(Path("tests/data/ynab_xlsx/empty_excel.xlsx")) is False


example_path = Path("tests/data/ynab_xlsx/example_bill.xlsx").resolve()


class TestGetTransactions:
    def test_should_instantiate(self) -> None:
        # Expect no exception
        YnabXlsx(example_path)

    def test_should_reject_unparseable_file(self) -> None:
        with pytest.raises(ParseError):
            YnabXlsx(Path("tests/data/ynab_xlsx/foreign_file_extension.txt"))

    def test_should_load_file_with_correct_columns(self) -> None:
        cut = YnabXlsx(example_path)
        assert all(col in cut._df.columns for col in ("Date", "Memo", "Outflow", "Inflow"))  # noqa: SLF001

    def test_should_return_DataFrame_with_sensible_columns(self) -> None:  # noqa: N802
        cut = YnabXlsx(example_path)
        df = cut.get_transactions()["main"]
        assert "Date" in df.columns
        assert "Payee" in df.columns
        assert "Memo" in df.columns
        assert "Inflow" in df.columns
        assert "Outflow" in df.columns

    def test_should_return_empty_DataFrame(self) -> None:  # noqa: N802
        cut = YnabXlsx(Path("tests/data/ynab_xlsx/empty_bill.xlsx"))
        df = cut.get_transactions()["main"]
        assert df.empty
        assert "Date" in df.columns
        assert "Payee" in df.columns
        assert "Memo" in df.columns
        assert "Inflow" in df.columns
        assert "Outflow" in df.columns

    def test_should_return_5_transactions(self) -> None:
        cut = YnabXlsx(example_path)
        df = cut.get_transactions()["main"]
        assert len(df) == 5

    def test_should_return_datetime_in_date_column(self) -> None:
        cut = YnabXlsx(example_path)
        df = cut.get_transactions()["main"]
        assert isinstance(df.iloc[0]["Date"], pd.Timestamp)

    def test_should_return_nonempty_memos(self) -> None:
        cut = YnabXlsx(example_path)
        df = cut.get_transactions()["main"]
        assert all(df["Memo"])

    def test_should_return_decimals_in_inflow_outflow(self) -> None:
        cut = YnabXlsx(example_path)
        df = cut.get_transactions()["main"]
        assert all(isinstance(x, Decimal) for x in df["Inflow"])
        assert all(isinstance(x, Decimal) for x in df["Outflow"])

    def test_should_return_both_positive_inflow_and_outflow(self) -> None:
        cut = YnabXlsx(example_path)
        df = cut.get_transactions()["main"]
        assert all(df["Inflow"] >= 0)
        assert all(df["Outflow"] >= 0)
