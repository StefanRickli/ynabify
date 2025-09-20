class ParseError(Exception):
    """Exception raised for errors in the parsing process."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Cannot parse {path}")


class LanguageError(Exception):
    """Exception raised for errors in determining the language of a file."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Cannot determine language of {path}")
