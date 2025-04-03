from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class ParserBase(ABC):
    @staticmethod
    @abstractmethod
    def can_parse(path: Path) -> bool:
        pass

    @abstractmethod
    def __init__(self, path: str) -> None:
        pass

    @abstractmethod
    def get_transactions(self) -> dict[str, pd.DataFrame]:
        pass
