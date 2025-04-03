from abc import ABC, abstractmethod

import pandas as pd


class ParserBase(ABC):
    @staticmethod
    @abstractmethod
    def can_parse(path: str) -> bool:
        pass

    @abstractmethod
    def __init__(self, path: str) -> None:
        pass

    @abstractmethod
    def get_transactions(self) -> dict[str, pd.DataFrame]:
        pass
