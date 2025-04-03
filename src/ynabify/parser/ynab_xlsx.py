import warnings
from decimal import Decimal
from pathlib import Path

import pandas as pd

from ynabify.exceptions import ParseError
from ynabify.parser_base import ParserBase

pd.set_option("display.max_columns", 10)
pd.set_option("display.max_colwidth", 30)


class YnabXlsx(ParserBase):
    @staticmethod
    def can_parse(path: Path) -> bool:
        if path.suffix.lower() != ".xlsx":
            return False
        if not path.exists():
            return False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(path)
        return all(col in df.columns for col in ("Date", "Memo", "Outflow", "Inflow"))

    def __init__(self, path: Path) -> None:
        self.path = path
        if not YnabXlsx.can_parse(self.path):
            raise ParseError(str(self.path))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._df = pd.read_excel(self.path)

    def get_transactions(self) -> dict[str, pd.DataFrame]:
        # if self._df.empty:
        #     return {'main': pd.DataFrame(columns=('Date', 'Payee', 'Memo', 'Inflow', 'Outflow'))}

        transactions = [
            {
                "Date": pd.to_datetime(row["Date"], format="%d.%m.%Y"),
                "Payee": "",
                "Memo": row["Memo"],
                "Inflow": Decimal(row["Inflow"]) if not pd.isna(row["Inflow"]) else Decimal(0),
                "Outflow": Decimal(row["Outflow"]) if not pd.isna(row["Outflow"]) else Decimal(0),
            }
            for _, row in self._df.iterrows()
        ]

        if not transactions:
            return {"main": pd.DataFrame(columns=("Date", "Payee", "Memo", "Inflow", "Outflow"))}

        return {"main": pd.DataFrame(transactions)}


if __name__ == "__main__":
    pass
