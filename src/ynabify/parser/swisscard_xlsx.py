import warnings
from decimal import Decimal
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from ynabify.exceptions import ParseError
from ynabify.parser_base import ParserBase

pd.set_option("display.max_columns", 10)
pd.set_option("display.max_colwidth", 30)


class SwisscardXlsx(ParserBase):
    @staticmethod
    def can_parse(path: Path) -> bool:
        if path.suffix.lower() != ".xlsx":
            return False
        if not path.exists():
            return False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(path)
        # Reject if we can't find these columns:
        # Transaktionsdatum, Beschreibung, Betrag, Status
        return all(col in df.columns for col in ("Transaktionsdatum", "Beschreibung", "Betrag", "Status"))

    def __init__(self, path: Path) -> None:
        self.path = path
        if not SwisscardXlsx.can_parse(self.path):
            raise ParseError(str(self.path))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._df = pd.read_excel(self.path)

    def get_transactions(self) -> dict[str, pd.DataFrame]:
        if self._df.empty:
            return {"main": pd.DataFrame(columns=("Date", "Payee", "Memo", "Inflow", "Outflow"))}

        transactions = []
        for _, row in tqdm(self._df.iterrows(), desc="Processing", total=len(self._df)):
            if row["Status"] != "Gebucht":
                continue
            transactions.append(
                {
                    "Date": pd.to_datetime(row["Transaktionsdatum"], format="%d.%m.%Y"),
                    "Payee": "",
                    "Memo": row["Beschreibung"],
                    "Inflow": Decimal(-row["Betrag"]) if row["Betrag"] < 0 else Decimal(0),
                    "Outflow": Decimal(row["Betrag"]) if row["Betrag"] > 0 else Decimal(0),
                },
            )

        if not transactions:
            return {"main": pd.DataFrame(columns=("Date", "Payee", "Memo", "Inflow", "Outflow"))}

        return {"main": pd.DataFrame(transactions)}


if __name__ == "__main__":
    pass
