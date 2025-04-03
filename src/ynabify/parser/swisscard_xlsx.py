from pathlib import Path

import pandas as pd

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
        df = pd.read_excel(path)
        # Reject if we can't find these columns:
        # Transaktionsdatum, Beschreibung, Betrag, Status
        return all(col in df.columns for col in ("Transaktionsdatum", "Beschreibung", "Betrag", "Status"))

    def __init__(self, path: Path) -> None:
        self.path = path
        if not SwisscardXlsx.can_parse(self.path):
            raise ParseError(str(self.path))
        self._df = pd.read_excel(self.path)

    def get_transactions(self) -> dict[str, pd.DataFrame]:
        if self._df.empty:
            return {"main": pd.DataFrame(columns=("Date", "Payee", "Memo", "Inflow", "Outflow"))}

        transactions = []
        for _, row in self._df.iterrows():
            if row["Status"] != "Gebucht":
                continue
            transactions.append(
                {
                    "Date": pd.to_datetime(row["Transaktionsdatum"], format="%d.%m.%Y"),
                    "Payee": "",
                    "Memo": row["Beschreibung"],
                    "Inflow": float(-row["Betrag"]) if row["Betrag"] < 0 else 0.0,
                    "Outflow": float(row["Betrag"]) if row["Betrag"] > 0 else 0.0,
                },
            )

        if not transactions:
            return {"main": pd.DataFrame(columns=("Date", "Payee", "Memo", "Inflow", "Outflow"))}

        return {"main": pd.DataFrame(transactions)}


if __name__ == "__main__":
    pass
