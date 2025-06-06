import argparse
import logging
import operator
import shutil
import time
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ynabify.parser_base import ParserBase

from ynabify.parser.raiffeisen_csv import RaiffeisenCsv
from ynabify.parser.swisscard_xlsx import SwisscardXlsx
from ynabify.parser.ynab_xlsx import YnabXlsx

logger = logging.getLogger(__name__)


def replace_text(string: str, text_from: list[str], text_to: list[str]) -> str:
    """If string contains one or more substrings from text_from, return the
    corresponding element from text_to where the matching substring is the longest.
    """
    candidates: list[tuple[int, str]] = []  # noqa: FURB138

    for i, search_text in enumerate(text_from):
        if string.lower().find(search_text.lower()) != -1:
            candidates.append((len(search_text), text_to[i]))

    if not candidates:
        return ""
    return sorted(candidates, reverse=True, key=operator.itemgetter(0))[0][1]


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.DEBUG)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("src")
    arg_parser.add_argument("-m", "--mapping", nargs="?", default="./mapping.xlsx")
    arg_parser.add_argument("-d", "--destination", nargs="?", default=None)
    args = arg_parser.parse_args() if argv is None else arg_parser.parse_args(argv)
    src_path = Path(args.src).resolve()

    file_parser: ParserBase | None = None
    if SwisscardXlsx.can_parse(src_path):
        file_parser = SwisscardXlsx(src_path)
    elif RaiffeisenCsv.can_parse(src_path):
        file_parser = RaiffeisenCsv(src_path)
    elif YnabXlsx.can_parse(src_path):
        file_parser = YnabXlsx(src_path)
    else:
        logger.error(f"Cannot handle file: {src_path}")
        raise SystemExit(1)

    if not Path(args.mapping).exists():
        shutil.copyfile("./tests/data/mapping_example.xlsx", args.mapping)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        replacements_raw = pd.read_excel(args.mapping, header=0)
    text_from = list(replacements_raw["from"])
    text_to = list(replacements_raw["to"])

    if args.destination is None:
        out_file_base = src_path.with_stem(Path(src_path).stem + "_ynab")
    else:
        out_file_base = Path(args.destination)

    dfs = file_parser.get_transactions()
    for account, df in dfs.items():
        name = replace_text(account, text_from, text_to) or account
        if len(dfs) > 1:
            out_file_path = str(out_file_base.with_name(out_file_base.stem + f"_{name}").with_suffix(".csv"))
        else:
            out_file_path = str(out_file_base.with_suffix(".csv"))

        df = df.set_index("Date")  # noqa: PLW2901
        df["Payee"] = df.apply(lambda row: replace_text(row["Memo"], text_from, text_to), axis=1)

        n_tries = 60
        while n_tries:
            try:
                n_tries -= 1
                df.to_csv(out_file_path, sep=",", encoding="utf_8_sig")
                logger.info(f"Wrote to {out_file_path}")
                break
            except PermissionError:
                logger.error(f"Cannot write to {out_file_path}. Please close the file.")  # noqa: TRY400
                time.sleep(1)


if __name__ == "__main__":
    main()
