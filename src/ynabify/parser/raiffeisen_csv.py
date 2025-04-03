import warnings
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from ynabify.exceptions import ParseError
from ynabify.parser_base import ParserBase

pd.set_option("display.max_columns", 10)
pd.set_option("display.max_colwidth", 30)


class RaiffeisenCsv(ParserBase):
    @staticmethod
    def can_parse(path: Path) -> bool:
        if path.suffix.lower() != ".csv":
            return False
        if not path.exists():
            return False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                df = pd.read_csv(path, header=0, delimiter=";", encoding="ANSI", dtype=str)
            except pd.errors.EmptyDataError:
                return False
        # Reject if we can't find these columns:
        # IBAN, Booked At, Text, Credit/Debit Amount
        return all(col in df.columns for col in ("IBAN", "Booked At", "Text", "Credit/Debit Amount"))

    def __init__(self, path: Path) -> None:
        self.path = path
        if not RaiffeisenCsv.can_parse(self.path):
            raise ParseError(str(self.path))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._df = pd.read_csv(self.path, header=0, delimiter=";", encoding="ANSI", dtype=str)

    def get_transactions(self) -> dict[str, pd.DataFrame]:
        if self._df.empty:
            return {"main": pd.DataFrame(columns=ParserBase.target_columns)}

        transactions = defaultdict(list)
        new_row: dict[str, Any] = {}
        for _, row in tqdm((self._df.iloc[::-1]).iterrows(), desc="Processing", total=len(self._df)):
            if pd.isna(row["IBAN"]):
                if "Memo" in new_row:
                    new_row["Memo"] = row["Text"] + ", " + new_row.get("Memo", "")
                else:
                    new_row["Memo"] = row["Text"]
            else:
                new_row["Date"] = pd.to_datetime(row["Booked At"][:10], format="%Y-%m-%d")
                new_row["Payee"] = ""
                if "Memo" in new_row:
                    new_row["Memo"] = row["Text"] + ", " + new_row.get("Memo", "")
                else:
                    new_row["Memo"] = row["Text"]
                new_row["Payee"] = new_row["Memo"]  # TODO: use mapping/apply on all rows
                amount = Decimal(row["Credit/Debit Amount"])
                if amount >= 0:
                    new_row["Inflow"] = amount
                    new_row["Outflow"] = Decimal(0)
                else:
                    new_row["Inflow"] = Decimal(0)
                    new_row["Outflow"] = -amount
                transactions[row["IBAN"]].append(new_row)
                new_row = {}

        if not transactions:
            return {"main": pd.DataFrame(columns=ParserBase.target_columns)}

        result = {}
        for iban, transaction_list in transactions.items():
            result[iban] = pd.DataFrame(reversed(transaction_list), columns=ParserBase.target_columns)

        return result


if __name__ == "__main__":
    pass
