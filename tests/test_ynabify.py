import shutil
from pathlib import Path

import pandas as pd
import pytest

from ynabify.ynabify import main

swisscard_xlsx_example_path = Path("tests/data/swisscard_xlsx/example_bill.xlsx").resolve()
ynab_xlsx_example_path = Path("tests/data/ynab_xlsx/example_bill.xlsx").resolve()
raiffeisen_csv_example_path = Path("tests/data/raiffeisen_csv/example_bill.csv").resolve()


@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    return (tmp_path / "outfile.csv").resolve()


class TestYnabify:
    def test_should_show_required_args(self, capsys: pytest.CaptureFixture[str]) -> None:
        args: list[str] = []
        with pytest.raises(SystemExit):
            main(argv=args)
        out, err = capsys.readouterr()
        assert "src" in err

    def test_should_reject_textfile(self, caplog: pytest.LogCaptureFixture) -> None:
        args = ["./tests/data/empty_textfile.txt"]
        with pytest.raises(SystemExit):
            main(argv=args)
        assert "Cannot handle file" in caplog.text

    def test_should_not_raise_on_swisscard_xlsx(self, output_path: Path) -> None:
        args = [str(swisscard_xlsx_example_path), "-d", str(output_path)]
        # Expect no exception
        main(argv=args)

    def test_should_not_raise_on_raiffeisen_csv(self, output_path: Path) -> None:
        args = [str(raiffeisen_csv_example_path), "-d", str(output_path)]
        # Expect no exception
        main(argv=args)

    def test_should_not_raise_on_ynab_xlsx(self, output_path: Path) -> None:
        args = [str(ynab_xlsx_example_path), "-d", str(output_path)]
        # Expect no exception
        main(argv=args)

    def test_should_create_output_file(self, tmp_path: Path) -> None:
        src_path = tmp_path / "example_bill.xlsx"
        shutil.copyfile(swisscard_xlsx_example_path, src_path)
        args = [str(src_path)]
        main(argv=args)
        target_file = src_path.with_name(src_path.stem + "_ynab").with_suffix(".csv")
        assert target_file.exists()

    def test_should_create_output_file_with_custom_destination(self, output_path: Path) -> None:
        args = [str(swisscard_xlsx_example_path), "-d", str(output_path)]
        main(argv=args)
        assert output_path.exists()

    def test_should_produce_valid_csv(self, output_path: Path) -> None:
        args = [str(swisscard_xlsx_example_path), "-d", str(output_path)]
        main(argv=args)
        df = pd.read_csv(output_path, header=0)
        required_cols = ["Date", "Payee", "Memo", "Outflow", "Inflow"]
        for r in required_cols:
            assert r in df.columns
        assert "Unnamed" not in "".join(df.columns)

    def test_should_convert_memos_into_payees(self, output_path: Path) -> None:
        args = [
            str(swisscard_xlsx_example_path),
            "--mapping",
            "./tests/data/swisscard_xlsx/mapping_example.xlsx",
            "-d",
            str(output_path),
        ]
        main(argv=args)
        df = pd.read_csv(output_path, header=0)
        assert len(df.index) > 0
        assert pd.notna(df["Payee"]).all()

    @pytest.mark.xfail
    def test_manual_path(self) -> None:
        args = [r"foo", "--mapping", "./mapping.xlsx", "-d", "output_path"]
        main(argv=args)
